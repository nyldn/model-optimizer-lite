# Shared optimizer implementation

Implemented in the existing repository after reviewing Octopus upstream
`1bee725` and current official provider documentation on 2026-09-05.

## Delivered

- Shared maintained skill source with generated Claude and Codex packages.
- Native Codex user/project install modes, detached from the source checkout.
- Existing Claude invocation, installer modes, managed markers, and legacy
  environment aliases preserved.
- Astra/Sol/Terra/Luna and Claude profiles with neutral task ownership.
- Deterministic recommendations that preserve pins and existing context.
- Bounded native Codex model discovery with no inference dispatch.
- Review receipts that distinguish completion, approval, and verified identity.
- Progressive disclosure and enforced entrypoint/always-on context limits.

## Validation evidence

- Legacy installer tests passed, including stdin install, repeated installs,
  rename migration, backups, symlinks, managed-block preservation, and file modes.
- Python tests cover routing, unsupported effort, model identity, malformed
  events, process failure, discovery pagination/timeouts, and Codex installation.
- Both package validators and byte-for-byte generated-source checks passed.
- Real installed Claude and Codex help expose the flags used by the references.
- Live Codex app-server discovery returned Astra and supported effort options.
- The independent 16-scenario policy pass and code review found specific issues;
  fixes include neutral ownership, preserved Astra pins, protected user-required
  identity checks, nonblocking discovery writes, and malformed-event rejection.

The recorded checks establish package and contract behavior. They do not measure
model quality, subscription savings, or automatic desktop model switching.
No provider configuration or installed skill was changed to run these checks.

## Migration

Existing Claude users can rerun their current install command. Codex users can
install the new package with `./install.sh codex`. Changed installations are
backed up outside discovery. Repository branding is AI Model Optimizer; the
Claude skill's existing discovery name remains stable through the transition.

Model and provider execution stay with native hosts. Choose Octopus explicitly
when a task requires its larger orchestration workflows.
