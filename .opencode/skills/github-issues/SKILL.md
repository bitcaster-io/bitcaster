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

### 2. Analyse the thread and determine if work is needed

Read the full thread and decide what action to take:

- **First run:** Check the original report for inconsistencies, missing info, or unclear requirements. Prompt the user if found.
- **Re-run after feedback:** Evaluate the latest comments. If they are positive/approval, report to the user and stop. If they request changes, clarify any ambiguity with the user, then proceed.

In all cases, if the issue is unclear, prompt the user before taking action.

### 3. Create a branch

Follow `.ai/branch-conventions.md` to name the branch. Create it with:

```
git checkout -b <branch-name>
```

### 4. Write a failing test

Write a test that reproduces the bug or validates the feature. Follow project conventions:
- Place the test in `tests/`, mirroring the source path under `src/bitcaster/`
- Use fixtures to wrap factories — never call factories directly in tests
- See `.ai/testing-patterns.md` for details

### 5. Confirm the test fails

```
tox -e tests -- pytest <path-to-test> -x --no-cov
```

Verify the test fails as expected.

### 6. Patch the source code

Find and fix the relevant code in `src/bitcaster/`.

### 7. Iterate until tests pass

Repeat until the test passes:

```
tox -e tests -- pytest <path-to-test> -x --no-cov
```

If you need to run the full test suite:

```
tox -e tests
```

### 8. Lint and fix loop

```
tox -e lint
```

If lint fails, fix the errors. If any source code changed during fixing, re-run the tests (step 7). Repeat until both lint and tests are clean.

### 9. Mypy and fix loop

```
tox -e mypy
```

If mypy fails, fix the errors. If any source code changed during fixing, re-run the tests (step 7). Repeat until both mypy and tests are clean.

### 10. Re-check issue for new comments

```
gh issue view <N> --comments
```

If new comments or review requests have arrived since step 2, re-enter at step 6 (patch source code) or step 4 (write a new failing test) depending on what the feedback requires. If nothing has changed, proceed to step 11.

### 11. Propose and create a commit

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

### 12. Fetch and rebase

Detect the correct upstream remote. If `upstream` exists, rebase against the canonical repo (fork workflow). Otherwise fall back to `origin` (direct contributor):

```bash
if git show-ref --verify refs/remotes/upstream/develop > /dev/null 2>&1; then
  git fetch upstream
  git rebase upstream/develop
else
  git fetch origin
  git rebase origin/develop
fi
```

If there are conflicts, **stop and alert the user**. Do not attempt to resolve conflicts automatically. If the user resolves them manually, re-enter at step 7 (iterate until tests pass) to re-verify the full pipeline.

### 13. Push the branch

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
