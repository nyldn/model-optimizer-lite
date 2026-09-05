#!/usr/bin/env python3
"""On-demand model recommendations and review receipts. No inference dispatch."""

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import select
import selectors
import shutil
import signal
import subprocess
import sys
import time

LIMIT = 1024 * 1024
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$")
TASKS = ("mechanical", "implementation", "review", "architecture", "research", "debugging")


def identifier(value):
    return value if isinstance(value, str) and IDENTIFIER.fullmatch(value) else None


def read_json(path):
    with open(path, "rb") as handle:
        raw = handle.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError("input exceeds 1 MiB")
    return json.loads(raw)


def normalize_catalog(value):
    if not isinstance(value, dict):
        raise ValueError("catalog must be an object")
    value = value.get("result", value)
    if not isinstance(value, dict) or not isinstance(value.get("data"), list):
        raise ValueError("catalog requires a model/list data array")
    models = []
    seen = set()
    for row in value["data"]:
        if not isinstance(row, dict):
            raise ValueError("invalid model entry")
        model = identifier(row.get("model"))
        if not model or model in seen:
            raise ValueError("invalid or duplicate model identifier")
        seen.add(model)
        efforts = row.get("supportedReasoningEfforts", [])
        if not isinstance(efforts, list):
            raise ValueError("invalid effort list")
        names = []
        for effort in efforts:
            name = identifier(effort.get("reasoningEffort")) if isinstance(effort, dict) else None
            if not name:
                raise ValueError("invalid effort entry")
            names.append({"reasoningEffort": name})
        models.append({"model": model, "hidden": row.get("hidden", False) is not False,
                       "supportedReasoningEfforts": names})
    return {"data": models}


def route(host, task, complexity, current=None, pin=None, effort=None, available=None, escalate=False):
    if host not in ("claude", "codex") or task not in TASKS or complexity not in ("routine", "complex", "hard"):
        raise ValueError("invalid routing input")
    for value in (current, pin, effort):
        if value is not None and not identifier(value):
            raise ValueError("invalid model or effort identifier")
    if pin:
        model, reason = pin, "user-pin"
    elif current and not escalate:
        model, reason = current, "existing-context"
    else:
        if host == "claude":
            model = {"routine": "sonnet", "complex": "opus", "hard": "fable"}[complexity]
        elif complexity == "hard":
            model = "gpt-6-astra"
        elif complexity == "complex":
            model = "gpt-5.6-sol"
        else:
            model = "gpt-5.6-luna" if task == "mechanical" else "gpt-5.6-terra"
        reason = "explicit-escalation" if escalate else "task-policy"
    status = "needs-capability-check"
    if available is not None:
        rows = normalize_catalog(available)["data"]
        match = next((row for row in rows if row["model"] == model and (not row["hidden"] or pin == model or current == model)), None)
        status = "available" if match else "unavailable"
        if match and effort and effort not in [e["reasoningEffort"] for e in match["supportedReasoningEfforts"]]:
            status = "unsupported-effort"
    return {"schema_version": 1, "host": host, "task": task, "complexity": complexity,
            "model": model, "effort": effort, "reason": reason, "status": status,
            "executed": False, "configuration_changed": False}


def verdict(text):
    if not isinstance(text, str):
        return None
    values = re.findall(r"^VERDICT: (APPROVE|REVISE)$", text, re.MULTILINE)
    return values[0] if len(values) == 1 else None


def review_receipt(host, events, expected, exit_code=0):
    if not identifier(expected) or not isinstance(events, list) or not events or not all(isinstance(e, dict) for e in events):
        raise ValueError("invalid review input")
    actual = None
    complete = False
    decision = None
    if host == "claude":
        final = None
        for event in events:
            message = event.get("message")
            if event.get("type") == "assistant":
                if not isinstance(message, dict):
                    raise ValueError("invalid assistant event")
                content = message.get("content", [])
                if not isinstance(content, list) or not all(isinstance(part, dict) for part in content):
                    raise ValueError("invalid assistant content")
                texts = [part.get("text") for part in content if part.get("type") == "text"]
                if not all(isinstance(text, str) for text in texts):
                    raise ValueError("invalid assistant text")
                if texts:
                    final = (identifier(message.get("model")), "\n".join(texts))
        result = events[-1]
        if final:
            actual, text = final
            decision = verdict(text)
            complete = (result.get("type") == "result" and result.get("subtype") == "success"
                        and result.get("is_error") is False and decision is not None
                        and verdict(result.get("result")) == decision)
    elif host == "codex":
        # codex exec --json does not attest the model that wrote the final text.
        # A launch flag, thread label, or model name in generated prose is not proof.
        final = None
        for event in events:
            if event.get("type") == "turn.started":
                final = None
            item = event.get("item")
            if event.get("type") == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
                final = item.get("text")
        decision = verdict(final)
        complete = events[-1].get("type") == "turn.completed" and decision is not None
        complete = complete and not any(e.get("type") in ("turn.failed", "error") for e in events)
    else:
        raise ValueError("unsupported review host")
    complete = complete and exit_code == 0
    verified = complete and actual == expected
    return {"schema_version": 1, "host": host, "requested_model": expected,
            "observed_model": actual, "model_verified": verified, "review_complete": complete,
            "process_exit_code": exit_code,
            "verdict": decision, "gate_passed": verified and decision == "APPROVE",
            "limitation": "model identity unavailable in codex exec JSON" if host == "codex" else None}


def discover_codex(executable="codex", timeout=15):
    """Read model/list through one short-lived app-server connection."""
    resolved = shutil.which(executable)
    if not resolved or ".app/Contents/" in str(Path(resolved).resolve()):
        raise ValueError("standalone Codex CLI unavailable")
    deadline = time.monotonic() + timeout
    proc = subprocess.Popen([resolved, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    os.set_blocking(proc.stdin.fileno(), False)
    buffer = b""
    total = 0

    def request(method, params, request_id=None):
        value = {"method": method, "params": params}
        if request_id is not None:
            value["id"] = request_id
        data = (json.dumps(value) + "\n").encode()
        offset = 0
        while offset < len(data):
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([], [proc.stdin.fileno()], [], remaining)[1]:
                raise ValueError("model discovery request timed out")
            try:
                offset += os.write(proc.stdin.fileno(), data[offset:])
            except BlockingIOError:
                continue

    def response(request_id):
        nonlocal buffer, total
        while time.monotonic() < deadline:
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                event = json.loads(line)
                if isinstance(event, dict) and event.get("id") == request_id:
                    if "error" in event or "result" not in event:
                        raise ValueError("model discovery request failed")
                    return event["result"]
            if not selector.select(max(0, deadline - time.monotonic())):
                break
            data = os.read(proc.stdout.fileno(), 65536)
            if not data:
                raise ValueError("model discovery ended before a response")
            total += len(data)
            if total > LIMIT:
                raise ValueError("model discovery output exceeds 1 MiB")
            buffer += data
        raise ValueError("model discovery timed out")

    try:
        request("initialize", {"clientInfo": {"name": "model_optimizer_lite", "version": "1"}}, 1)
        response(1)
        request("initialized", {})
        models, cursors = [], set()
        cursor = None
        for number in range(2, 22):
            params = {"limit": 100, "includeHidden": False}
            if cursor:
                params["cursor"] = cursor
            request("model/list", params, number)
            result = response(number)
            models.extend(normalize_catalog(result)["data"])
            cursor = result.get("nextCursor")
            if cursor is None:
                output = normalize_catalog({"data": models})
                output["source"] = "codex-app-server:model/list"
                output["observed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return output
            if not isinstance(cursor, str) or not cursor or cursor in cursors:
                raise ValueError("invalid model discovery pagination")
            cursors.add(cursor)
        raise ValueError("model discovery exceeded 20 pages")
    finally:
        selector.close()
        # Kill the group even when its parent already exited, so descendants do not linger.
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
        proc.stdin.close()
        proc.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    router = commands.add_parser("route", help="recommend only; never switch or launch a model")
    router.add_argument("--host", choices=("claude", "codex"), required=True)
    router.add_argument("--task", choices=TASKS, required=True)
    router.add_argument("--complexity", choices=("routine", "complex", "hard"), default="complex")
    router.add_argument("--current-model")
    router.add_argument("--model", help="explicit user pin; overrides task policy")
    router.add_argument("--effort")
    router.add_argument("--catalog", help="model/list JSON; inventory is not an entitlement guarantee")
    router.add_argument("--escalate", action="store_true", help="consider leaving the current model")
    discover = commands.add_parser("codex-models", help="discover models without an inference request; may contact provider")
    discover.add_argument("--timeout", type=int, default=15, choices=range(1, 61), metavar="SECONDS")
    receipt = commands.add_parser("review-receipt", help="validate review completion and observable model identity")
    receipt.add_argument("--host", choices=("claude", "codex"), required=True)
    receipt.add_argument("--expected-model", required=True)
    receipt.add_argument("--events", required=True, help="one run of JSONL events, at most 1 MiB")
    receipt.add_argument("--exit-code", required=True, type=int, help="recorded native process exit code")
    args = parser.parse_args()
    try:
        if args.command == "route":
            result = route(args.host, args.task, args.complexity, args.current_model, args.model,
                           args.effort, read_json(args.catalog) if args.catalog else None, args.escalate)
            code = 2 if result["status"] in ("unavailable", "unsupported-effort") else 0
        elif args.command == "codex-models":
            result, code = discover_codex(timeout=args.timeout), 0
        else:
            with open(args.events, "rb") as handle:
                raw = handle.read(LIMIT + 1)
            if len(raw) > LIMIT:
                raise ValueError("event stream exceeds 1 MiB")
            events = [json.loads(line) for line in raw.splitlines() if line.strip()]
            result = review_receipt(args.host, events, args.expected_model, exit_code=args.exit_code)
            code = 0 if result["gate_passed"] else 2
        print(json.dumps(result, sort_keys=True))
        return code
    except (ValueError, OSError, TypeError, KeyError):
        # Native output, prompts, configuration values, and local paths stay out of errors.
        print(json.dumps({"error": "Invalid input or unavailable capability; inspect the local input or CLI.",
                          "configuration_changed": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
