Field semantic inventory
========================

Purpose and status
------------------

This document inventories the Baserow-specific knowledge currently encoded by
``baserowapi``. It is a design input for narrowing the library's focus. It does
not expand the public API or promise support that the implementation does not
currently provide.

The proposed focus is a schema-aware client for Baserow's database-token data
API. Under that focus, the library should own behavior that callers would
otherwise have to rediscover from Baserow, including field metadata, read and
write representations, read-only rules, filtering, pagination, linked rows,
file upload, and Baserow error responses. General Python collection helpers,
permissive argument coercion, logging setup, and HTTP implementation details do
not belong in the public contract unless they support one of those behaviors.

Evidence for this inventory was collected from:

* package implementation and integration tests at release ``0.1.0b5``;
* a read-only schema request to the configured hosted ``baserow.io`` test table
  on 2026-09-01;
* disposable hosted write probes on 2026-09-01 for boolean and rating nulls,
  number precision beyond the configured decimal places, and a datetime with a
  non-UTC ISO offset;
* disposable hosted write probes on 2026-09-01 for select, link-row, and file
  IDs, labels, returned objects, comma-separated forms, empty forms, and nulls;
* hosted upload and explicit row-assignment tests on 2026-09-01, including the
  distinct user-file ``original_name`` and attached-file ``visible_name``
  payloads;
* a disposable hosted row probe on 2026-09-02 confirming a raw Formula button
  object, Count decimal string, empty text Lookup list, UUID string, and
  Autonumber integer;
* the generated API documentation captured on 2026-09-01, visually checked on
  2026-09-02 for configured filter lists, plus hosted equality and empty-result
  filter probes;
* the maintainer's generated API documentation for that database, captured on
  2026-09-01 and kept as an ignored local test reference; and
* Baserow's current `Database API documentation
  <https://baserow.io/user-docs/database-api>`_, `field overview
  <https://baserow.io/user-docs/baserow-field-overview>`_, and `database token
  documentation <https://baserow.io/user-docs/personal-api-tokens>`_.

Hosted Baserow is not version-pinned. Observations dated 2026-09-01 are
compatibility evidence, not a claim about a particular Baserow release.

Support levels
--------------

``Strong``
   The package encodes material Baserow behavior and integration tests exercise
   its important read and write forms.

``Partial``
   The package has a dedicated type or behavior, but one or more important
   representations, settings, operations, or tests are missing or inconsistent.

``Pass-through``
   The package mostly preserves the server value. The class name adds little or
   no semantic guarantee.

``Fallback``
   An unknown type is preserved through ``GenericField`` and
   ``GenericRowValue``. This supports reading but deliberately provides no
   validation or type-specific filtering.

``Absent``
   Current Baserow documentation identifies the field category, but the package
   has no dedicated support and the configured test table does not exercise it.

Cross-cutting value pipeline
----------------------------

The current field semantics are not applied uniformly. This is more important
than the behavior of any individual field class.

.. list-table::
   :header-rows: 1
   :widths: 19 28 25 28

   * - Path
     - Current behavior
     - Guarantee
     - Required direction
   * - Read row
     - ``Row`` chooses a ``RowValue`` subclass using a second type map, then
       ``row[name]`` returns ``RowValue.value``.
     - Scalar, unknown, select, link, lookup, file, and collaborator RowValues
       delegate to ``Field.decode_value``. Password remains an exception.
     - Fields now own scalar and identity-bearing semantics. RowValue classes
       remain compatibility facades until the public row model is simplified.
   * - Create rows
     - ``Table.add_rows`` checks only that field names are writable. It sends
       caller values directly to the batch endpoint.
     - Field validation and ``format_for_api`` are bypassed.
     - Validate and encode through the same field operation used by updates.
   * - Update one ``Row``
     - Mapping values are validated and formatted by ``Field``. An update with
       no mapping formats each writable ``RowValue``.
     - This is the most complete current value pipeline.
     - Make this pipeline authoritative and reuse it everywhere.
   * - Batch update mappings
     - Values are validated but the original mapping is sent without
       ``format_for_api``.
     - Validation and wire encoding can disagree with single-row updates.
     - Encode each supplied field value before constructing the batch payload.
   * - Filter rows
     - ``Table`` sends the sole JSON filter-tree encoding. Fields expose
       three-state advisory compatibility.
     - Supported, unsupported, and locally unknown operators are distinguished;
       no compatibility result blocks a normal query.
     - Keep structural Filter validation and allow unknown operators to reach
       the unpinned hosted service.
   * - Unknown type
     - Field and value mappings independently fall back to generic classes
       without routine warnings.
     - Raw values remain readable; writable unknown fields can be sent without
       semantic validation.
     - The fallback preserves the original type, metadata, and raw value as
       expected forward compatibility.

The two independent dispatch tables, ``Table.FIELD_TYPE_CLASS_MAP`` and
``ROW_VALUE_TYPE_MAPPING``, duplicate the list of supported Baserow types. A new
field currently requires coordinated changes to both maps. Fields own scalar
and structured decoding, validation, and encoding; ``format_for_api`` remains a
compatibility alias. The duplicate dispatch remains until the public row model
is simplified.

Field-by-field inventory
------------------------

The read and write columns below describe current package behavior, not every
shape the Baserow server may accept. In particular, create currently bypasses
the field encoders described in the write column.

.. list-table::
   :header-rows: 1
   :widths: 13 16 18 20 10 23

   * - API type
     - Baserow knowledge
     - Current read value
     - Current accepted or encoded write
     - Level
     - Finding
   * - ``text``
     - Text default, primary-field metadata, text filters.
     - ``str`` or ``None``.
     - ``str`` or ``None``; no transformation.
     - Partial
     - The field is useful schema metadata, but ``TextRowValue`` is only a
       type-checked pass-through. Local filters omit ``starts_with``.
   * - ``long_text``
     - Text default and rich-text flag.
     - ``str`` or ``None``.
     - ``str`` or ``None``; Markdown semantics are not interpreted.
     - Partial
     - The field class earns its metadata; the separate RowValue class does not.
       Local filters omit ``starts_with``.
   * - ``boolean``
     - Boolean filter and API scalar shape.
     - ``bool``.
     - Exactly ``bool``; ``None`` is rejected locally.
     - Partial
     - RowValue delegates to the field validator. Hosted ``baserow.io`` rejected
       a ``null`` write on 2026-09-01, confirming the non-null write policy.
   * - ``number``
     - Decimal-place and negative-number settings; numeric filters.
     - Hosted tests currently receive a decimal string such as ``"42.00"``.
     - ``int``, ``float``, numeric ``str``, or ``None``; value is returned
       unchanged after validation.
     - Partial
     - Reads remain lossless strings. Validation uses ``Decimal`` internally to
       avoid float conversion and enforces hosted precision and negativity
       settings without exposing ``Decimal``. Local filters omit ``starts_with``.
   * - ``rating``
     - Maximum value, color, style, and bounded integer validation.
     - Numeric value.
     - Integer from zero through ``max_value``; ``None`` is rejected.
     - Partial
     - RowValue delegates to field validation. Hosted ``baserow.io`` rejected a
       ``null`` write on 2026-09-01. Local filters omit inclusive comparisons
       present in generated documentation.
   * - ``date``
     - Date-only versus datetime, display format, 12/24-hour display, timezone
       display, and forced timezone metadata.
     - ISO date or datetime ``str``; explicit field helpers convert to ``date``
       or timezone-aware ``datetime`` and format using field metadata.
     - Strict ISO strings, the corresponding Python ``date`` or aware
       ``datetime``, or ``None``. Encoding never invents missing date, time, or
       timezone information.
     - Partial
     - Phase 2 removed two-digit-year guessing, slash normalization, implicit
       midnight, local-machine display timezone, and unjustified ``Z`` handling.
       Hosted ``baserow.io`` accepted a non-UTC ISO offset and returned canonical
       UTC ``Z`` form on 2026-09-01. New ``date_is*`` filters remain missing
       while deprecated operators dominate the local list.
   * - ``created_on``
     - Computed timestamp and date display metadata.
     - ISO date or datetime ``str`` with date helpers.
     - Read-only; setter raises.
     - Partial
     - Read-only handling is valuable. Tests only check presence, not timestamp
       shape or field settings.
   * - ``last_modified``
     - Computed timestamp and date display metadata.
     - ISO date or datetime ``str`` with date helpers.
     - Read-only; setter raises.
     - Partial
     - Same semantic family as ``date`` and ``created_on``; a separate RowValue
       class adds little beyond the read-only setter.
   * - ``url``
     - URL field identity and Baserow filters.
     - ``str`` or ``None``.
     - Any ``str`` or ``None``; URL form is not checked locally.
     - Partial
     - Baserow validates URL form, while the package only guarantees a string.
       Local filters omit ``starts_with``.
   * - ``email``
     - Email field identity and Baserow filters.
     - ``str`` or ``None``.
     - Any ``str`` or ``None``; email form is not checked locally.
     - Partial
     - Baserow validates email form, while the package only guarantees a string.
       Local filters omit ``starts_with``.
   * - ``phone_number``
     - Baserow's 100-character limit and permitted character set.
     - ``str``.
     - Empty, ``None``, or a matching phone string.
     - Partial
     - The validator encodes real server knowledge. RowValue duplicates the
       validator. Local filters omit ``starts_with``.
   * - ``single_select``
     - Option IDs, labels, colors, read object shape, write-by-ID-or-label, and
       first-match label behavior.
     - ``SelectOption`` retaining ID, label, color, and raw metadata, or
       ``None``.
     - Option record, ID, label, returned option dictionary, or ``None``;
       identity-bearing forms encode to IDs.
     - Strong
     - The canonical option record preserves identity. ``resolve_option``
       optionally rejects missing or duplicate labels. Local filters omit
       ``starts_with``, ``single_select_is_any_of``, and
       ``single_select_is_none_of``.
   * - ``multiple_select``
     - Option metadata, read object list, and write-by-ID-or-label semantics.
     - List of ``SelectOption`` records retaining identity and raw metadata.
     - List of option records, IDs, labels, or returned dictionaries;
       comma-separated labels and empty lists follow hosted behavior.
     - Strong
     - Returned records round-trip by ID. Ordinary label writes retain hosted
       resolution behavior; the strict resolver rejects ambiguity on request.
   * - ``link_row``
     - Related table ID, reverse field ID, selection-view metadata, complete-set
       replacement semantics, empty-list clearing, and ID-or-primary-label writes.
     - List of ``LinkedRow`` records retaining table ID, row ID, display value,
       and raw metadata.
     - Linked-row records, returned dictionaries, single IDs/labels, lists, or
       comma-separated labels. Every update replaces the complete set.
     - Strong
     - ``get_linked_rows`` preserves IDs and honors the selection view.
       ``resolve_linked_row`` optionally rejects absent or ambiguous labels.
   * - ``file``
     - File object shape, upload endpoints, assignment after upload, public file
       URL, visible name, and size verification.
     - List of ``BaserowFile`` records retaining stored, visible, and original
       names plus returned metadata.
     - File records, returned dictionaries, stored filename forms, empty lists,
       or ``None``. Upload methods return unattached records.
     - Strong
     - Client-level upload and explicit assignment separate the two Baserow
       operations. Generic downloading is outside the semantic core. Local
       filters omit ``files_lower_than``.
   * - ``formula``
     - Formula text, result type, array result type, error, and read-only status.
     - Raw server value; the configured button is a ``label``/``url`` object.
     - Read-only.
     - Partial
     - The configured ``formula_type="button"`` result remains lossless and
       raw because no equivalent writable field exists. Other observed scalar
       formula types preserve the corresponding ordinary scalar representation.
   * - ``count``
     - Link-through metadata, numeric formula result, and read-only status.
     - Baserow decimal string through number-result semantics.
     - Read-only.
     - Partial
     - It reuses ``NumberField`` behavior and the complete configured filter
       list while remaining unconditionally read-only.
   * - ``lookup``
     - Link field, target field, array result metadata, row IDs, values, and
       read-only status.
     - List of ``LookupEntry`` records retaining row ID, raw entry, and an
       text inner value; unknown inner result shapes remain raw.
     - Read-only.
     - Partial
     - ``formula_type`` and ``array_formula_type`` are exposed. The configured
       text result uses ordinary text semantics; unobserved target result
       families remain raw rather than being guessed.
   * - ``multiple_collaborators``
     - Notification metadata, collaborator object shape, and collaborator
       filters.
     - List of ``Collaborator`` records retaining ID and returned metadata.
     - List of collaborator records or returned dictionaries; both encode to
       ``{"id": ...}`` objects.
     - Partial
     - Identity is preserved offline, but a non-empty hosted collaborator read
       and the complete documented write surface still need verification.
   * - ``password``
     - Write-only secret behavior: server reads are ``null`` or ``true`` and a
       string write sets the password.
     - Boolean indicating whether the raw value is non-``None``.
     - ``str``, ``None``, or literal ``True`` pass local validation.
     - Partial
     - The asymmetry is important, but accepting ``True`` for writes is not
       justified by generated API documentation. The RowValue contains unused
       state and would report a raw ``False`` as set.
   * - ``uuid``
     - Read-only unique persistent identifier.
     - UUID string, with an explicit ``parse_value`` helper returning
       ``uuid.UUID``.
     - Unconditionally read-only.
     - Strong
     - Dedicated metadata, equality-filter knowledge, and lossless string reads
       match the hosted field observed on 2026-09-02.
   * - ``autonumber``
     - Read-only monotonically assigned row number.
     - Hosted integer value without conversion.
     - Unconditionally read-only.
     - Strong
     - Dedicated metadata and configured comparison-filter knowledge preserve
       the hosted integer representation observed on 2026-09-02.
   * - Other unknown API type
     - Original type string and arbitrary metadata are retained.
     - Raw server value.
     - Passed through if Baserow metadata does not mark the field read-only.
     - Fallback
     - This behavior is necessary because hosted Baserow changes independently
       of the package. Unknown writes should be explicitly documented as
       unvalidated rather than appearing fully supported.

Known field-category gaps
-------------------------

Baserow's current field overview lists these categories in addition to those
above. Their exact API type strings and wire representations have not been
verified against the configured database, so display names must not be used as
implementation keys without further evidence.

.. list-table::
   :header-rows: 1
   :widths: 21 18 25 36

   * - Baserow category
     - Expected character
     - Current handling
     - Evidence needed before implementation
   * - Duration
     - Writable scalar with display-unit settings.
     - Generic fallback if encountered.
     - API type string, raw and write units, precision, metadata, and filters.
   * - Rollup
     - Read-only computed scalar whose type depends on aggregation and target.
     - Generic fallback if encountered.
     - API type string, aggregation metadata, result types, null/error forms,
       and result-dependent filters.
   * - Created by
     - Read-only collaborator-like value.
     - Generic fallback if encountered.
     - API type string, returned user object, visibility rules, and filters.
   * - Last modified by
     - Read-only collaborator-like value.
     - Generic fallback if encountered.
     - API type string, returned user object, visibility rules, and filters.
   * - AI prompt
     - Computed or asynchronously populated value.
     - Generic fallback if encountered.
     - Availability, API type, result and error states, mutability, and whether
       database-token use has additional restrictions.
   * - Edit row link
     - Generated action/link value.
     - Generic fallback if encountered.
     - API type, returned representation, token/access behavior, and whether it
       belongs in a data client rather than an administrative client.

Test coverage inventory
-----------------------

The suite now combines credential-free characterization tests with hosted
``baserow.io`` integration tests. A passing create test proves that the server
accepts the supplied payload; it does not prove that the local field encoder was
used because ``add_rows`` still bypasses that encoder.

.. list-table::
   :header-rows: 1
   :widths: 25 28 47

   * - Coverage
     - Fields
     - Missing assurance
   * - Create and returned value
     - Text, long text, boolean, number, rating, three date configurations, URL,
       email, empty file, selects, phone, empty links, empty collaborators, and
       password.
     - Create still bypasses the encoder. Non-empty collaborators and hosted
       duplicate-label configurations remain unverified.
   * - Specialized operation
     - Date conversion/display, client file upload and upload-by-URL with
       explicit assignment, and linked-row discovery/update by ID.
     - Forced-timezone display, duplicate hosted primary labels, selection-view
       limits, and concurrent complete-set replacement remain unverified.
   * - Presence only
     - Created on and last modified.
     - Their hosted shapes and filter behavior still need focused assertions.
   * - Direct scalar field semantics
     - Text-like pass-through, boolean, rating, number, date/datetime, generic
       fallback, identity-bearing structured fields, Count, UUID, Autonumber,
       and the evidenced Formula/Lookup results.
     - Unobserved computed result families and create/update encoding parity
       remain for later evidence and Phase 5.

What should remain central
--------------------------

The inventory supports retaining and strengthening these responsibilities:

* database-token authentication, Baserow endpoints, pagination, and structured
  error interpretation;
* table discovery, schema retrieval, cached metadata, and an explicit schema
  refresh operation;
* one field semantic authority for decoding, validation, encoding, read-only
  status, and result-dependent behavior;
* row reads, singular and batch writes, movement, deletion, and uniform value
  encoding;
* query construction for Baserow filters, ordering, search, views, includes,
  excludes, and pagination;
* select-option and linked-row identity, including Baserow's ambiguous
  label-resolution rules;
* file upload and assignment; and
* forward-compatible raw access for field types the package does not yet know.

These responsibilities do not require a public custom field list, a public
custom row-value list, one RowValue subclass per Baserow type, global logging
configuration, or multiple public request-parsing helpers. ``Row`` convenience
methods can remain if they delegate to the same singular or batch primitives
and therefore preserve one semantic implementation.

Settled design decisions
------------------------

These decisions describe the intended contract for the refactor. Phase 2 scalar
semantics and Phase 3 identity-bearing values are implemented on
``release/0.2.0b1``; later sections remain design direction until their phase is
completed.

Focus and authority
~~~~~~~~~~~~~~~~~~~

``baserowapi`` will focus on the schema-aware database-token data API. It will
encode Baserow field, query, row, file, and error behavior without growing into
a complete administration SDK or a general HTTP framework.

Each Field will become the single semantic authority for decoding a Baserow
response, validating a supported input, encoding an API write, reporting
read-only status, exposing advisory filter knowledge, and interpreting computed
result metadata. Create, single-update, and batch-update operations will use the
same field encoder.

Scalar representations
~~~~~~~~~~~~~~~~~~~~~~

Ordinary reads will preserve Baserow scalar representations:

* Number values remain Baserow decimal strings, including significant trailing
  zeroes such as ``"42.00"``. Validation may use ``Decimal`` internally but will
  not expose ``Decimal`` as the row value.
* Date-only values remain ISO date strings and datetime values remain ISO
  timestamp strings.
* Explicit date helpers may parse date-only values to ``date`` and datetime
  values to timezone-aware ``datetime``. Display formatting is also explicit
  and may apply field metadata such as ``date_force_timezone``.
* Date writes accept ``None``, the appropriate Python ``date`` or timezone-aware
  ``datetime``, and strict ISO strings. The core path will not guess two-digit
  years, accept locale-dependent slash formats, assume midnight, append an
  unjustified ``Z``, or silently use the executing machine's timezone.

Documented inputs and validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The core client will accept every input representation documented by Baserow.
This includes IDs, labels, lists, comma-separated strings, and empty forms where
the relevant field documentation permits them. The package will document
Baserow's first-match behavior for ambiguous option labels and linked-row
primary values instead of imposing a narrower contract.

Optional strict helpers may resolve stable IDs and reject absent or ambiguous
labels. Local validation will enforce stable structural rules but will not use a
stale local compatibility matrix to block behavior accepted by the unpinned
hosted service. Convenience coercions not documented by Baserow must be
explicit, deterministic helpers rather than implicit core behavior.

Identity-bearing values
~~~~~~~~~~~~~~~~~~~~~~~

Reads will use small, lossless domain objects when Baserow identity or structure
would otherwise be discarded. Initial concepts include:

* a select option retaining ID, value, color, and raw metadata;
* a linked-row reference retaining row ID, display value, and raw metadata;
* a Baserow file retaining its server name, visible name, URL, size, MIME type
  when present, and raw metadata;
* a collaborator retaining user ID, available display information, and raw
  metadata; and
* a lookup entry retaining related row ID, decoded value, and raw metadata.

These will be independent value records, not a shared hierarchy or capability
framework. They will use ordinary Python collections, contain no HTTP behavior,
and remain suitable as write inputs. Scalar values will not be wrapped merely
for symmetry.

Selects, links, files, and collaborators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Select and link writes will accept both the lossless domain objects and every
documented Baserow representation. IDs or returned objects are the recommended
deterministic forms; labels and comma-separated strings retain Baserow's
documented resolution behavior. Strict lookup helpers live on the relevant
Field and reject ambiguity when requested.

Linked-row updates replace the complete relationship set. Empty lists clear the
relationship. Any add/remove convenience must make the resulting complete-set
write explicit and document that it cannot provide an atomic concurrent update
when the Baserow endpoint itself only replaces the set.

File upload will be a Client operation that returns an unattached Baserow file
object. Assignment to a row will be explicit, for example by passing the
returned object in a file-field update. Append and replace behavior will be
expressed by the list supplied to the row update rather than hidden RowValue
state. Generic downloading of public file URLs and recursive directory upload
do not belong in the semantic core; they may be separate utilities if retained.

Collaborator values will preserve identity and raw returned metadata. The data
client will assign documented collaborator values but will not take on user
invitations, permissions, or workspace administration.

Computed fields
~~~~~~~~~~~~~~~

Formula, lookup, count, rollup, and other computed fields will decode according
to result metadata such as ``formula_type`` and ``array_formula_type`` as well
as their declared field type. They will reuse the corresponding scalar or
identity-bearing representation. Count uses number semantics; computed dates
use date semantics; computed select or linked values preserve identity.

Computed fields remain read-only when their hosted metadata says so. Unknown
result types, including unverified button, AI, and error states, remain raw
until their representations are observed. The package will not collapse a
formula error or unfamiliar result into ``None``.

Unknown fields
~~~~~~~~~~~~~~

Unknown hosted field types are expected compatibility cases. Their original API
type and raw metadata remain inspectable. Reads return the raw value unchanged;
writes pass values through unchanged only when hosted metadata marks the field
writable. The package will not claim validation, formatting, or filter knowledge
for an unknown type. Unknown types will not produce a warning for every field
and row. The existing generic fallback may remain as a compatibility alias while
the public concept is clarified.

Filters
~~~~~~~

Normal filter validation covers stable query structure and does not enforce the
compatibility lists. Operator names and values pass through to Baserow.
``FilterCompatibility`` reports ``supported``, ``unsupported``, or ``unknown``
as advisory package knowledge.

The JSON filter-tree representation used by row queries is authoritative. The
detached ``FilterValidator`` and unused legacy ``Filter.query_string`` have been
removed. Recursive groups will be supported only to the extent verified in
current Baserow documentation and hosted behavior.

Rows, containers, and transport
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Table.fields`` will become an ordered read-only mapping from field name to
Field. ``FieldList`` and ``RowValueList`` will not remain public abstractions.
Row access will return values decoded by the Field, with explicit access to the
original raw value when needed. Per-type RowValue classes will be removed after
their behavior has moved to Fields and domain records.

Explicit ``row.update({...})`` is the preferred persistence operation. The
current staged ``row[name] = value; row.update()`` behavior should be removed or
modeled explicitly rather than allowing raw and decoded state to diverge. Row
operation conveniences may remain as thin delegates to the same Table
primitives used for singular and batch requests.

The Client will retain one request boundary for authentication, timeouts,
connectivity, HTTP failures, JSON parsing, and Baserow error extraction. Logging
configuration, header combination, request execution, and response parsing will
be private implementation details. A documented low-level ``request`` escape
hatch will remain public for hosted endpoints not yet modeled by the package;
it provides transport and error handling, not schema semantics or endpoint
stability. Mutating requests will not be retried without an idempotency
guarantee.

Evidence still required
-----------------------

The design direction is settled, but implementation still requires evidence
for several hosted representations:

* non-empty collaborator reads and every documented collaborator write form;
* exact API types, metadata, read values, write values, and filters for Duration,
  Rollup, Created by, Last modified by, AI prompt, and Edit row link;
* formula and rollup values for each result family, including per-field and
  per-cell error states;
* lookup entries whose target is not text;
* current nested filter-group limits and serialization; and
* duplicate select labels and linked primary values, selection-view limits, and
  complete-set replacement behavior.

Do not invent an API type string, result shape, or validation rule to fill these
gaps. Add a live field to the disposable test database, inspect the generated
documentation and response, record sanitized fixtures, and describe hosted
compatibility by verification date.

The implementation sequence and phase exit criteria are recorded in
:doc:`refactoring_plan`.
