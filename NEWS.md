## Next Release

### Features

- **Dynamic policy collections**: `policy-collection add` accepts `--repository-uuid`,
  which makes the collection dynamic — its policies always match the latest scan of
  that repository. The repository view that does the scanning is configured with
  `--branch-name`, `--policy-file-suffix`, `--policy-directory` and `--start-rev-spec`
  (`TAIL` for a deep import, settable only at creation time). `policy-collection
  update` takes the same view options apart from `--start-rev-spec`.

  This restores the capability behind the `repository add` options removed in
  2026.08.10: the platform moved that configuration onto the repository *view*, which
  only exists as part of a dynamic policy collection.

- **`repository register`**: registers a repository config and its dynamic policy
  collection in one command, which is what it takes for a repository's policies to
  actually get scanned — `addRepositoryConfig` alone creates no view, and policies are
  scanned per view. Accepts the options of both halves, with `--collection-name` and
  `--collection-description` for the collection, plus `--deep-import` as shorthand for
  `--start-rev-spec=TAIL`.

- `repository remove` accepts `--cascade`, to also remove bindings and policy
  collections tied to the repository. (Added in 2026.08.10 but not noted at the time.)

### Changes

- `policy-collection` output now includes `autoUpdate`, `isDynamic`, `repositoryConfig`
  and `repositoryView`, and no longer selects the deprecated `repository` field. Use
  `repositoryConfig` instead.

### Fixes

---

## August 10, 2026

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

---

## November 17, 2025

### Features

- **Python 3.14 support**: `stacklet-admin` now works with Python 3.14.

---
