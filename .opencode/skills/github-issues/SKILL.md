---
name: github-issues
description: Resolve GitHub issues using TDD: read, analyse, branch, test, fix, lint, type-check, rebase
license: MIT
compatibility: opencode
---

## What I do

Walk through a complete GitHub issue resolution: read the ticket, analyse it, branch, write a failing test, fix the code, lint, type-check, rebase, and push the branch.

## When to use me

Use this when you are asked to fix a bug, implement a feature, or handle a chore tracked as a GitHub issue. An issue number is required as the starting point. If you also have a PR number/URL, the agent can additionally monitor PR review comments.

## Procedure

### 0. Load project context

Before reading the issue, load the project's conventions and domain model:

1. Read `AGENTS.md` — it lists every `.ai/` instruction file.
2. Read **all** `.ai/` files referenced there. These are the single source of truth for standards, architecture, testing, safety, dispatchers, and the domain model.
3. Pay special attention to:
   - `.ai/standards.md` — multi-tenancy isolation, relative imports, British English
   - `.ai/architecture.md` — src layout, module structure
   - `.ai/domain.md` — model hierarchy, owner cascading, access control patterns

Do **not** skip this step. The `.ai/` files contain mandatory rules the agent must follow.

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

When creating or modifying models (Organization, Project, Application, Event, etc.):
- Respect the **org → project → application → event** FK chain — never leave a gap
- Set `owner` with fallback: `Application.save()` auto-cascades from `project.owner`; `Project.save()` auto-cascades from `organization.owner`
- Use `.local()` queryset method to exclude the system `OS4D` org where appropriate
- For scoped models (ApiKey, MessageTemplate), use `ScopedManager` to auto-resolve the org/project/application hierarchy from kwargs
- See `.ai/domain.md` for the complete reference

### 8. Iterate until tests pass

Repeat until the test passes:

```
tox -e tests -- pytest <path-to-test> -x --no-cov
```

If you need to run the full test suite:

> **Note:** The full suite can take several minutes. When invoking the bash
> tool for this command, pass `timeout=600000` (10 minutes) to prevent
> premature timeout.

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

### 11. Re-check for new feedback

#### 11a. Always check issue comments

```
gh issue view <N> --comments
```

#### 11b. Attempt to find a linked PR

Try to derive a PR number from the issue:

```
PR_NUM=$(gh issue view <N> --json closedByPullRequestsReferences \
  --jq 'if length > 0 then .[0].number else "" end' 2>/dev/null)
```

**If `gh` succeeded and a PR is found** (non-empty `$PR_NUM`):

Present to the user: *"I found PR #$PR_NUM linked to this issue. Shall I also check PR review comments? [y/n]"*

- **Yes** → fetch review comments: `gh pr view $PR_NUM --comments`
- **No** → skip PR channel.

**If `gh` succeeded but no PR is found** (`$PR_NUM` empty):

Ask: *"Do you have a PR number? (leave blank for no)"*

- **Provided** → verify it exists: `gh pr view <PR_NUM>`. If the command fails (non-zero exit), warn the user and skip. Otherwise, fetch review comments.
- **Blank** → skip PR channel.

**If `gh` failed** (unauthenticated or not installed):

Ask: *"I could not reach GitHub CLI. Do you have a PR number? (leave blank for no)"*

- **Provided** → parse the owner/repo from `git remote get-url origin` and build the PR URL (`https://github.com/OWNER/REPO/pull/<PR_NUM>`). Use `webfetch` to retrieve the page. If it returns an error (e.g. 404), warn the user and skip. Otherwise, advise the user that review comments could not be fetched and suggest they paste relevant feedback.
- **Blank** → skip PR channel.

#### 11c. Evaluate feedback

Combine issue comments and PR review comments (if any). Decide:

- **New change requests / review requests** → re-enter at step 7 (patch source code) or step 5 (write a new failing test), depending on what the feedback requires.
- **Nothing new or only approval** → proceed to step 12.

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

Notify the user the branch is pushed and ready for them to open a PR:

*"Branch `<branch-name>` is pushed. Once a PR is created from it, it will be auto-linked to issue #<N>. You can ask me to handle PR feedback later — I will try to detect the PR automatically."*

If new feedback arrives later and the user asks you to handle it, re-enter at step 1 with the same issue number. The agent will attempt to find a linked PR (step 11b) and check both issue comments and PR review comments.
