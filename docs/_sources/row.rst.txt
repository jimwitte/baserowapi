Row Class
=========

``Row`` represents one Baserow row. It provides field access and thin
conveniences for updating, moving, and deleting that row.

Reading values
--------------

Indexing a row returns the value decoded by its Field. ``values`` exposes all
decoded values as an ordered, read-only mapping. ``raw_values`` exposes the
original values returned by Baserow, which is useful for forward compatibility
and inspecting unfamiliar field types. ``to_dict()`` returns a mutable,
top-level copy of the decoded values.

.. code-block:: python

    row = table.get_row(1)

    print(row["Notes"])
    print(row.values)
    print(row.raw_values)

    values = row.to_dict()
    values["Notes"] = "This changes only the copied dictionary"

Rows do not stage mutations. Item assignment is unsupported, so raw, decoded,
and pending state cannot silently diverge.

Updating and deleting
---------------------

Pass an explicit mapping to ``update``. The method returns the server's updated
``Row`` and refreshes the existing object's response data.

.. code-block:: python

    updated_row = row.update({"Notes": "Updated on the server"})

    # Place the row before row 4, or omit before_id to move it to the end.
    moved_row = row.move(before_id=4)
    moved_to_end = row.move()

    deleted = row.delete()

For multiple rows, use ``Table.update_rows`` with a list of mappings containing
explicit ``id`` values. Batch updates do not accept ``Row`` objects.

Migration from 0.1
------------------

Replace staged assignment and a no-argument update with one explicit update:

.. code-block:: python

    # 0.1
    row["Notes"] = "Updated"
    updated_row = row.update()

    # 0.2
    updated_row = row.update({"Notes": "Updated"})

Code that previously navigated ``RowValue`` objects should use the decoded
mapping, raw mapping, or the corresponding Field helper directly.
