"""Publish a live instrument run to rhylthyme.com (the web bridge, slice 1).

``rhylthyme bridge --workcell lab.json PROGRAM`` runs a program exactly like
``rhylthyme run`` and, while it runs, keeps two rows up to date in the user's
own Supabase tables (owner-only RLS; see rhylthyme-server/sql/galago_bridges.sql
and docs/design/web-bridge.md):

- ``bridges``: this lab machine, its tools (name, type, status) and a
  heartbeat;
- ``bridge_state``: the run's steps, their status, the tool each waits on and
  any failure.

Only outbound HTTPS, with the user's session. Nothing about where a tool
listens ever leaves the machine: rows are built from an allowlist of fields,
and error text is scrubbed of every workcell host and port.
"""

import base64
import json
import re
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional

from .workcell import Workcell

TokenFn = Callable[[], str]

HEARTBEAT_SECONDS = 10.0
STATE_SECONDS = 1.0


class BridgeError(RuntimeError):
    """The bridge could not reach or write to rhylthyme.com."""


def user_id_from_token(token: str) -> str:
    """The ``sub`` of a Supabase JWT (the server re-checks it through RLS)."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))["sub"]
    except Exception as e:  # noqa: BLE001
        raise BridgeError("The saved session is not a usable token; run `rhylthyme login`.") from e


def bridge_id_for(workcell: Workcell, config_path: Path) -> str:
    """A stable id per workcell on this machine, kept in ``config_path``."""
    try:
        ids = json.loads(config_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        ids = {}
    if workcell.id not in ids:
        ids[workcell.id] = str(uuid.uuid4())
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(ids, indent=2))
    return ids[workcell.id]


def scrubber(workcell: Workcell) -> Callable[[str], str]:
    """Replace every workcell host/port in free text with the tool's name."""
    pairs = []
    for tool in workcell.tools.values():
        pairs.append((f"{tool.host}:{tool.port}", tool.name))
        pairs.append((tool.host, tool.name))
        for value in (tool.config or {}).values():
            if isinstance(value, str) and value:
                pairs.append((value, "<config>"))
    # Longest first, so "10.0.0.12:50010" goes before "10.0.0.12".
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    pattern = re.compile("|".join(re.escape(p[0]) for p in pairs)) if pairs else None
    mapping = dict(pairs)

    def scrub(text: Optional[str]) -> str:
        if not text or pattern is None:
            return text or ""
        return pattern.sub(lambda m: mapping[m.group(0)], text)

    return scrub


def _status_value(status: Any) -> str:
    return getattr(status, "value", str(status))


def run_status(runner: Any) -> str:
    if getattr(runner, "program_abort_reason", None):
        return "aborted"
    if getattr(runner, "failed_steps", None):
        return "failed"
    steps = list(runner.steps.values())
    if steps and all(_status_value(s.status) == "COMPLETED" for s in steps):
        return "completed"
    if getattr(runner, "is_paused", False):
        return "paused"
    if getattr(runner, "is_running", False):
        return "running"
    return "idle"


def snapshot(runner: Any, scrub: Callable[[str], str]) -> Dict[str, Any]:
    """The run as the web sees it: an allowlist of fields, error text scrubbed."""
    t0 = getattr(runner, "program_start_time", None)

    def rel(t: Optional[float]) -> Optional[float]:
        return round(t - t0, 2) if (t is not None and t0 is not None) else None

    steps = []
    for step in runner.steps.values():
        instrument = step.instrument or {}
        status = _status_value(step.status)
        failure = None
        if step.failure:
            failure = {
                "code": str(step.failure.get("code") or ""),
                "errorMessage": scrub(step.failure.get("errorMessage")),
            }
        steps.append(
            {
                "stepId": step.step_id,
                "name": step.name,
                "trackId": step.track_id,
                "status": status,
                "start": rel(step.start_time),
                "end": rel(step.end_time),
                "tool": instrument.get("tool"),
                "command": instrument.get("command"),
                "waitingOn": instrument.get("tool") if (instrument and status == "RUNNING") else None,
                "failure": failure,
                "abortReason": scrub(step.abort_reason) if step.abort_reason else None,
            }
        )
    clock = None
    if t0 is not None:
        clock = round(runner.current_time - t0, 2)
    return {
        "clock": clock,
        "paused": bool(getattr(runner, "is_paused", False)),
        "abortReason": scrub(getattr(runner, "program_abort_reason", None)) or None,
        "steps": steps,
    }


class SupabaseRest:
    """Minimal PostgREST client acting as the signed-in user."""

    def __init__(self, url: str, anon_key: str, token: TokenFn, timeout: float = 10.0):
        self.url = url.rstrip("/") + "/rest/v1"
        self.anon_key = anon_key
        self.token = token
        self.timeout = timeout

    def upsert(self, table: str, row: Mapping[str, Any], on_conflict: str) -> None:
        self._request(
            "POST",
            f"/{table}?on_conflict={on_conflict}",
            row,
            {"Prefer": "resolution=merge-duplicates,return=minimal"},
        )

    def patch(self, table: str, match: str, row: Mapping[str, Any]) -> None:
        self._request("PATCH", f"/{table}?{match}", row, {"Prefer": "return=minimal"})

    def _request(self, method: str, path: str, body: Any, extra: Dict[str, str]) -> None:
        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.token()}",
            "Content-Type": "application/json",
            **extra,
        }
        req = urllib.request.Request(
            self.url + path, data=json.dumps(body).encode(), headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            raise BridgeError(f"{method} {path.split('?')[0]}: HTTP {e.code} {detail}") from e
        except urllib.error.URLError as e:
            raise BridgeError(f"Could not reach rhylthyme.com: {e.reason}") from e


class Publisher:
    """Keeps ``bridges`` and ``bridge_state`` current on a background thread."""

    def __init__(
        self,
        runner: Any,
        *,
        rest: SupabaseRest,
        bridge_id: str,
        user_id: str,
        workcell: Workcell,
        tools: List[Dict[str, str]],
        program: Mapping[str, Any],
        mode: str,
        allows_live: bool,
        version: str,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self.runner = runner
        self.rest = rest
        self.bridge_id = bridge_id
        self.user_id = user_id
        self.workcell = workcell
        self.tools = tools
        self.program = program
        self.mode = mode
        self.allows_live = allows_live
        self.version = version
        self.scrub = scrubber(workcell)
        self.run_id = str(uuid.uuid4())
        self.on_error = on_error or (lambda message: None)
        self.last_error: Optional[str] = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_state: Optional[str] = None
        self._last_heartbeat = 0.0

    def bridge_row(self) -> Dict[str, Any]:
        return {
            "id": self.bridge_id,
            "user_id": self.user_id,
            "name": self.workcell.name,
            "allows_live": self.allows_live,
            "tools": self.tools,
            "version": self.version,
            "last_seen": _now_iso(),
        }

    def state_row(self) -> Dict[str, Any]:
        state = snapshot(self.runner, self.scrub)
        state["program"] = self.program
        return {
            "bridge_id": self.bridge_id,
            "user_id": self.user_id,
            "run_id": self.run_id,
            "program_name": self.program.get("name"),
            "mode": self.mode,
            "status": run_status(self.runner),
            "state": state,
            "updated_at": _now_iso(),
        }

    def publish_once(self, force: bool = False) -> None:
        now = time.time()
        if force or now - self._last_heartbeat >= HEARTBEAT_SECONDS:
            self.rest.upsert("bridges", self.bridge_row(), "id")
            self._last_heartbeat = now
        row = self.state_row()
        key = json.dumps({k: v for k, v in row.items() if k != "updated_at"}, sort_keys=True)
        if force or key != self._last_state:
            self.rest.upsert("bridge_state", row, "bridge_id")
            self._last_state = key

    def start(self) -> "Publisher":
        self.publish_once(force=True)  # fail fast: bad session, missing tables
        self._thread = threading.Thread(target=self._loop, name="rhylthyme-bridge", daemon=True)
        self._thread.start()
        return self

    def _loop(self) -> None:
        while not self._stop.wait(STATE_SECONDS):
            try:
                self.publish_once()
                self.last_error = None
            except Exception as e:  # noqa: BLE001 - keep running; report once
                message = str(e)
                if message != self.last_error:
                    self.on_error(message)
                self.last_error = message

    def stop(self) -> None:
        """Publish the final state, then stop."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        try:
            self.publish_once(force=True)
        except Exception as e:  # noqa: BLE001
            self.on_error(str(e))


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


__all__ = [
    "BridgeError",
    "Publisher",
    "SupabaseRest",
    "bridge_id_for",
    "run_status",
    "scrubber",
    "snapshot",
    "user_id_from_token",
]
