# Agent Instructions for Bitcaster

Bitcaster is a system-to-user notification platform. For detailed guidance, refer to the modular instruction files in the `.ai/` directory:

## Mandatory first step

**Before any edit, commit, push, or PR: read every file in `.ai/`.** These
rules are binding and are not duplicated in this file. Do not start a task or
modify the codebase before you have read them all.

## Rule index

1. **[.ai/standards.md](.ai/standards.md):** Environment setup, Python/Django conventions, linting, and type safety rules.
2. **[.ai/architecture.md](.ai/architecture.md):** Project layout, code structure, and import patterns.
3. **[.ai/domain.md](.ai/domain.md):** Model hierarchy, ownership cascade, and access control patterns.
4. **[.ai/workflow.md](.ai/workflow.md):** Build/verify commands and validation protocol.
5. **[.ai/safety.md](.ai/safety.md):** Secret management, git safety, and data privacy rules.
6. **[.ai/testing-patterns.md](.ai/testing-patterns.md):** Test factories, fixtures, markers, and coverage rules.
7. **[.ai/dispatchers.md](.ai/dispatchers.md):** Dispatcher implementation and testing guidelines.
8. **[.ai/branch-conventions.md](.ai/branch-conventions.md):** Branch naming patterns.

All `.ai/` files are the single source of truth for their respective domains. Do not duplicate this content in other instruction files.
