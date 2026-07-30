## Next Release

### Features

### Changes

- **Migrated off deprecated GraphQL APIs**: `stacklet-admin` no longer uses GraphQL
  fields/mutations that are deprecated in the platform schema. This includes some
  breaking changes:
  - `repository add` no longer accepts `--branch-name`, `--policy-file-suffix`,
    `--policy-directory`, or `--deep-import` — the platform's replacement
    `addRepositoryConfig` mutation no longer supports configuring these at
    repository-creation time.
  - `repository process`, `repository scan`, `repository remove`, and
    `repository show` now take `--uuid` (the repository config UUID) instead of
    `--url`. `repository scan` no longer accepts `--start-rev-spec`.
  - `account-group add-item` no longer accepts `--provider` (implied by the
    target account group).
  - `account-group list/show/add/update/remove` and `policy-collection
    list/show/add/update/add-item/remove-item/remove` now return account/policy
    mappings (with a mapping id and pagination info) instead of the deprecated
    flat `items`/`itemCount` fields.
  - `binding` commands now return execution variables nested under
    `executionConfig` instead of a top-level `variables` field.

### Fixes

---

## November 17, 2025

### Features

- **Python 3.14 support**: `stacklet-admin` now works with Python 3.14.

---
