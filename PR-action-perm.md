# Labels action fails on fork PR with HttpError

**Session ID:** ses_18c1b3840ffeeNtw7N2njpFyJ2
**Created:** 5/29/2026, 2:20:33 PM
**Updated:** 5/29/2026, 2:20:58 PM

---

## User

When creating PR from this fork the action "labels pull requests" fails with "Error: HttpError: Resource not accessible by integration". See  https://github.com/bitcaster-io/bitcaster/actions/runs/26149032537?pr=193 . Why?

---

## Assistant (Plan · Big Pickle · 2.9s)

_Thinking:_

The user is asking about a GitHub Actions workflow failure. The error "Resource not accessible by integration" typically occurs when a GitHub Actions workflow (especially one triggered by a fork/PR from a fork) tries to use a token that doesn't have sufficient permissions. Let me look at the workflow file that handles labeling pull requests.

Let me find the relevant workflow file.

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/*label*"
}
```

**Output:**
```
/home/gigio/PROJS/KT/bitcaster/src/bitcaster/social/migrations/0002_socialprovider_label.py
/home/gigio/PROJS/KT/bitcaster/src/bitcaster/social/migrations/0003_alter_socialprovider_label.py
/home/gigio/PROJS/KT/bitcaster/.github/workflows/labelize.yml
```

**Tool: grep**

**Input:**
```json
{
  "pattern": "labels.*pull|pull.*labels",
  "include": "*.yml"
}
```

**Output:**
```
Found 2 matches
/home/gigio/PROJS/KT/bitcaster/.github/workflows/labelize.yml:
  Line 1: # Adds labels to pull requests for the type of change the PR makes

  Line 19:     name: labels pull requests

```

---

## Assistant (Plan · Big Pickle · 1.9s)

_Thinking:_

Let me read the labelize workflow file to understand the issue.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/gigio/PROJS/KT/bitcaster/.github/workflows/labelize.yml"
}
```

**Output:**
```
<path>/home/gigio/PROJS/KT/bitcaster/.github/workflows/labelize.yml</path>
<type>file</type>
<content>
1: # Adds labels to pull requests for the type of change the PR makes
2: name: Adds labels
3: 
4: on:
5:   pull_request:
6:     types: [opened, synchronize, edited, ready_for_review]
7: 
8: permissions:
9:   pull-requests: write
10:   id-token: write
11:   contents: read
12: 
13: jobs:
14:   label-pullrequest:
15:     permissions:
16:       contents: read
17:       issues: write
18:       pull-requests: write
19:     name: labels pull requests
20:     runs-on: ubuntu-latest
21:     steps:
22:       - uses: actions/checkout@v4
23:         with:
24:           persist-credentials: false
25: 
26:       - name: Check for file changes
27:         uses: dorny/paths-filter@v3
28:         id: changes
29:         with:
30:           token: ${{ github.token }}
31:           filters: .github/file-filters.yml
32: 
33:       - name: Add Migration label
34:         uses: actions-ecosystem/action-add-labels@v1
35:         if: steps.changes.outputs.migrations == 'true'
36:         with:
37:           labels: 'Add/Change migration(s)'
38: 
39:       - name: Add Dependencies label
40:         uses: actions-ecosystem/action-add-labels@v1
41:         if: steps.changes.outputs.dependencies == 'true'
42:         with:
43:           labels: 'Add/Change dependencies'
44: 
45:       - name: Code configuration settings
46:         uses: actions-ecosystem/action-add-labels@v1
47:         if: steps.changes.outputs.code_settings == 'true'
48:         with:
49:           labels: 'Change Linters Configuration'
50: 
51:       - name: GitHub Configuration
52:         uses: actions-ecosystem/action-add-labels@v1
53:         if: steps.changes.outputs.actions == 'true'
54:         with:
55:           labels: 'GitHub Actions'

(End of file - total 55 lines)
</content>
```

---

## Assistant (Plan · Big Pickle · 9.7s)

_Thinking:_

The issue is clear. When a PR is created from a fork, GitHub Actions runs with a read-only `GITHUB_TOKEN` for security reasons. The `actions-ecosystem/action-add-labels` action (and similar actions that modify PR labels) requires write permissions to pull-requests, but PRs from forks don't have access to repository secrets and use a restricted token.

However, the workflow does declare the permissions correctly at both the top level (line 8-11) and the job level (lines 15-18). The problem is:

When a PR is opened from a fork, GitHub Actions workflows that are triggered by `pull_request` events run with a read-only token by default, regardless of what `permissions` you specify in the workflow file. This is a security feature of GitHub Actions - fork PRs cannot be given write access to the repository through the `GITHUB_TOKEN`.

The error "Resource not accessible by integration" happens because the `GITHUB_TOKEN` is read-only for PRs from forks, and the `actions-ecosystem/action-add-labels` action needs write permissions to add labels.

Possible solutions:
1. Use a different approach that handles fork PRs - like using `pull_request_target` event instead of `pull_request` (but this has security implications)
2. Use a personal access token (PAT) stored as a secret instead of `GITHUB_TOKEN`
3. Use an alternative approach like `actions/labeler` which might handle this differently

Let me look at the `pull_request_target` approach - using `pull_request_target` runs the workflow in the context of the base repository (not the fork), so it has access to secrets and full write permissions. However, this is risky because you're checking out and executing code from the fork.

Actually, looking more carefully at the workflow - the `paths-filter` action uses `${{ github.token }}` explicitly. And `action-add-labels` also uses the token implicitly.

The issue is specifically that:
1. The workflow runs on `pull_request` (not `pull_request_target`)
2. For PRs from forks, `GITHUB_TOKEN` is read-only
3. The `action-add-labels` action can't write labels

The fix would be to change the trigger to `pull_request_target` or to use a PAT token.

But wait - there's also another subtlety. Even with `permissions` set at the workflow level, for fork PRs, GitHub still restricts the token. From GitHub docs:

> When a workflow is triggered by a `pull_request` event from a forked repository, the `GITHUB_TOKEN` has read-only permissions and the token is not passed to any action called by the workflow.

So the `permissions` block is essentially ignored for fork PRs when using `pull_request` event.

The common fix is to use `pull_request_target` but with caution. Let me check if there's a safer alternative.

Actually, for labeling PRs, `pull_request_target` is commonly used and safe as long as you don't check out the fork's code (or if you do, don't execute it). In this case, the workflow checks out the code but only uses `paths-filter` to check file changes and then labels accordingly. The actual labeling action doesn't execute any code from the fork.

However, there's still a risk with `dorny/paths-filter` - it reads files from the checkout. If you use `pull_request_target`, the checkout would be of the base branch, not the PR head, which might give incorrect results.

The safest approach for labeling PRs from forks:
1. Use `pull_request_target` event
2. Check out the PR's code using `actions/checkout` with `ref: ${{ github.event.pull_request.head.sha }}`
3. Run the labeling logic

Or alternatively, use a GitHub App token or PAT secret.

Let me look at what the actual error is more carefully. The user said it fails with "Resource not accessible by integration". This is the classic fork PR issue.

Let me also check if there's a `file-filters.yml` to understand the full picture.

**Tool: grep**

**Input:**
```json
{
  "pattern": "pull_request_target",
  "include": "*.yml"
}
```

**Output:**
```
No files found
```

**Tool: glob**

**Input:**
```json
{
  "pattern": ".github/file-filters.yml"
}
```

**Output:**
```
/home/gigio/PROJS/KT/bitcaster/.github/file-filters.yml
```

---

## Assistant (Plan · Big Pickle · 2.4s)

_Thinking:_

Let me check if there are any actions workflow files that reference anything about secrets or tokens that might be relevant, and also look at any other workflow files for patterns.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/gigio/PROJS/KT/bitcaster/.github/file-filters.yml"
}
```

**Output:**
```
<path>/home/gigio/PROJS/KT/bitcaster/.github/file-filters.yml</path>
<type>file</type>
<content>
1: # This is used by the action https://github.com/dorny/paths-filter
2: docker: &docker
3:   - added|modified: './docker/**/*'
4:   - added|modified: './docker/*'
5: 
6: dependencies: &dependencies
7:   - 'uv.lock'
8:   - 'pyproject.toml'
9: 
10: actions: &actions
11:   - added|modified: './.github/**/*'
12: 
13: python: &python
14:   - added|modified: 'src/**'
15:   - added|modified: 'tests/**'
16:   - 'manage.py'
17: 
18: changelog:
19:   - added|modified: 'changes/**'
20:   - 'CHANGELOG.md'
21: 
22: mypy:
23:   - *python
24:   - 'mypy.ini'
25: 
26: run_tests:
27:   - *actions
28:   - *python
29:   - *docker
30:   - *dependencies
31:   - 'pytest.ini'
32:   - 'tox.ini'
33: 
34: package: &package
35:   - *python
36:   - *dependencies
37: 
38: dockerize:
39:   - *package
40:   - *docker
41:   - '.github/workflows/test.yml'
42:   - '.github/workflows/dockerize.yml'
43: 
44: migrations:
45:   - added|modified: 'src/**/migrations/*'
46: 
47: code_settings: &code_settings
48:   - '.pre-commit-config.yaml'
49:   - '.semgrep.yaml'
50:   - '.semgrepignore'
51:   - '.trivyignore'
52:   - 'bandit.yaml'
53:   - 'djlint.toml'
54:   - 'mypy.ini'
55:   - 'pyproject.toml'
56:   - 'pytest.ini'
57:   - 'ruff.toml'
58:   - 'tox.ini'
59:   - 'transifex.yml'
60:   - 'trivy.yaml'
61: 
62: 
63: lint:
64:   - *python
65:   - *code_settings
66: 
67: docs:
68:   - added|modified: './docs/**/*'
69:   - modified: '.mkdocs.yml'
70:   - modified: './src/bitcaster/config/__init__.py'
71:   - modified: './github/workflows/docs.yml'
72:   - modified: './github/file-filters.yml'

(End of file - total 72 lines)
</content>
```

---

## Assistant (Plan · Big Pickle · 8.2s)

_Thinking:_

Now I have the full picture. The issue is:

1. The workflow `labelize.yml` is triggered on `pull_request` event
2. For PRs from forks, GitHub's `GITHUB_TOKEN` is automatically scoped to read-only permissions, regardless of the `permissions` block in the workflow file
3. The `actions-ecosystem/action-add-labels` action needs write permission to add labels to PRs
4. This causes the "Resource not accessible by integration" error

The fix is to change the trigger from `pull_request` to `pull_request_target`. The `pull_request_target` event runs in the context of the base repository (not the fork), so the `GITHUB_TOKEN` has the full permissions specified in the workflow.

However, there's a security consideration with `pull_request_target`:
- It runs with write permissions in the context of the base repo
- It checks out the base branch by default
- If not careful, malicious PRs could exfiltrate secrets

In this specific case:
- The workflow only labels PRs based on file changes
- The `actions/checkout` step with `persist-credentials: false` is used
- The labeling actions don't execute any code from the PR

So changing to `pull_request_target` should be safe. But we should also change the checkout to explicitly checkout the merge commit (or the PR head) so that `paths-filter` evaluates the PR's files correctly.

Actually, `paths-filter` with `pull_request_target` needs the PR's code, not the base. So we'd need:

```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha }}
    persist-credentials: false
```

Wait, but there's also a simpler approach. The `dorny/paths-filter` action supports a `ref` parameter to specify which ref to check. But the checkout needs to happen first.

Actually, let me think again. The issue is specifically about fork PRs. When running on `pull_request`:
- Fork PRs get a read-only token
- Labels can't be added

When running on `pull_request_target`:
- All PRs (including forks) use the token with permissions from the base repo
- But we need to checkout the PR's head sha to detect file changes correctly

The plan:
1. Change `on: pull_request` to `on: pull_request_target` (keeping the same types)
2. Update the checkout step to use `ref: ${{ github.event.pull_request.head.sha }}` so the file filters reflect the PR's changes

This is the standard fix for this issue. Let me present this to the user.

The error "Resource not accessible by integration" occurs because the workflow is triggered on `pull_request` (line 5 of `labelize.yml`). When a PR comes from a **fork**, GitHub **always** downgrades `GITHUB_TOKEN` to read-only — even if `permissions: write` is declared — as a security measure. Since `actions-ecosystem/action-add-labels@v1` needs `pull-requests: write` to add labels, it fails.

**Fix:** Change the trigger to [`pull_request_target`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request_target), which runs in the context of the base repository (where the token has its declared permissions) rather than the fork.

```diff
 on:
-  pull_request:
+  pull_request_target:
     types: [opened, synchronize, edited, ready_for_review]
```

And update the checkout to use the PR's head SHA so `paths-filter` evaluates the correct diff:

```diff
 - uses: actions/checkout@v4
   with:
+    ref: ${{ github.event.pull_request.head.sha }}
     persist-credentials: false
```

This is safe here because the workflow only reads file paths and applies labels — it never executes untrusted code from the fork.

---

