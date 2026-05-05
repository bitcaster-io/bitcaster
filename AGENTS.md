# Agent Instructions for Bitcaster

Bitcaster is a system-to-user notification platform. For detailed guidance, refer to the modular instruction files in the `.ai/` directory:

1. **[.ai/standards.md](.ai/standards.md):** Environment setup, Python/Django conventions, linting, and type safety rules.
2. **[.ai/architecture.md](.ai/architecture.md):** Project layout, code structure, and import patterns.
3. **[.ai/workflow.md](.ai/workflow.md):** Build/verify commands, CI rules, and validation protocols.
4. **[.ai/safety.md](.ai/safety.md):** Secret management, git safety, and data privacy rules.
5. **[.ai/testing-patterns.md](.ai/testing-patterns.md):** Test factories, fixtures, markers, and coverage rules.
6. **[.ai/dispatchers.md](.ai/dispatchers.md):** Dispatcher implementation and testing guidelines.

All `.ai/` files are the single source of truth for their respective domains. Do not duplicate this content in other instruction files.
