Semantic refactoring plan
=========================

Purpose
-------

This plan turns the decisions in :doc:`semantic_inventory` into reviewable,
independently verifiable phases. It does not authorize all phases at once. Each
phase should begin only after the preceding phase is complete and the next
scope has been reviewed.

The refactor is successful when the package presents a smaller conceptual model
while encoding more Baserow knowledge. It should remove duplicated value
semantics, make all write paths agree, preserve hosted forward compatibility,
and leave another maintainer able to find each rule in one place.

The working release target is ``0.2.0b1`` on branch
``release/0.2.0b1``. The new minor beta identifies this as a deliberate,
potentially breaking public API revision. Keep the installed package and Sphinx
release aligned at ``0.2.0b1`` while Phase 8 prepares the release.

Constraints
-----------

* Hosted ``baserow.io`` is not version-pinned. Live behavior must be described
  by service and verification date.
* Existing public contracts should remain until a phase explicitly replaces
  them. Breaking changes are permitted during beta but must be deliberate,
  documented, and tested.
* The existing generic fallback must remain usable throughout the refactor.
* Live tests must run serially against the disposable configured tables and
  clean up resources they create.
* No phase should introduce a registry, plugin system, shared value hierarchy,
  or new dependency without a demonstrated requirement.
* Administrative workspace, database, table, view, user, and permission APIs
  remain out of scope.
* Automatic retries for mutating requests remain out of scope without an
  idempotency guarantee.

Phase 1: Establish offline characterization tests
-------------------------------------------------

Status: complete on branch ``release/0.2.0b1``. The offline baseline and the
unchanged hosted suite were verified on 2026-09-01.

Goal
~~~~

Create a fast, credential-free safety net around the Baserow metadata and value
shapes the refactor will move.

Work
~~~~

* Add sanitized JSON or Python fixtures derived from hosted field metadata and
  row responses. Fixtures must contain no token, authorization header, personal
  path, or unrelated user data.
* Characterize current number, date, select, linked-row, file, password,
  computed, collaborator, UUID, Autonumber, and unknown-field behavior.
* Test filter-tree and row payload serialization without making HTTP requests.
* Test structured error parsing at the request boundary using constructed
  responses or a fake session.
* Mark offline tests separately from live integration tests so both suites can
  be selected explicitly.

Exit criteria
~~~~~~~~~~~~~

* Offline tests run without ``.env`` or network access.
* Existing live integration tests still pass serially.
* Fixtures document their hosted verification date and source scenario.
* No public behavior has changed.

Phase 2: Introduce the Field semantic interface
------------------------------------------------

Status: implemented on branch ``release/0.2.0b1`` and verified against hosted
``baserow.io`` on 2026-09-01. Commit status is intentionally tracked separately
from phase completion.

Goal
~~~~

Give decoding, validation, and API encoding one explicit owner without yet
removing the existing public RowValue surface.

Work
~~~~

* Add explicit Field operations equivalent to ``decode(raw)``,
  ``validate(value)``, and ``encode(value)``. Exact method names may follow
  established package terminology, but their responsibilities must remain
  distinct.
* Make the base or unknown Field pass raw values through and preserve original
  API type and metadata.
* Implement the settled scalar contracts first: text-like values, booleans,
  ratings, Baserow decimal strings, and strict ISO dates. Keep UUID and
  Autonumber lossless through the unknown fallback until their dedicated field
  knowledge is added in Phase 4.
* Add explicit date parsing and display helpers driven by field metadata.
* Keep current RowValue classes as temporary delegates where compatibility
  requires them; do not duplicate newly moved logic.

Exit criteria
~~~~~~~~~~~~~

* Each implemented scalar rule has one Field-owned implementation and focused
  offline tests.
* Number reads preserve decimal strings and date reads preserve ISO strings.
* Date helpers reject implicit timezone and locale guessing.
* Unknown fields remain lossless and do not emit per-row warnings.
* Existing public Row and Table behavior remains available unless a reviewed
  defect requires an earlier correction.

Phase 3: Preserve structured value IDs and add file upload
----------------------------------------------------------

Status: implemented on branch ``release/0.2.0b1`` and verified against hosted
``baserow.io`` on 2026-09-01. Upload responses use ``original_name`` while
attached row-file responses can use ``visible_name``; both endpoint shapes are
preserved. Commit status is intentionally tracked separately from phase
completion.

Goal
~~~~

Preserve Baserow identity for structured values and separate file creation from
row assignment.

Work
~~~~

* Add independent, lossless value records for select options, linked rows,
  Baserow files, collaborators, and lookup entries as verified by fixtures.
* Decode single and multiple selects without discarding option IDs or metadata.
* Decode linked rows and lookups without discarding related row IDs.
* Accept the value records plus every Baserow-documented write form.
* Add optional strict label-resolution helpers that reject missing or ambiguous
  matches while preserving ordinary server-compatible label writes.
* Move file upload and upload-via-URL operations to the Client. Return an
  unattached Baserow file value and require explicit row assignment.
* Keep generic file downloading and directory traversal outside the semantic
  core. If retained, place them in a clearly separate utility.

Exit criteria
~~~~~~~~~~~~~

* Structured reads preserve identity and raw metadata.
* Returned domain values round-trip through the Field encoder.
* IDs, labels, documented comma-separated forms, and empty forms match hosted
  Baserow behavior.
* Duplicate-label strict helpers have deterministic tests.
* File upload and row assignment are independently testable operations.

Phase 4: Implement computed, unknown, and filter semantics
----------------------------------------------------------

Status: complete on branch ``release/0.2.0b1``. The full offline and serial
hosted suites passed on 2026-09-02. Focused hosted checks covered the configured
Formula button, Count, text Lookup, UUID, Autonumber, and representative
filters. Unobserved computed result families and field categories remain raw
through the generic fallback rather than being inferred. Commit status is
intentionally tracked separately from phase completion.

Goal
~~~~

Interpret computed results through their declared result metadata and make
filter compatibility forward-compatible.

Work
~~~~

* Dispatch formula, lookup, count, rollup, and related results through their
  result metadata and the existing scalar or identity value semantics.
* Preserve unknown computed result and error shapes raw.
* Add dedicated UUID and Autonumber field knowledge while retaining the unknown
  fallback for newer hosted types.
* Replace strict static filter enforcement with structural validation and
  advisory known compatibility.
* Distinguish supported, unsupported, and unknown filter compatibility.
* Keep JSON filter trees as the sole row-query encoding and remove the unused
  query-string path when migration permits.
* Add new field categories only after their hosted representations have been
  observed and recorded.

Exit criteria
~~~~~~~~~~~~~

* Computed values reuse the same representations as equivalent writable fields.
* Read-only status prevents every create and update path from sending computed
  fields.
* Unknown result types and unknown filter operators remain pass-through rather
  than becoming false client errors.
* Current hosted filter examples pass focused live compatibility tests.

Phase 5: Unify row create and update encoding
---------------------------------------------

Status: COMPLETE. On 2026-09-02, the Python 3.12 suites passed with 113 offline
tests and 35 serial hosted tests. Sphinx 9.1.0 also rebuilt the tracked
documentation successfully.

Goal
~~~~

Make every row write operation apply the same Field semantics and produce the
same wire representation for the same value.

Work
~~~~

* Route singular create, batch create, singular update, and batch update through
  one internal row encoder.
* Separate singular and plural methods where the current union inputs or return
  types make the contract ambiguous.
* Validate row IDs, batch sizes, writable fields, and response shapes in one
  consistent location.
* Define and test behavior for partial batch failure before adding any retry or
  recovery mechanism.
* Keep Row convenience operations as thin delegates to the same Table
  primitives.

Exit criteria
~~~~~~~~~~~~~

* Equivalent singular and batch inputs produce equivalent encoded field values.
* Create no longer bypasses Field validation and encoding.
* Mapping-based and object-based updates no longer diverge.
* Return types are fixed and documented for singular and plural operations.
* Live integration tests cover representative scalar, identity, computed
  exclusion, file, and unknown-field cases.

Phase 6: Simplify the public row and field model
------------------------------------------------

Status: complete on branch ``release/0.2.0b1`` and verified against hosted
``baserow.io`` on 2026-09-02. The public RowValue and custom-container layers
were removed in favor of Field-owned decoding and explicit read-only mappings.
Commit status is intentionally tracked separately from phase completion.

Goal
~~~~

Remove containers and per-cell classes that no longer own Baserow knowledge.

Work
~~~~

* Expose Table fields as an ordered read-only mapping by field name.
* Make Row item access return Field-decoded values and provide explicit raw
  value access.
* Remove ``FieldList``, ``RowValueList``, and per-type RowValue classes after all
  retained behavior has moved to Fields, value records, Client operations, or
  explicit utilities.
* Remove or explicitly model staged Row mutation so raw, decoded, and pending
  state cannot diverge.
* Review root-package exports and expose only the concepts intended as public
  contracts.
* Provide migration examples for label-only select/link values, file upload,
  ``row.values``, field iteration, and staged updates.

Exit criteria
~~~~~~~~~~~~~

* No remaining RowValue or custom-container behavior is required by the package
  implementation or tests.
* The public workflow remains Client to Table to Row, with Fields and a small
  set of Baserow value records.
* Raw Baserow values and metadata remain inspectable.
* Removed imports and changed return types are listed in the changelog and
  migration documentation.

Phase 7: Consolidate transport and discovery
--------------------------------------------

Status: complete on branch ``release/0.2.0b1`` and verified against hosted
``baserow.io`` on 2026-09-02. The Python 3.12 suite passed with 154 offline
tests and 37 serial hosted tests, including table discovery and both file
upload paths. The warning-strict Sphinx 9.1.0 build also passed. Commit status
is intentionally tracked separately from phase completion.

Goal
~~~~

Keep one reliable Baserow request boundary while making incidental transport
mechanics private.

Work
~~~~

* Consolidate authentication, timeout, connectivity, HTTP, parsing, and Baserow
  error behavior in one request implementation.
* Remove global logging configuration from client initialization.
* Make header combination, raw execution, and response parsing private.
* Retain one documented low-level request escape hatch with explicitly limited
  guarantees.
* Add table discovery within the database-token scope.
* Keep ``Baserow.get_table(table_id)`` uncached. A newly constructed Table
  lazily loads current hosted field metadata and is the documented way to
  obtain a new schema snapshot after an external schema change.
* Do not add schema-refresh cache invalidation without a demonstrated
  long-running application need. Database tokens cannot mutate schema, and a
  refresh method would need to define behavior for Rows created under the old
  schema.
* Configure timeout and any safe read-retry policy at Client construction.
* Do not retry mutating operations without an idempotency guarantee.

Exit criteria
~~~~~~~~~~~~~

* Endpoint methods, file uploads, pagination, and the low-level escape hatch all
  use the same exception and response boundary.
* Importing or constructing the package does not configure application logging.
* Separate Table instances do not share cached Fields; a newly constructed
  Table loads current hosted schema when its fields are first accessed.
* Table discovery is verified against hosted database-token permissions.

Phase 7.5: Tighten row contracts and remove residual duplication
-----------------------------------------------------------------

Status: complete on branch ``release/0.2.0b1``. On 2026-09-02, the Python 3.12
suite passed with 197 offline tests and 37 serial hosted tests. A subsequent
review identified the bounded corrections assigned to Phase 7.8.

Goal
~~~~

Resolve the bounded review findings left between transport consolidation and
release preparation without expanding the conceptual model.

Work
~~~~

* Split row retrieval into fixed ``get_rows`` list and ``iter_rows`` iterator
  contracts, remove legacy return-type switches and arbitrary query keyword
  arguments, and validate every pagination response before yielding rows.
* Make singular delete and move operations Table primitives used by Row
  conveniences. Keep an updated or moved Row synchronized with the response.
* Require batch deletion to receive a non-empty list of valid row IDs, validate
  all input before the first request, and expose partial progress after a later
  chunk fails.
* Make compatible-filter collections immutable and consolidate identical
  knowledge on the nearest common Field base.
* Consolidate shared select-option lookup mechanics without merging the
  different single-select and multiple-select wire contracts.
* Expand the public API snapshot to cover signatures and return-contract
  boundaries affected by the refactor.
* Replace whole-table integration cleanup with per-test tracking and deletion
  of only resources created by that test.
* Remove stale documentation output and the unused ``pytz`` dependency.

Exit criteria
~~~~~~~~~~~~~

* List and streaming row retrieval have distinct, tested signatures and reject
  malformed hosted page shapes consistently.
* Singular Row operations delegate through Table and batch deletion has the
  same preflight and partial-failure guarantees as other batch writes.
* Filter compatibility is exposed through immutable tuples with no duplicated
  per-instance list construction.
* Integration cleanup never discovers or deletes unrelated table contents.
* Offline and hosted suites pass serially and warning-strict documentation
  generation succeeds.

Phase 7.8: Stabilize contracts and test infrastructure
-------------------------------------------------------

Status: complete on branch ``release/0.2.0b1``. On 2026-09-02, all 215 offline
tests and 37 serial hosted tests passed under Python 3.12. The warning-strict
Sphinx 9.1.0 build also passed.

Goal
~~~~

Correct the release-blocking edge cases and remove small sources of misleading
or duplicated behavior found in the review after Phase 7.5.

Work
~~~~

* Record row IDs completed before a partial batch-add failure so integration
  cleanup can delete them.
* Define and validate integer contracts for row-query view, page-size, and
  result-limit parameters.
* Test public parameter names, kinds, and defaults without depending on how
  Python renders type annotations. Test the iterator contract without requiring
  a particular iterator implementation.
* Reuse the existing batch-progress exception implementation for deletion.
* Remove the unused linked-table integration fixture and configuration value;
  link fields obtain their related table ID from hosted field metadata.
* Replace dense user-facing terminology with direct descriptions of returned
  values and Field behavior.
* Remove Field constructors and validation overrides that only repeat inherited
  behavior.
* Require batch-delete responses to return HTTP 204 before recording completed
  row IDs, and remove redundant field-name exception logging.
* Remove obsolete local release outputs and unused or incorrectly named test
  support files before release verification.
* Correct the documented hosted test schema and settle the remaining generic
  fallback and base-field registry remnants.

Exit criteria
~~~~~~~~~~~~~

* Partial batch-add failure IDs are recorded by the integration resource
  tracker and covered by an offline regression test.
* ``view_id`` and ``size`` accept only positive integers; ``limit`` accepts only
  non-negative integers and zero performs no request.
* Public API tests survive annotation-only refactoring while still protecting
  parameter order, names, kinds, defaults, and observed return contracts.
* Row mutation progress has one implementation and integration configuration
  has one accurate documented source of truth.
* No behavior-free Field override identified by the review remains.
* Batch deletion cannot overstate confirmed IDs after an unexpected response,
  and release verification cannot include stale distributions.
* Offline and hosted suites pass serially and warning-strict documentation
  generation succeeds.

Phase 8: Compatibility, documentation, and beta release
--------------------------------------------------------

Status: implemented on branch ``release/0.2.0b1``. On 2026-09-02, all 240
offline tests and 37 serial hosted tests passed under Python 3.12, and the
warning-strict Sphinx 9.1.0 build passed. Isolated ``0.2.0b1`` wheel and source
artifacts passed Twine, wheel-install, source-content, and extracted-source
offline-test checks. Repeating artifact verification from the exact clean
release commit remains the final exit criterion.

Goal
~~~~

Close the remaining public-boundary, diagnostic, packaging, and documentation
gaps, then prepare one deliberate beta migration from a clean release commit.

Work
~~~~

* Keep user-supplied query, filter, search, payload, and phone-number values out
  of client-generated logs and default exception messages. Log the HTTP method
  and a safe origin and path without query values. Preserve structured Baserow
  error fields for callers to inspect explicitly, but do not automatically log
  a hosted error description that may repeat submitted data. Add log and
  exception tests that use recognizable sentinel values.
* Require table IDs and the client default batch size to be positive,
  non-boolean integers. Convert the integration environment's table ID from its
  string representation at the configuration boundary. Align annotations,
  documentation, and negative tests with these contracts.
* Validate successful field-schema responses before constructing Fields. The
  response must be a list of objects with the stable metadata needed by the
  client, including a positive field ID, non-empty name and type, and valid
  order. Preserve extra metadata and continue accepting unknown non-empty type
  strings through ``GenericField``. Cover malformed responses while preserving
  ``FieldDataRetrievalError`` chaining.
* Retain ``GenericField`` and the unknown-type fallback. Describe
  ``GenericField.TYPE == "generic"`` as an internal sentinel because the
  repository has no evidence that hosted Baserow returns a ``generic`` field
  type. Keep the explicit registry entry for this beta to avoid unnecessary
  compatibility churn.
* Make the included source-distribution tests runnable from declarations in the
  archive. Include both requirements files, retain the Python, JSON, Markdown,
  and WebP test assets, and verify the extracted source distribution after
  installing its declared development dependencies.
* Rewrite the semantic inventory as a description of the current contract.
  Remove intermediate labels such as "proposed focus", "Phase 6 row model",
  and "implemented through Phase 7.5", correct remaining prose errors, and
  retain historical evidence only where it explains a current decision.
* Remove the unused ``Row.logger`` and logging import, and correct the historical
  changelog date typo ``2024--8-06``.
* Run the full offline suite and the serial hosted integration suite. Exercise
  the generated API documentation's representative field and filter forms
  against the disposable tables.
* Update user documentation, docstrings, examples, public API reference,
  migration guidance, and changelog to describe the implemented behavior.
  Regenerate the tracked Sphinx output with warnings treated as errors.
* Update the package version and Sphinx release to ``0.2.0b1`` after the
  implementation and migration scope is complete. Confirm that ``setup.py``,
  Sphinx configuration, generated documentation, distribution filenames, and
  installed package metadata all report the same version.
* Explicitly stage every intended addition, deletion, fixture, and generated
  documentation change. Require a clean Git status, then build wheel and source
  distributions from a clean checkout of the release commit. Check both
  distributions and install the wheel in a clean Python 3.12 environment.

Exit criteria
~~~~~~~~~~~~~

* Client-generated logs and default exception messages omit sentinel query and
  payload values while structured Baserow error details remain available for
  explicit inspection.
* Invalid table IDs and default batch sizes fail during configuration, and
  malformed field-schema responses fail with a clear, chained package error.
* Offline and hosted suites pass without parallel execution, and the
  warning-strict documentation build passes.
* Every public contract in the documentation has a corresponding test or an
  explicitly identified hosted compatibility dependency.
* The semantic inventory describes the released behavior without requiring
  knowledge of the completed refactoring phases. The migration guide covers
  every intentional breaking change.
* ``setup.py``, Sphinx configuration, generated documentation, distribution
  filenames, and installed metadata all report ``0.2.0b1``.
* The extracted source distribution contains its declared test dependencies
  and required fixtures, and its offline suite passes in a clean Python 3.12
  environment.
* The release commit has a clean Git status and distribution verification
  succeeds from its clean checkout before any separate tag or publication
  request.

Working method for each phase
-----------------------------

Before implementation, turn the phase into a bounded checklist tied to current
files and tests. Keep commits aligned with one coherent outcome. At the end of a
phase:

#. run its offline tests and the relevant serial live tests;
#. compare public exports and documented return types;
#. update the inventory when new hosted evidence changes a recorded fact;
#. update user documentation only for behavior actually implemented;
#. report deferred risks separately rather than expanding the phase; and
#. review the next phase before beginning it.
