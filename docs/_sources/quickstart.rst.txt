Quick Start with Baserow API
============================

Installation
------------

.. code-block:: bash

    pip install baserowapi

Basic operations
----------------

.. code-block:: python

    from baserowapi import Baserow

    baserow = Baserow(url="https://api.baserow.io", token="mytoken")
    table = baserow.get_table(1234567)

    for discovered in baserow.get_tables():
        print(discovered.id, discovered.name)

    print(table.field_names)
    print(table.fields["Name"])

    row = table.get_row(1)
    print(row["Name"])
    print(row.to_dict())

    # Decoded and raw Baserow values are both read-only mappings.
    print(row.values)
    print(row.raw_values)

    for result in table.get_rows():
        print(result.to_dict())

    updated_row = row.update({"Notes": "Updated on the server"})
    deleted = updated_row.delete()

Rows do not stage item assignment. Supply every change explicitly to
``row.update(values)`` or ``table.update_row(row_id, values)``.
