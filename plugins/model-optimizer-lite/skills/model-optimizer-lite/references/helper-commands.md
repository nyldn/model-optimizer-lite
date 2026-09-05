# Helper commands

Run these from the installed skill directory, or use its absolute script path.
They require Python 3.9+ on macOS, Linux, or WSL. None dispatches inference.

## Recommendation

```sh
python3 scripts/model_optimizer_lite.py route --host codex --task implementation --complexity complex
python3 scripts/model_optimizer_lite.py route --host codex --task debugging --complexity hard --current-model gpt-5.6-terra --escalate
python3 scripts/model_optimizer_lite.py route --host claude --task review --model opus
```

Explicit `--model` wins. `--current-model` preserves the session unless
`--escalate` is passed. An omitted effort means use the host's existing default.
`route` prints JSON, changes no files, and starts no provider process.

## Codex model discovery

```sh
python3 scripts/model_optimizer_lite.py codex-models > /tmp/optimizer-models.json
python3 scripts/model_optimizer_lite.py route --host codex --task debugging --complexity hard --catalog /tmp/optimizer-models.json
```

Discovery requires a standalone `codex` on PATH. It starts one short-lived native
app-server, initializes the protocol, and reads `model/list` with pagination.
It never starts a thread, submits a prompt, or writes provider settings. Native
startup may use account/network access and write its own logs or caches. The
helper terminates its process group on success, failure, or timeout. Output is
limited to 1 MiB and 20 pages; the default deadline is 15 seconds.

The output contains only model IDs, hidden flags, effort options, and discovery
provenance. Use it for the same client and host, and refresh after account or
client changes. A catalog is not an entitlement or execution guarantee.

Claude discovery remains a native `/model` check. The CLI can accept a reviewed
catalog with the same `data` shape for Claude, but it does not resolve aliases to
full provider IDs. Missing entries never trigger a silent fallback.

## Review receipts

```sh
python3 scripts/model_optimizer_lite.py review-receipt --host claude --expected-model claude-opus-5 --events /tmp/review.jsonl --exit-code 0
python3 scripts/model_optimizer_lite.py review-receipt --host codex --expected-model gpt-6-astra --events /tmp/review.jsonl --exit-code 0
```

Supply native events from one run, at most 1 MiB, and its actual process exit code.
The example's zero must be replaced when the native command failed. Claude uses `stream-json` output;
Codex uses `codex exec --json`. A Claude receipt checks the final text-bearing
assistant model, normal completion, and matching single-line verdicts in final
assistant and result messages. Mixed auxiliary usage never proves final identity.

Codex exec output can prove completion and a final verdict but does not provide
authoritative final-model identity. Its receipt reports `model_verified: false`
and leaves `observed_model` null. Never replace that with the requested model.
Such a result can be useful evidence, but cannot pass a gate that requires a
verified model. Use separately supported host evidence. An owner may revise a
requirement it introduced, but a user-required model or identity check remains
binding until the user changes it.

Exit 0 means a recommendation was produced, discovery succeeded, or a verified
review approved. Exit 2 means invalid input, unavailable model/effort, or a review
gate that did not pass. Read the JSON: `REVISE`, incomplete, and model-unverified
are different outcomes. Malformed inputs omit their contents from error output.
Receipts validate event structure, not signatures or the truth of findings. Keep
raw events locally with their command, artifact revision, and process exit code.
