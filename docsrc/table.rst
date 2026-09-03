Table Class
===========

The ``Table`` class provides an interface to interact with a Baserow table. Through this class, users can perform CRUD operations on rows, query table information, retrieve field properties, and utilize various filtering and sorting options. Below, we showcase the properties and methods available in the ``Table`` class along with examples of common use cases.

**Important Note**: Baserow returns paged row results. ``get_rows()`` follows
those pages and returns a list. Use ``iter_rows()`` to consume rows lazily.
Both methods require every page to contain a ``results`` list and a ``next``
URL or ``None``; malformed hosted responses raise ``RowFetchError``.
``view_id`` and ``size`` must be positive integers. ``limit`` must be a
non-negative integer; a zero limit returns no rows without contacting Baserow.
Boolean values are rejected for all three parameters.

Row write contracts
-------------------

Singular and plural writes are deliberately separate. ``add_row(values)`` and
``update_row(row_id, values)`` return one ``Row``. ``add_rows(rows)`` and
``update_rows(rows)`` accept non-empty lists and always return ``list[Row]``.
The plural methods no longer accept a single mapping. ``update_rows`` entries
must be mappings containing an explicit ``id``; Row objects are not accepted.

Every create and update passes supplied values through the corresponding
Field's validation and encoder. This gives a date, select option, linked-row
reference, file record, or unknown writable field the same wire representation
in singular and batch operations. Read-only and absent fields are rejected
before a request is sent.

Batch requests are processed sequentially and are not atomic across chunks. A
``RowAddError`` or ``RowUpdateError`` raised after an earlier chunk succeeded
exposes ``failed_batch_number``, ``completed_count``, and
``completed_row_ids``. The client does not automatically retry or roll back
mutating requests.

Deletion follows the same explicit split. ``delete_row(row_id)`` deletes one
row. ``delete_rows(row_ids)`` requires a non-empty list of row IDs, validates
the complete input before sending anything, and reports completed IDs through
``RowDeleteError`` if a later batch fails. ``move_row(row_id, before_id)``
moves one row before another, or to the end when ``before_id`` is omitted.
Both deletion endpoints must return HTTP 204 before the client confirms the
affected row IDs.

Properties
----------

- ``id``: Table's unique identifier.
- ``name``: Table name returned by discovery, or ``None`` when constructed by ID.
- ``database_id``: Parent database ID returned by discovery, when available.
- ``order``: Table order returned by discovery, when available.
- ``metadata``: Read-only mapping of the complete discovery metadata.
- ``primary_field``: The primary field of the table.
- ``fields``: Ordered, read-only mapping of field names to Field objects.
- ``writable_fields``: Ordered, read-only subset of fields accepted by writes.
- ``field_names``: List of field names present in the table.

Methods and Usage
-----------------

.. code-block:: python

    from baserowapi import Baserow, Filter

    baserow = Baserow(token='mytoken')

    # Initializing a table instance
    table = baserow.get_table(1234567)

    # Or discovering every table visible to the database token
    discovered_tables = baserow.get_tables()

    # Displaying table properties
    print(table.id)
    print(table.primary_field)

    # Accessing table fields properties
    print(table.fields['Name'])
    print(table.fields['Name'].order)
    print(table.fields['Name'].field_data)

    # Getting field names for the table
    print(table.field_names)

    # Fetching a single row by its ID
    my_row = table.get_row(1)

    # Fetching all rows, returns list
    for row in table.get_rows():
        print(row['Name'])

    # Streaming all rows (efficient for large datasets)
    for row in table.iter_rows():
        print(row['Name'])

    # Fetching rows with filters
    rows_with_name_grace = table.get_rows(filters=[Filter("Name", "Grace")])
    for row in rows_with_name_grace:
        print(row.to_dict())

    # Fetching rows using multiple filters (OR logic)
    rows_with_name_ada_or_grace = table.get_rows(filters=[Filter("Name", "Ada"), Filter("Name", "Grace")], filter_type='OR')
    for row in rows_with_name_ada_or_grace:
        print(row.to_dict())

    # Sorting rows
    rows_name_ascending = table.get_rows(order_by=["Name"])
    for row in rows_name_ascending:
        print(row.to_dict())

    # Fetching rows with a search term
    rows_with_test = table.get_rows(search="test")
    for row in rows_with_test:
        print(row.to_dict())

    # Fetching rows from a specific view
    rows_from_view = table.get_rows(view_id=12345678)
    for row in rows_from_view:
        print(row.to_dict())

    # Limiting fields in the fetched rows
    rows_with_include = table.get_rows(include=['Name','Last name', 'Notes', 'Active'])
    for row in rows_with_include:
        print(row.to_dict())

    # Excluding specific fields from the fetched rows
    rows_with_exclude = table.get_rows(exclude=['Notes','Active'])
    for row in rows_with_exclude:
        print(row.to_dict())

    # Limit number of rows fetched
    single_row = table.get_rows(limit=1)

    # Adding a new row
    new_row_data = {
        'Name': 'Ringo',
        'Last name': 'Staar',
        'Notes': 'drums',
        'Active': True
    }
    added_row = table.add_row(new_row_data)

    # Add multiple rows
    rows_data = [
        {"Name": "Alice", "Last name": "Smith", "Notes": "VIP customer", "Active": True},
        {"Name": "Bob", "Last name": "Johnson", "Notes": "Pending review", "Active": False},
    ]

    # Add the rows to the table
    added_rows = table.add_rows(rows_data)

    # Update one row
    updated_row = table.update_row(added_row.id, {'Notes': 'new note'})

    # Updating rows
    rows_data = [
        {"id": 1, "Notes": "Alice has a new order", "Active": True},
        {"id": 2, "Notes": "Bob's review completed", "Active": True},
    ]

    # Update the rows
    updated_rows = table.update_rows(rows_data)

    # Move one row before another
    moved_row = table.move_row(added_row.id, before_id=updated_rows[0].id)

    # Delete one row
    table.delete_row(moved_row.id)

    # Delete multiple rows
    row_ids = [1, 2]
    table.delete_rows(row_ids)

Migration from 0.1
------------------

``add_rows(mapping)`` previously accepted a single mapping but still returned
a one-element list. Use the explicit singular method instead:

.. code-block:: python

    # 0.1
    row = table.add_rows({'Name': 'Ada'})[0]

    # 0.2
    row = table.add_row({'Name': 'Ada'})

Plural calls continue to use a list and return a list. For direct table updates,
use ``update_row(row_id, values)`` for one row and ``update_rows(rows)`` for a
list. ``row.update(values)`` remains available and delegates to
``table.update_row``.

``Table.fields`` previously used a custom container whose iteration yielded
Field objects. It is now an ordinary read-only mapping, so iteration yields
field names and ``table.fields.values()`` yields Field objects.

Batch updates previously accepted Row objects. Pass explicit mappings instead:

.. code-block:: python

    # 0.1
    updated_rows = table.update_rows([row])

    # 0.2
    updated_rows = table.update_rows([
        {"id": row.id, "Notes": "Updated"},
    ])

Row retrieval no longer switches return types through ``iterator=True`` and
does not accept arbitrary query keyword arguments. Use the fixed methods:

.. code-block:: python

    # 0.1
    rows = table.get_rows(iterator=True)

    # 0.2
    rows = table.iter_rows()

Batch deletion similarly requires an explicit list of row IDs. Pass a single
ID to ``delete_row`` rather than passing a scalar, generator, or Row object to
``delete_rows``.
