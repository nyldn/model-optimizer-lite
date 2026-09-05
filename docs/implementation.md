# Shared optimizer implementation

Implemented in the existing repository after reviewing Octopus upstream
`1bee725` and current official provider documentation on 2026-09-05.

## Delivered

- Shared maintained skill source with one generated package for both hosts.
- Native Codex user/project install modes, detached from the source checkout.
- Unified `model-optimizer-lite` skill name, managed markers, and
  `MODEL_OPTIMIZER_LITE_` installer settings. Old-name aliases and migrations removed.
- Astra/Sol/Terra/Luna and Claude profiles with neutral task ownership.
- Deterministic recommendations that preserve pins and existing context.
- Bounded native Codex model discovery with no inference dispatch.
- Review receipts that distinguish completion, approval, and verified identity.
- Progressive disclosure and enforced entrypoint/always-on context limits.

## Validation evidence

- Installer tests cover stdin install, repeated installs, backups, symlinks,
  managed-block preservation, and file modes.
- Python tests cover routing, unsupported effort, model identity, malformed
  events, process failure, discovery pagination/timeouts, and Codex installation.
- Package validators and byte-for-byte generated-source checks passed.
- Real installed Claude and Codex help expose the flags used by the references.
- Live Codex app-server discovery returned Astra and supported effort options.
- The independent 16-scenario policy pass and code review found specific issues;
  fixes include neutral ownership, preserved Astra pins, protected user-required
  identity checks, nonblocking discovery writes, and malformed-event rejection.

The recorded checks establish package and contract behavior. They do not measure
model quality, subscription savings, or automatic desktop model switching.
No provider configuration or installed skill was changed to run these checks.

## Installation

Install for Claude with `./install.sh skill` or for Codex with
`./install.sh codex`. Both use the `model-optimizer-lite` package. Changed
installations are backed up outside discovery. No old-name migration is included.

Model and provider execution stay with native hosts. Choose Octopus explicitly
when a task requires its larger orchestration workflows.
