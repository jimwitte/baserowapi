# Repository guidance

## Purpose and architecture

`baserowapi` is a synchronous Python client for the hosted Baserow API. Python
3.12 is the supported development runtime.

The public workflow is `Baserow` -> `Table` -> `Row`. `Baserow` owns HTTP
sessions and request handling, `Table` handles field metadata and row
operations, and `Row` provides typed field access and single-row operations.
Field and RowValue subclasses translate between Baserow metadata, API payloads,
and Python values. Unknown field types fall back to the generic field and row
value implementations.

Important locations:

* `baserowapi/` contains the package implementation.
* `baserowapi/models/fields/` defines field metadata, validation, and API
  formatting.
* `baserowapi/models/row_values/` defines values exposed through rows.
* `tests/` contains live integration tests against hosted `baserow.io`.
* `docsrc/` contains the handwritten Sphinx documentation sources.
* `docs/` contains generated, tracked documentation output.

## Working rules

Inspect the relevant implementation, callers, tests, and documentation before
changing behavior. Treat the implementation as authoritative for current
behavior when existing documentation disagrees, then correct the documentation
as part of the change.

Preserve existing public contracts unless a defect or a justified design change
requires breaking them. This package is beta, so breaking changes are permitted
when necessary, but they must be deliberate and documented. Pay particular
attention to public imports, return types, list-versus-generator behavior, lazy
field loading, pagination, batching, validation, value formatting, and exception
types.

Keep changes focused and explicit. Avoid speculative abstractions, unrelated
refactoring, and new dependencies without a concrete need. Preserve unrelated
working-tree changes and generated artifacts that are outside the task.

When adding support for a Baserow field type, update both the Table field-class
mapping and the Row row-value mapping. Add tests for metadata handling,
validation, API formatting, and returned values as applicable. Retain the
generic fallback for unknown hosted Baserow field types.

Package exceptions must have one definition and a consistent inheritance
hierarchy rooted in `BaserowAPIError`. Preserve underlying failures with
exception chaining. Do not indiscriminately replace HTTP, connectivity,
timeout, validation, and parsing failures with generic `Exception` instances.

## Development environment

Use the devcontainer as the canonical development environment. To reproduce its
Python setup manually, install the development dependencies and package with:

```sh
python -m pip install --no-cache-dir -r requirements_dev.txt
python -m pip install --no-cache-dir -e .
```

Do not assume an offline unit-test suite exists. The current test suite requires
network access and configured Baserow credentials.

Keep runtime and development dependency declarations consistent when changing
dependencies. Do not edit build output, distribution archives, egg metadata,
Python caches, or pytest caches by hand.

## Integration tests

All existing tests are live integration tests against hosted `baserow.io`.
They create, update, move, upload files to, and delete rows. The configured test
tables are disposable and are authorized for test mutation.

The tests read configuration from `.env` through these environment variables:

* `BASEROW_URL`
* `BASEROW_TOKEN`
* `BASEROW_TABLE_ID`
* `LINK_TABLE_ID`

Run the suite serially from the repository root with:

```sh
python -m pytest -m integration
```

Do not use pytest-xdist, parallel workers, or overlapping test runs. Several
tests assume exclusive ownership of table contents and ordering. When modifying
tests, record resources created by each test and clean them in fixture finalizers
so cleanup still runs after failures. Prefer deleting recorded resource IDs over
fetching and deleting all table rows.

Hosted `baserow.io` is not version-pinned. Treat unexpected service behavior as
a compatibility signal that must be investigated, not automatically as a
package defect. Describe compatibility verification by service and date rather
than claiming an unverified Baserow server version.

## Documentation and releases

Edit documentation in `docsrc/`, not in generated HTML. Public behavior changes
must update the relevant docstrings and `docsrc/*.rst` pages. Regenerate the
tracked `docs/` output with:

```sh
make -C docsrc html
```

Keep the package version, Sphinx release, and changelog consistent for release
work. Record breaking changes and meaningful public fixes in `changelog.txt`.
Build wheel and source distributions through the PEP 517 backend with:

```sh
python -m build
python -m twine check dist/*
```

Install the resulting wheel in a clean Python 3.12 environment before release.
Do not publish packages, upload distributions, create tags, or push Git changes
unless the user explicitly requests it.

## Credentials and local state

Never commit, modify, or print `.env` contents, Baserow tokens, `.pypirc`
credentials, authorization headers, or other secrets. Avoid logging sensitive
request data. Do not add personal Git identity, signing keys, or host-specific
credential mounts to shared repository configuration.
