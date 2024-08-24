Row Class
=========

The ``Row`` class represents individual rows within a Baserow table. This class provides methods for manipulating the data of a single row and for interacting with the server for CRUD operations. Below is a detailed guide on how to work with the ``Row`` objects.

**Key Points**:
- The ``update()`` method communicates and synchronizes changes with the server.
- Using direct setters (e.g., ``single_row['Notes'] = "Changed note in memory"``) will only alter values in the memory, and not immediately update them on the server.

Methods and Usage
-----------------

.. code-block:: python

    from baserowapi import Baserow

    baserow = Baserow(token='mytoken')

    # Initializing a table instance
    table = baserow.get_table(1234567)

    # Retrieving a single row by id
    single_row = table.get_row(1)

    # Modifying an in-memory Row value
    single_row['Notes'] = "Changed note in memory"

    # Displaying row content of all fields as a dictionary
    print(single_row.to_dict())

    # Accessing a specific row value
    print(single_row['Notes'])

    # Synchronizing the current row values with the server
    updated_row = single_row.update()

    # Updating a Row using a dictionary and saving changes to the server
    updated_row = single_row.update({'Notes': 'Updated row via dictionary'})

    # Reordering a row to be placed before another row (specified by ID)
    single_row.move_row(before_id=4)

    # Moving a row to the end of the table
    single_row.move_row()

    # Deleting the row
    deleted_status = single_row.delete()

