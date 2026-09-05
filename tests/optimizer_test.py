import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("optimizer", ROOT / "shared/scripts/model_optimizer_lite.py")
optimizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimizer)


def catalog(*models):
    return {"data": [{"model": model, "hidden": False,
                      "supportedReasoningEfforts": [{"reasoningEffort": "low"}, {"reasoningEffort": "high"}]
                      } for model in models]}


def claude_stream(model="claude-opus-5", verdict="APPROVE"):
    text = "VERDICT: " + verdict
    return [{"type": "assistant", "message": {"model": model, "content": [{"type": "text", "text": text}]}},
            {"type": "result", "subtype": "success", "is_error": False, "result": text}]


class RoutingTests(unittest.TestCase):
    def test_existing_context_is_preserved(self):
        result = optimizer.route("codex", "mechanical", "routine", current="gpt-6-astra")
        self.assertEqual(result["model"], "gpt-6-astra")
        self.assertEqual(result["reason"], "existing-context")

    def test_explicit_pin_wins_over_task_class(self):
        result = optimizer.route("codex", "implementation", "hard", pin="gpt-5.6-luna",
                                 available=catalog("gpt-5.6-luna", "gpt-6-astra"))
        self.assertEqual(result["model"], "gpt-5.6-luna")
        self.assertEqual(result["reason"], "user-pin")

    def test_no_catalog_does_not_promise_availability(self):
        result = optimizer.route("codex", "implementation", "hard")
        self.assertEqual(result["status"], "needs-capability-check")
        self.assertEqual(result["model"], "gpt-6-astra")
        self.assertFalse(result["executed"])

    def test_missing_pin_never_silently_falls_back(self):
        result = optimizer.route("codex", "implementation", "hard", pin="gpt-6-astra",
                                 available=catalog("gpt-5.6-sol"))
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["model"], "gpt-6-astra")

    def test_hidden_models_are_not_automatic_candidates(self):
        available = catalog("gpt-6-astra")
        available["data"][0]["hidden"] = True
        self.assertEqual(optimizer.route("codex", "research", "hard", available=available)["status"], "unavailable")

    def test_unsupported_effort_is_rejected(self):
        result = optimizer.route("codex", "review", "hard", effort="ultra", available=catalog("gpt-6-astra"))
        self.assertEqual(result["status"], "unsupported-effort")

    def test_no_effort_preserves_native_default(self):
        self.assertIsNone(optimizer.route("codex", "review", "complex", available=catalog("gpt-5.6-sol"))["effort"])

    def test_escalation_is_explicit(self):
        result = optimizer.route("codex", "debugging", "hard", current="gpt-5.6-terra", escalate=True,
                                 available=catalog("gpt-6-astra"))
        self.assertEqual(result["model"], "gpt-6-astra")

    def test_claude_and_codex_have_separate_defaults(self):
        self.assertEqual(optimizer.route("claude", "implementation", "complex")["model"], "opus")
        self.assertEqual(optimizer.route("codex", "implementation", "complex")["model"], "gpt-5.6-sol")

    def test_catalog_discards_private_and_unknown_fields(self):
        value = catalog("gpt-6-astra")
        value["private"] = "secret"
        value["data"][0]["description"] = "private endpoint"
        self.assertNotIn("private", json.dumps(optimizer.normalize_catalog(value)))


class ReceiptTests(unittest.TestCase):
    def test_completed_claude_review_verifies_final_model(self):
        result = optimizer.review_receipt("claude", claude_stream(), "claude-opus-5")
        self.assertTrue(result["gate_passed"])
        self.assertTrue(result["model_verified"])

    def test_fallback_does_not_pass_a_model_pin(self):
        result = optimizer.review_receipt("claude", claude_stream("claude-sonnet-5"), "claude-opus-5")
        self.assertFalse(result["gate_passed"])
        self.assertEqual(result["observed_model"], "claude-sonnet-5")

    def test_revise_is_valid_review_but_not_approval(self):
        result = optimizer.review_receipt("claude", claude_stream(verdict="REVISE"), "claude-opus-5")
        self.assertTrue(result["review_complete"])
        self.assertFalse(result["gate_passed"])

    def test_incomplete_or_error_run_is_rejected(self):
        for events in [claude_stream()[:1], claude_stream() + [{"type": "result", "subtype": "error", "is_error": True}]]:
            self.assertFalse(optimizer.review_receipt("claude", events, "claude-opus-5")["review_complete"])

    def test_conflicting_final_verdicts_are_rejected(self):
        events = claude_stream()
        events[-1]["result"] = "VERDICT: REVISE"
        self.assertFalse(optimizer.review_receipt("claude", events, "claude-opus-5")["review_complete"])

    def test_aggregate_usage_does_not_verify_final_model(self):
        events = claude_stream("claude-sonnet-5")
        events[-1]["modelUsage"] = {"claude-opus-5": {"outputTokens": 200}}
        self.assertFalse(optimizer.review_receipt("claude", events, "claude-opus-5")["model_verified"])

    def test_codex_completion_does_not_invent_model_identity(self):
        events = [{"type": "thread.started", "thread_id": "fixture"},
                  {"type": "item.completed", "item": {"type": "agent_message", "text": "VERDICT: APPROVE"}},
                  {"type": "turn.completed", "usage": {"input_tokens": 12, "output_tokens": 8}}]
        result = optimizer.review_receipt("codex", events, "gpt-6-astra")
        self.assertTrue(result["review_complete"])
        self.assertFalse(result["model_verified"])
        self.assertFalse(result["gate_passed"])
        self.assertIsNone(result["observed_model"])

    def test_receipt_omits_report_content(self):
        events = claude_stream()
        events[0]["message"]["content"][0]["text"] += "\nprivate finding"
        events[-1]["result"] += "\nprivate finding"
        self.assertNotIn("private", json.dumps(optimizer.review_receipt("claude", events, "claude-opus-5")))

    def test_process_failure_cannot_pass_a_successful_event(self):
        self.assertFalse(optimizer.review_receipt("claude", claude_stream(), "claude-opus-5", exit_code=1)["gate_passed"])

    def test_malformed_later_assistant_cannot_certify_an_earlier_model(self):
        events = claude_stream()
        events.insert(1, {"type": "assistant", "message": {"model": "claude-sonnet-5", "content": [{"type": "text", "text": None}]}})
        with self.assertRaises(ValueError):
            optimizer.review_receipt("claude", events, "claude-opus-5")


class DiscoveryTests(unittest.TestCase):
    def fake(self, directory, body):
        path = Path(directory) / "codex"
        path.write_text("#!" + sys.executable + "\n" + body)
        path.chmod(0o755)
        return str(path)

    def test_paginated_protocol_and_output_redaction(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = self.fake(directory, '''import json,sys
for line in sys.stdin:
    request=json.loads(line)
    if request['method']=='initialize': result={}
    elif request['method']=='initialized': continue
    elif request['method']=='model/list':
        page=request['params'].get('cursor')
        result={'data':[{'model':'gpt-6-astra' if page is None else 'gpt-5.6-terra', 'description':'private value'}], 'nextCursor':'next' if page is None else None}
    else: raise RuntimeError('unexpected request')
    print(json.dumps({'id':request['id'],'result':result}),flush=True)
''')
            output = optimizer.discover_codex(executable=executable, timeout=2)
            self.assertEqual(len(output["data"]), 2)
            self.assertNotIn("private", json.dumps(output))

    def test_timeout_terminates_child(self):
        with tempfile.TemporaryDirectory() as directory:
            pid = Path(directory) / "pid"
            executable = self.fake(directory, "import os,time\nopen(" + repr(str(pid)) + ", 'w').write(str(os.getpid()))\ntime.sleep(10)\n")
            started = time.monotonic()
            with self.assertRaises(ValueError):
                optimizer.discover_codex(executable=executable, timeout=0.3)
            self.assertLess(time.monotonic() - started, 3)
            if pid.exists():
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(pid.read_text()), 0)

    def test_stalled_reader_cannot_block_pagination_past_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = self.fake(directory, '''import json,sys,time
for line in sys.stdin:
    request=json.loads(line)
    if request['method']=='initialize': result={}
    elif request['method']=='initialized': continue
    else:
        print(json.dumps({'id':request['id'],'result':{'data':[], 'nextCursor':'x'*100000}}),flush=True)
        time.sleep(10)
        break
    print(json.dumps({'id':request['id'],'result':result}),flush=True)
''')
            started = time.monotonic()
            with self.assertRaises(ValueError):
                optimizer.discover_codex(executable=executable, timeout=0.4)
            self.assertLess(time.monotonic() - started, 3)

    def test_invalid_and_oversize_output_is_rejected(self):
        for body in ["print('not JSON',flush=True)\n", "print('x'*1100000,flush=True)\n"]:
            with tempfile.TemporaryDirectory() as directory:
                executable = self.fake(directory, body)
                with self.assertRaises(ValueError):
                    optimizer.discover_codex(executable=executable, timeout=2)

    def test_app_bundled_runtime_is_rejected(self):
        with tempfile.TemporaryDirectory(suffix=".app") as directory:
            resources = Path(directory) / "Contents/Resources"
            resources.mkdir(parents=True)
            executable = self.fake(resources, "raise RuntimeError('must not run')\n")
            with self.assertRaises(ValueError):
                optimizer.discover_codex(executable=executable)


if __name__ == "__main__":
    unittest.main()
