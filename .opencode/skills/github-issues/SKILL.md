---
name: github-issues
description: Resolve GitHub issues using TDD: read, analyse, branch, test, fix, lint, type-check, rebase
license: MIT
compatibility: opencode
---

## What I do

Walk through a complete GitHub issue resolution: read the ticket, analyse it, branch, write a failing test, fix the code, lint, type-check, rebase, and push the branch.

## When to use me

Use this when you are asked to fix a bug, implement a feature, or handle a chore tracked as a GitHub issue. The issue number is required — if there isn't one, this skill doesn't apply.

## Procedure

### 1. Read the ticket and thread

```
gh issue view <N>
gh issue view <N> --comments
```

Read the full thread including all comments.

### 2. Analyse the thread and surface ambiguities

Read the full thread and produce a structured analysis. You must explicitly
list each of the following **before** proceeding:

**What is clear:** Facts, requirements, and expected behavior that are
unambiguous from the report.
**Assumptions:** Anything you must assume to proceed (environment, edge
cases, unstated behavior, implied requirements).
**Open questions / Ambiguities:** Anything unclear, contradictory, vague,
or missing.

**First run:** Present this analysis to the user and ask:
*"Here's my understanding of the issue. Is this correct?"*

- **Yes** → proceed to step 3.
- **No / partially** → incorporate the user's clarifications, update the
  analysis, and re-present. Repeat until the user confirms.

Do **not** proceed past this point without explicit user confirmation.

**Re-run after feedback:** Evaluate the latest comments. If they are
positive/approval, report to the user and stop. If they request changes,
clarify any ambiguity with the user before proceeding.

### 3. Present a plan before branching

Before creating a branch or writing any code, present a concrete plan:

- Which test you will write and where (`tests/...`)
- Which source files you will modify and how
- What the expected outcome is

Ask the user: *"Here's my plan. Shall I proceed?"*

- **Yes** → proceed to step 4.
- **No / revise** → discuss alternatives with the user, update the plan,
  and re-present. Repeat until the user confirms.

Do **not** create a branch or write any code until the user confirms.

### 4. Create a branch

Follow `.ai/branch-conventions.md` to name the branch. Fetch the latest `develop` and branch from it:

```
# origin/develop is assumed up-to-date with upstream
git fetch origin develop
git checkout -b <branch-name> origin/develop
```

### 5. Write a failing test

Write a test that reproduces the bug or validates the feature. Follow project conventions:
- Place the test in `tests/`, mirroring the source path under `src/bitcaster/`
- Use fixtures to wrap factories — never call factories directly in tests
- See `.ai/testing-patterns.md` for details

### 6. Confirm the test fails

```
tox -e tests -- pytest <path-to-test> -x --no-cov
```

Verify the test fails as expected.

### 7. Patch the source code

Find and fix the relevant code in `src/bitcaster/`.

### 8. Iterate until tests pass

Repeat until the test passes:

```
tox -e tests -- pytest <path-to-test> -x --no-cov
```

If you need to run the full test suite:

```
tox -e tests
```

### 9. Lint and fix loop

```
tox -e lint
```

If lint fails, fix the errors. If any source code changed during fixing, re-run the tests (step 8). Repeat until both lint and tests are clean.

### 10. Mypy and fix loop

```
tox -e mypy
```

If mypy fails, fix the errors. If any source code changed during fixing, re-run the tests (step 8). Repeat until both mypy and tests are clean.

### 11. Re-check issue for new comments

```
gh issue view <N> --comments
```

If new comments or review requests have arrived since step 2, re-enter at step 7 (patch source code) or step 5 (write a new failing test) depending on what the feedback requires. If nothing has changed, proceed to step 12.

### 12. Propose and create a commit

Present the changes to the user and ask for approval before committing:

1. Show a summary of what changed:
   ```
   git diff --stat
   ```
2. Draft a commit message from the issue title, rephrased in the
   **imperative mood** to describe what the commit *does*. Use the branch
   prefix (`fix/`, `feat/`, `chore/`) as the Conventional Commits type:
   ```
   <type>: <issue title>

   Closes #<N>
   ```
3. **Ask the user:** *"Shall I commit these changes with this message?
   [y/n / edit]"*
   - **y** → `git commit -m "<message>"`
   - **edit** → prompt the user for their message and use that
   - **n** → stop and report back to the user

Do **not** proceed past this point without explicit approval.

### 13. Fetch and rebase

Detect the correct upstream remote. If `upstream` exists, rebase against the canonical repo (fork workflow). Otherwise fall back to `origin` (direct contributor):

```bash
DEFAULT_BRANCH="develop"

if git remote get-url upstream > /dev/null 2>&1; then
  TARGET_REMOTE="upstream"
else
  TARGET_REMOTE="origin"
fi

git fetch "$TARGET_REMOTE" "$DEFAULT_BRANCH"
git rebase "$TARGET_REMOTE/$DEFAULT_BRANCH"
```

If there are conflicts, **stop and alert the user**. Do not attempt to resolve conflicts automatically. If the user resolves them manually, re-enter at step 8 (iterate until tests pass) to re-verify the full pipeline.

### 14. Push the branch

Ask the user for approval before pushing:

- *"Branch `<branch-name>` is rebased and ready. Shall I push to `origin`?
  [y/n]"*
- If approved, push:
  ```
  git push origin <branch-name>
  ```
- If declined, stop and report back.

Notify the user the branch is pushed and ready for them to open a PR.

If new feedback arrives later and the user asks you to handle it, re-enter the procedure at step 1.
