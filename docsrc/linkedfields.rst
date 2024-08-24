Working with Linked Fields in Baserow API
=========================================

Linked fields in Baserow allow you to associate rows from one table with rows in another table. Understanding how to work with these fields can greatly enhance your data relations and queries.

Basics of Linked Fields
-----------------------

A linked field has several properties and functions that provide information about the relationship it establishes:

- `link_row_table_id`: The ID of the table that the linked field points to.
- `link_row_related_field_id`: The ID of the related field in the linked table.
- `link_row_limit_selection_view_id`: The ID of a view limiting options in the linked table.
- `get_options()`: Returns list of valid values from primary field of linked table.


Working with Linked Fields: Examples
------------------------------------

Here are some Python code examples to help you work with linked fields:

.. code-block:: python


    # For the sake of this example, assume you've fetched a specific row
    db = Baserow(
        url=BASEROW_URL, token=BASEROW_TOKEN
    )

    table = db.get_table(123456)

    single_row = table.get_row(1)

    # Retrieve the linked table ID from the linked field
    linked_table_id = table.fields['myTableLink'].link_row_table_id
    print(f"Linked Table ID: {linked_table_id}")

    # Obtain list of the valid options for linked field values
    options = table.fields['myTableLink'].get_options()
    print(f"Valid Options: {options}")

    # Obtain the ID of the field in the related table
    linked_field_id = table.fields['myTableLink'].link_row_related_field_id

    # Obtain the ID of the view limiting the selection options
    limit_selection_view_id = table.fields['myTableLink'].link_row_limit_selection_view_id

    # Access the related table object - this can be useful for various operations like searching or filtering rows to link
    related_table = table.get_table(linked_table_id)
    print(f"Related Table: {related_table}")

    # Retrieve all rows from the related table. Could add filters if needed.
    related_rows = related_table.get_rows()

    # Set the in-memory value of the linked field to the first two valid options
    single_row['myTableLink'] = options[:2]

    # Finally, update the row to persist the changes to the server
    single_row.update()

