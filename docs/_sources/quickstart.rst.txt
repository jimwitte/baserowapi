Quick Start with Baserow API
============================

Welcome to the Quick Start guide for the Baserow API! Follow the steps below to swiftly get up and running with basic operations.

Installation
------------

To start with, install the Baserow API Python package:

.. code-block:: bash

    pip install baserowapi

Begin with Basic Operations
---------------------------

After installation, you can perform basic operations such as fetching tables, reading rows, and manipulating data.

.. code-block:: python

    from baserowapi import Baserow

    # Initialize the Baserow client
    baserow = Baserow(url='https://api.baserow.io', token='mytoken')

    # Create a table instance using its ID
    table = baserow.get_table(1234567)

    # Print a list of field names in the table
    print(table.field_names)

    # Fetch a row using its ID
    my_row = table.get_row(1)
    # Display a dictionary of field names and their values for this row
    print(my_row.content)

    # Access a specific field's value in the row
    print(my_row['Name'])

    # Retrieve all rows in the table. Note: The RowIterator object automatically handles pagination.
    all_my_rows = table.get_rows()
    for row in all_my_rows:
        print(row)

    # Modify an in-memory value of the Row object
    my_row['Notes'] = "Changed note in memory"
    print(my_row['Notes'])

    # Synchronize changes made in memory to the server
    updated_row = my_row.update()
    print(updated_row.content)

    # Update a Row's content using a dictionary and save to the server
    updated_row = my_row.update({'Notes': 'Updated row via dictionary'})

    # Delete a single row
    deleted_status = updated_row.delete()

