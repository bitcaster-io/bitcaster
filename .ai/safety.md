# AI Safety & Security

## Secret Management
- NEVER move secrets out of `.env` or `.envrc` files.
- NEVER hardcode credentials, tokens, or API keys into the source code.
- If a task requires modifying sensitive configurations, request explicit confirmation.

## Agent Behavior
- **Git Safety:** NEVER execute `git push` or `git commit` without explicit permission from the user.
- **Data Privacy:** Treat all project data as confidential. Do not leak internal logic to external prompts unless necessary for the task.
- **Traceability:** Log all significant self-modifications as a changelog if the task involves multi-file refactoring.
