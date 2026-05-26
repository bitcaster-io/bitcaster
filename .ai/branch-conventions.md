# Branch Conventions

Patterns:
  <type>/<optional-issue-number>-<kebab-description>

Types:
  fix/    # bug fix
  feat/   # feature
  chore/  # maintenance, refactoring, tooling

Rules:
  - type is always required
  - issue-number is optional (include when available)
  - description is kebab-cased from issue title or short summary
  - if issue-number is present, place it right after type, before description

Examples:
  feat/193-add-multi-oidc-support
  feat/add-pwa-offline-mode
  fix/docker-version
  chore/update-dependencies
