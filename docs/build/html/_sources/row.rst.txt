Row class
==========

These examples show how to work with Row objects.
Rows 

Note that the .update() function always sends changes to the server.
Using the direct setter (single_row['Notes'] = "Changed note in memory") changes values in memory.

.. code-block:: python

    from baserowapi import Baserow, Filter

    baserow = Baserow(token='mytoken')

    # create table instance
    table = baserow.get_table(1234567)

    # get a row
    single_row = table.get_row(1)

    # change value for in-memory Row value
    # use update in order to save to server
    single_row['Notes'] = "Changed note in memory"

    # row content of all fields as a dict
    print(single_row.content)

    # access row value
    print(single_row['Notes'])

    # save Row with current row values to server
    updated_row = single_row.update()

    # update Row with dictionary
    # changes in-memory and saves row to server
    updated_row = single_row.update({'Notes': 'Updated row via dictionary'})

    # move row before row 4
    single_row.move_row(before_id=4)

    # move row to the end
    single_row.move_row()

    # delete row
    deleted_status = single_row.delete()
