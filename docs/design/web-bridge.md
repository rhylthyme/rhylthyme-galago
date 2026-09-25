# Design note: the web live-view bridge (plan phase 10)

Status: **approved 2026-09-25** (decisions recorded at the end).
Plan: [issue #1](https://github.com/rhylthyme/rhylthyme-galago/issues/1), phase 10.

## Goal

An operator can watch and steer an instrument run from rhylthyme.com, from any
device, while the instruments stay on the lab network:

- see a run's steps, tools and failures live;
- answer a failure (retry / skip / abort), pause and resume;
- start a saved program on a lab's workcell (simulated; live only if the lab
  machine allows it).

## What exists today (and why it can't be reused as is)

- The web **live mode** (shared cooking/lab sessions) is browser-only: a
  Supabase Realtime *broadcast* channel `live:<8-char id>`, admission and
  roles enforced in client JavaScript. Any subscriber can broadcast any
  action. That is fine for kitchen timers; it is not fine for moving hardware.
- The CLI already holds a Supabase user session (`rhylthyme login`, refreshable,
  `~/.config/rhylthyme/credentials.json`, mode 0600).
- Run records already upload to `POST /api/mcp/programs/<id>/runs`
  (schema-validated, owner-only RLS on `program_runs`).
- Vercel functions are short-lived (120-180 s max); there is no server-side
  realtime of our own. Supabase (Postgres + RLS + Realtime) is.

## Shape

```
 lab machine                                    Supabase                        browser
 ───────────                                    ────────                        ───────
 galago-serve ×N ◄─gRPC─ rhylthyme bridge ──HTTPS──► bridges        ◄─read── rhylthyme.com
   (LAN only)            (outbound only)    ──HTTPS──► bridge_state  ◄─realtime── "Bridges" panel
                                            ◄─poll──── bridge_commands ◄─insert── run / pause / retry…
```

- **`rhylthyme bridge --workcell lab.json`** (new command in rhylthyme-galago's
  CLI entry, needs `rhylthyme login`). It owns a `ProgramRunner` +
  `InstrumentExecutor` exactly as `rhylthyme run` does; the terminal shows the
  same UI plus every remote command it received. Ctrl-C locally always wins.
- **Outbound only.** The bridge makes HTTPS calls to Supabase (PostgREST, with
  the user's JWT). No inbound port on the lab machine, no tunnel, nothing new
  on Vercel's request path.
- **Server-side authorization by Postgres RLS**, not by the browser: every
  table below is readable and writable only by `auth.uid() = user_id`.

## Data (Supabase, all RLS owner-only)

| Table | Written by | Holds |
|---|---|---|
| `bridges` | bridge (upsert on start, heartbeat every 10 s) | `id`, `user_id`, `name` (workcell name), `last_seen`, `allows_live` (bool, from the bridge's own flag), `tools: [{name, type, status}]` |
| `bridge_state` | bridge (throttled, ≤ 1/s while a run is active) | `bridge_id`, `run_id`, `program_id`, `program_name`, `mode` (simulated/live), `clock`, `steps: [{stepId, name, status, start, end, tool, waitingOn, failure: {code, errorMessage}}]` |
| `bridge_commands` | browser (insert) / bridge (update status) | `id`, `bridge_id`, `user_id`, `kind`, `args`, `created_at`, `status` (pending / accepted / rejected / done), `result` |

Never stored or sent: tool host, port, COM port or any `config` from the
workcell. The bridge builds these rows from an allowlist of fields, and a test
serialises a run with a workcell full of distinctive addresses and asserts none
appear (the same test style as the existing workcell-privacy tests).

The web page subscribes to `bridge_state` and `bridges` with Supabase Realtime
`postgres_changes` (which honours RLS), so it updates live without polling. The
bridge polls `bridge_commands` for `pending` rows every second (one indexed
query; ~86k/day per online bridge, well inside Supabase's free tier; can move to
Realtime later without changing the table).

## The command set (browser → bridge)

The bridge accepts exactly these `kind`s and rejects anything else:

| kind | args | effect |
|---|---|---|
| `start_run` | `program_id` (a saved program the same user owns), `mode` | loads the program from the user's library, validates it against the local workcell (`check_program`), refuses programs with `codeBlock` steps, then runs it. `mode: "live"` is refused unless the bridge was started with `--allow-live`; otherwise simulated. |
| `pause` / `resume` | — | `toggle_pause` |
| `retry` / `skip` | `step_id` | answer a failed step |
| `abort` | `reason` | `abort_program` |

Rules the bridge enforces (it is the final authority, whatever the server lets
through):

- **No arbitrary instrument commands, no code.** The browser can only choose a
  saved program and answer the runner's own prompts; it cannot send a galago
  command or run a `codeBlock` (a remote-started `codeBlock` would be remote code
  execution on the lab machine).
- **Live needs two keys.** The bridge must be started with `--allow-live`
  (a local, physical decision), *and* the browser shows the bridge's pre-flight
  summary (tools, statuses, every command) and asks the user to type `live`.
- **Stale commands expire.** A command older than 30 s when the bridge sees it
  is marked `rejected` ("expired"), so a laptop reconnecting after an hour does
  not replay a `retry` or `start_run`.
- **One run at a time** per bridge; `start_run` while running is rejected.
- **Idempotent by command id**; each is acted on once and its outcome written
  back to `status` / `result`, which the browser shows.
- **Everything is logged locally** in the bridge's terminal and in the run
  record (`context.remoteCommands`), so a lab can audit who did what.

## Web UI

- A **Bridges** panel (lab host first) lists the user's bridges with online
  state (`last_seen` < 30 s), tool list and whether live is allowed.
- **Run on…** a bridge from a saved program.
- The live view reuses the existing player in a read-only mode, fed from
  `bridge_state` (timeline, `[tool]` badges, FAILED highlight), with Pause /
  Resume and, on failure, Retry / Skip / Abort buttons that insert commands.

## Security summary

| Threat | Mitigation |
|---|---|
| Someone else controls my lab | RLS owner-only on all three tables; bridge also checks `user_id` of each command matches its own session |
| Stolen browser session | can at most start *simulated* runs unless the bridge allows live, and live also needs the typed confirmation; the lab can run `--read-only` (watch only) |
| Remote code execution | no `codeBlock` programs, no free-form commands |
| Replayed / delayed commands | 30 s expiry, idempotent ids |
| Leaking the lab network | address fields never serialised; tested |
| Abuse / cost | command inserts limited by an RLS-checked count per user per minute (or an Edge Function later); state writes throttled at the bridge |

## Delivery in slices (each shippable)

1. **Watch only**: `rhylthyme bridge` publishes `bridges` + `bridge_state`;
   the web panel shows runs started locally. (Migrations + RLS + panel.)
2. **Steer**: pause / resume / retry / skip / abort from the web.
3. **Start simulated runs** from the web (`start_run`, simulated only).
4. **Live from the web** behind `--allow-live` + typed confirmation.

## Out of scope for phase 10

Sharing a bridge with other lab members (owner-only in v1; a
`bridge_members` table later), editing workcells remotely, sending individual
instrument commands, bridge auto-update, and mobile push notifications on
failure.

## Decisions (2026-09-25)

1. **Transport**: Supabase tables + owner-only RLS; the browser follows
   `bridge_state` / `bridges` through Realtime row changes; the bridge polls
   `bridge_commands` every second.
2. **Access**: owner only in v1.
3. **Live from the web**: two keys, `--allow-live` on the bridge and a typed
   `live` in the browser after the pre-flight summary.
4. **Package**: `rhylthyme bridge` ships in rhylthyme-galago.
