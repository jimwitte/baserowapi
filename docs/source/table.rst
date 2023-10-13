Table class
============

These examples show properties and functions of the table class.

The baserow API returns paged results (by default 100 rows per page) when using the .get_rows() function. 
This function returns an iterator that you can loop through, and the iterator will handle the paging for you.


.. code-block:: python

    from baserowapi import Baserow, Filter

    baserow = Baserow(token='mytoken')

    # create table instance
    table = baserow.get_table(1234567)

    # table properties
    print(table.id)
    print(table.primary_field)

    # table fields (columns) properties
    print(table.fields['Name'])
    print(table.fields['Name'].order)
    print(table.fields['Name'].field_data)

    # get list of field names for table
    print(table.field_names)

    # get a single row by id
    my_row = table.get_row(1)

    # get all rows as row iterator object
    all_rows = table.get_rows()

    # loop through the iterator, it handles paging as needed
    for row in all_rows:
        print(row['Name'])

    # get rows as list object, forces paging until all rows are fetched
    all_my_rows_as_list = list(table.get_rows())

    # get rows with filter, implied equal operator
    rows_with_name_grace = table.get_rows(filters=[Filter("Name", "Grace")])
    for row in rows_with_name_grace:
        print(row.content)

    # get rows with multiple filters on same field, OR
    rows_with_name_ada_or_grace = table.get_rows(filters=[Filter("Name", "Ada"), Filter("Name", "Grace")], filter_type='OR')
    for row in rows_with_name_ada_or_grace:
        print(row.content)

    # get rows sorted ascending by field
    rows_name_ascending = table.get_rows(order_by=["Name"])
    for row in rows_name_ascending:
        print(row.content)

    # get rows sorted descending by field
    rows = table.get_rows(order_by=["-Name"])
    for row in rows:
        print(row.content)

    # get rows with search
    rows_with_test = table.get_rows(search="test")
    for row in rows_with_test:
        print(row.content)

    # get rows as view
    rows_from_view = table.get_rows(view_id=12345678)
    for row in rows_from_view:
        print(row.content)

    # get rows, limited to included fields
    rows_with_include = table.get_rows(include=['Name','Last name', 'Notes', 'Active'])
    for row in rows_with_include:
        print(row.content)

    # get rows exclude fields
    rows_with_exclude = table.get_rows(exclude=['Notes','Active'])
    for row in rows_with_exclude:
        print(row.content)

    # add new row from dictionary
    new_row_data = {
        'Name': 'Ringo',
        'Last name': 'Staar',
        'Notes': 'drums',
        'Active': True
    }
    added_row = table.add_row(new_row_data)
    print(added_row.content)

    # add multiple rows from list of dictionaries
    # uses 'batch' api endpoint
    add_multiple_row_data = [
        {
            'Name': 'Nick',
            'Last name': 'Saban',
            'Notes': 'Head coach of Alabama Crimson Tide',
            'Active': True
        },
        {
            'Name': 'Dabo',
            'Last name': 'Swinney',
            'Notes': 'Head coach of Clemson Tigers',
            'Active': True
        },
        {
            'Name': 'Urban',
            'Last name': 'Meyer',
            'Notes': 'Former head coach of Ohio State Buckeyes',
            'Active': False
        }
    ]

    added_rows = table.add_row(add_multiple_row_data)
    for row in added_rows:
        print(row.content)

    # delete multiple rows
    # uses batch delete api endpoint
    deleted_status = table.delete_rows(added_rows)
    print(deleted_status)

    # delete multiple rows using list of ids
    re_added_rows = table.add_row(add_multiple_row_data)
    rows_to_delete = []
    for row in re_added_rows:
        rows_to_delete.append(row.id)
    delete_status = table.delete_rows(rows_to_delete)

    # update multiple rows from dictionary
    # uses batch update api endpoint
    update_rows_data = [
        {"id": 3, "Notes": "dict update test"},
        {"id": 4, "Notes": "dict update test"},
        {"id": 5, "Notes": "dict update test"}
    ]
    updated_rows = table.update_rows(update_rows_data)
    for row in updated_rows:
        print(row.content)

    # update multiple rows from Row objects
    my_rows = list(table.get_rows(filters=[Filter("Notes", "dict update test")]))
    for row in my_rows:
        row.update(values={'Notes': 'Row object update test'}, memory_only=True)
        print(row.content)

    updated_rows = table.update_rows(my_rows)
    for row in updated_rows:
        print(row.content)

    # return first row from results as Row object
    single_row = table.get_rows(return_single=True)
