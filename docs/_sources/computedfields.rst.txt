Computed and Generated Fields
=============================

Formula, Count, Lookup, UUID, and Autonumber fields are read-only. Row creation
and every update path exclude them from API payloads.

Formula Results
---------------

``FormulaField`` exposes ``formula_type``, ``array_formula_type``, and the
field-level ``error`` metadata. Ordinary scalar results retain the same Python
representation as their writable equivalents. Result families without an
observed writable equivalent remain raw and lossless. For example, the hosted
button field verified for ``0.2.0b1`` returns its object unchanged:

.. code-block:: python

    {'label': 'Baserow Home', 'url': 'https://baserow.io'}

Unknown result and error shapes are not collapsed into ``None``.

Count and Lookup
----------------

Count uses number-result semantics, so ordinary reads preserve Baserow's
decimal string, such as ``"0"``. A Lookup reads as ``LookupEntry`` records.
Each entry retains its related row ID and raw metadata. The configured text
lookup exposes an ordinary string as ``entry.value``; unobserved inner result
types remain raw.

UUID and Autonumber
-------------------

UUID reads preserve Baserow's string. ``UUIDField.parse_value()`` provides an
explicit conversion to ``uuid.UUID`` when needed. Autonumber preserves the
integer returned by hosted Baserow. Both fields expose verified filter
compatibility and are unconditionally read-only.
