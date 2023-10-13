Working with filters
=====================

When fetching rows using the .get_rows() function of the table class, 
you can pass Filter objects.

A filter consists of a field, a value, and an operator. If no operator is specified, 'equal' is the default.

Each field type is compatible with specific filter operators. You can query the table field 'compatible_filters' property to discover compatible operators.
Compatible filters are also listed in the baserow api documentation.


.. code-block:: python

    from baserowapi import Baserow, Filter

    baserow = Baserow(token='mytoken')

    # create table instance
    table = baserow.get_table(1234567)

    # find compatible filter operators for 'Name' field
    valid_operators = table.fields['Name'].compatible_filters

    # filter object implied equal
    name_equal_grace = Filter("Name", "Grace")

    # contains_not filter
    name_contains_not_A = Filter("Name", "A", 'contains_not')

    # get rows with equal filter
    rows_with_name_grace = table.get_rows(filters=[name_equal_grace])
    for row in rows_with_name_grace:
        print(row.content)

    # get rows with contains_not filter
    rows_not_containing_A = table.get_rows(filters=[Filter("Name", "A", 'contains_not')])
    for row in rows_not_containing_A:
        print(row.content)

