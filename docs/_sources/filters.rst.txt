Working with Filters
====================

``Table.get_rows()`` sends Baserow's JSON filter-tree representation. A
``Filter`` contains a non-empty field name and operator plus the value Baserow
should compare. Operator names and values are sent to the hosted service without
a static client-side compatibility gate.

.. code-block:: python

    from baserowapi import Baserow, Filter

    baserow = Baserow(token='mytoken')
    table = baserow.get_table(1234567)

    rows = table.get_rows(
        filters=[Filter('Name', 'Grace', 'equal')],
        filter_type='AND',
    )

Compatibility Knowledge
-----------------------

Field metadata does not include a complete, stable compatibility matrix, and
hosted ``baserow.io`` is not version-pinned. Each Field therefore reports the
package's current knowledge as advisory information:

.. code-block:: python

    from baserowapi import FilterCompatibility

    status = table.fields['Name'].filter_compatibility('starts_with')
    if status is FilterCompatibility.SUPPORTED:
        print('documented for this field')

The possible results are:

``SUPPORTED``
   The operator is documented for this field in the package's verified
   compatibility data.

``UNSUPPORTED``
   The operator is known to Baserow but is not documented for this field.
   This is advisory and does not block a query.

``UNKNOWN``
   The operator or field type is not known locally. The query may still be
   accepted by a newer hosted service.

Unknown operators remain valid ``Filter`` inputs and are sent to Baserow. This
forward-compatible path is intentional. Baserow remains authoritative for the
result of a live query.

Migration from 0.1
------------------

The detached ``FilterValidator`` and the unused ``Filter.query_string``
property were removed in ``0.2.0b1``. Use ``field.filter_compatibility()`` for
advisory discovery and pass ``Filter`` objects to ``Table.get_rows()`` for the
single supported JSON-tree encoding.
