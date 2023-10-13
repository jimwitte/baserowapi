Quick Start
=============

Installation
-------------

.. code-block:: python

    pip install baserowapi

Basic Operations
----------------

.. code-block:: python

    from baserowapi import Baserow, Filter

    # baserow client
    baserow = Baserow(url='https://api.baserow.io',token='mytoken')

    # create table instance
    table = baserow.get_table(1234567)

    # get list of field names for table
    print(table.field_names)

    # get row by id
    my_row = table.get_row(1)

    # dictionary of field names and values for row
    print(my_row.content)

    # access value for specific field
    print(my_row['Name'])

    # get all rows as RowIterator object
    # iterator handles paging as items are accessed
    all_my_rows = table.get_rows()
    for row in all_my_rows:
        print(row)

    # change value for in-memory Row object
    single_row['Notes'] = "Changed note in memory"
    print(single_row['Notes'])

    # save Row with current row values to server
    updated_row = single_row.update()
    print(updated_row.content)

    # update Row with dictionary
    # saves row to server
    updated_row = single_row.update({'Notes': 'Updated row via dictionary'})

    # delete single row
    deleted_status = added_row.delete()
