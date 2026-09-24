# rhylthyme-galago

Run lab instruments from [Rhylthyme](https://rhylthyme.com) programs through
[galago-tools](https://github.com/sciencecorp/galago-tools) (Science Corp's gRPC
drivers for shakers, incubators, plate readers, liquid handlers and robot arms).

A step names a galago command; the runner sends it when the step starts, and the
step ends when the instrument replies:

```json
{
  "stepId": "shake",
  "name": "Shake at 1000 rpm",
  "instrument": {
    "tool": "shaker",
    "toolType": "bioshake",
    "command": "start_shake",
    "params": { "speed": 1000, "acceleration": 5, "duration": 5 }
  },
  "startTrigger": { "type": "afterStep", "stepId": "load-plate" }
}
```

Programs name tools by role. A local **workcell** file says where each tool
listens, and stays on the lab machine:

```json
{
  "id": "simulated-bench",
  "tools": [
    { "name": "shaker", "type": "bioshake", "host": "localhost", "port": 50710,
      "config": { "com_port": "COM3" } }
  ]
}
```

Status: phases 1–8 of the [plan](https://github.com/rhylthyme/rhylthyme-galago/issues/1).
Tools run in galago's simulated mode unless you pass `--live`.

## Quick start (simulated, no hardware)

galago-tools needs Python 3.9; Rhylthyme needs 3.12+. They talk over gRPC, so each
gets its own environment.

```bash
# 1. A simulated Bioshake from galago-tools
python3.9 -m venv .venv-galago
.venv-galago/bin/pip install galago-tools
.venv-galago/bin/galago-serve --tool bioshake --port 50710 &

# 2. Rhylthyme with instrument support
python3 -m venv .venv && source .venv/bin/activate
# --workcell is on rhylthyme-cli-runner main; neither package is on PyPI with it yet
pip install "git+https://github.com/rhylthyme/rhylthyme-cli-runner" ./

# 3. Run the example; press s to start, q to quit
rhylthyme run examples/shake-plate.json --workcell examples/workcell-simulated.json
```

While the command runs, the runner shows the step with a `[shaker]` badge and
"waiting on shaker"; the run record (`rhylthyme runs`) marks it
`endedBy: "instrument"` and keeps every reply, retries included, with any data
the tool returned:

```json
"instrument": {
  "tool": "shaker", "command": "start_shake",
  "replies": [
    { "attempt": 1, "at": 3.0, "code": "DRIVER_ERROR", "errorMessage": "lid open" },
    { "attempt": 2, "at": 41.2, "code": "SUCCESS", "metadata": { "wells": { "A1": 0.41 } } }
  ]
}
```

## A three-tool example

`examples/passage-check.json` fetches a plate from a Liconic incubator, shakes it
on a Bioshake, images it on a Cytation, has someone check the media, and stores
it again, while media is warmed and aliquoted by hand on a second track:

```bash
for t in liconic:50721 bioshake:50722 cytation:50723; do
  .venv-galago/bin/galago-serve --tool ${t%%:*} --port ${t##*:} &
done
rhylthyme run examples/passage-check.json --workcell examples/workcell-cell-culture.json
```

It runs end to end in CI against these simulated servers
(`tests/test_integration.py`).

galago-tools 0.19.9 cannot simulate an Opentrons `run_program` (its simulated
dispatch passes an argument `RunProgram` does not take, so the tool answers
`DRIVER_ERROR`); other Opentrons commands, and real OT-2 runs, are unaffected.

## Real hardware

```bash
rhylthyme run shake.json --workcell lab.json --live
```

`--live` first lists each tool (address and current status, read without
configuring anything) and every instrument command the run will send, then asks
you to type `live`. Only then are the tools configured for real; the run starts
only if every tool reports READY. Scripts pass `--confirm-live` instead of
answering; without a terminal and without that flag, a live run is refused.

Workcell files stay on the lab machine: `rhylthyme publish` and `rhylthyme
analyze` refuse them, programs name tools only by role, and run records hold no
tool addresses.

## Tools are resources

Each tool a program uses is a resource of capacity 1, so two steps never send
commands to the same shaker at once: the second waits until the first is done.
A tool needs no person (actor) while it works, so hand steps and instrument
steps run side by side. To let a tool take more than one command at a time,
declare a constraint with its name:

```json
"resourceConstraints": [{ "task": "shaker", "maxConcurrent": 2, "description": "two-deck shaker" }]
```

## When an instrument fails

Any reply other than SUCCESS (a driver error, a tool that is unreachable or
not ready) and any command that outlives its `timeoutSeconds` marks the step
**FAILED**. Nothing new starts; steps already running on other tools finish. The
runner shows what failed (tool, command, response code, message) and waits:

- `r` resends the command; if it succeeds the program carries on.
- `x` marks the step done by hand (`endedBy: "skipped"`) and releases what depends on it.
- `A` twice aborts the program; the reason is kept in the run record (`context.abortReason`).

Ctrl-C stops the run at once and names any command still in flight.

## Planning with instrument durations

An instrument step may leave out its `duration`: at run time it ends when the
tool replies. For planning, `rhylthyme plan` and `rhylthyme analyze` fill one in
and flag it in `metadata.durationEstimate`:

```text
$ rhylthyme plan shake.json planned.json --workcell lab.json
Estimated instrument durations:
  shake: 5 s (from shaker EstimateDuration)
Makespan (by start triggers and durations): 11 s
```

The number comes from the tool's own `EstimateDuration` (with `--workcell`, for
tools that are already configured; planning never configures a tool), else a
duration-like command param (`duration`, `timeout`, ...), else 60 s. Authored
durations are never changed.

## Checking programs

`rhylthyme validate` checks every instrument step's command and params against
galago's own definitions, naming the step, tool, command and field:

```text
$ rhylthyme validate shake.json --workcell lab.json
  - [instrument_invalid_command] Step 'shake': shaker (bioshake) start_shake: unknown param 'rpm' (takes speed, acceleration, duration)
```

Without `--workcell`, steps are checked against their `toolType`; steps with
neither get an `instrument_unchecked` warning. With `--workcell`, it also reports
tools the workcell lacks and `toolType`s that disagree with it. `rhylthyme run`
runs the same checks before configuring any tool.

From Python: `rhylthyme_galago.validate_command(tool_type, command, params)` and
`check_program(program, workcell=None)`.

## Development

```bash
pip install -e ".[dev]"
pytest                      # unit tests; integration tests need galago-serve
GALAGO_SERVE=/path/to/galago-serve pytest -m integration
```

The integration tests find `galago-serve` through `GALAGO_SERVE`, then
`.venv-galago/bin/galago-serve`, then `PATH`, and are skipped when none exists.

### galago protos

`proto/galago/` holds galago-tools' `.proto` files, copied verbatim and pinned in
`proto/galago/UPSTREAM.json`. The Python stubs in `src/rhylthyme_galago/_gen/` are
generated from them under this package's namespace (the wire format is galago's own):

```bash
python scripts/refresh_protos.py --ref <galago-tools commit or tag>  # re-vendor + regenerate
python scripts/refresh_protos.py                                      # regenerate only
```

## License

Apache-2.0. The vendored galago-tools protos are Apache-2.0 too (Science
Corporation); see `proto/galago/LICENSE`.
