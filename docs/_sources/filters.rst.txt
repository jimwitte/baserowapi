Working with Filters in Baserow API
===================================

When querying rows using Baserow API, filters play a pivotal role in refining your search. The `.get_rows()` function of the table class supports the use of Filter objects to fine-tune your queries.

Filter Basics
-------------

A filter is composed of three elements:

- Field: The field name you're looking to filter on.
- Value: The value you're comparing against.
- Operator: Specifies the type of comparison (e.g., equal, contains_not, etc.). If omitted, 'equal' is the default.

Field Type and Filter Operators
-------------------------------

Each field type in Baserow supports specific filter operators. It's crucial to use compatible filter operators for accurate results:

- You can determine the list of compatible operators for a field by querying the `compatible_filters` property of the field.
- Additionally, the official Baserow API documentation provides a comprehensive list of these compatible filters.

Working with Filters: Examples
------------------------------

Here are some Python code examples to help you get started with filters:

.. code-block:: python

    from baserowapi import Baserow, Filter

    # Initialize the Baserow client
    baserow = Baserow(token='mytoken')

    # Create a table instance
    table = baserow.get_table(1234567)

    # Discover valid filter operators for the 'Name' field
    valid_operators = table.fields['Name'].compatible_filters
    print(f"Valid operators for 'Name' field: {valid_operators}")

    # Create a filter where the 'Name' field equals 'Grace'
    name_equal_grace = Filter("Name", "Grace")

    # Fetch rows that match the filter
    rows_with_name_grace = table.get_rows(filters=[name_equal_grace])
    for row in rows_with_name_grace:
        print(row.content)

    # Create and use a filter where the 'Name' field does not contain the letter 'A'
    name_contains_not_A = Filter("Name", "A", 'contains_not')
    rows_not_containing_A = table.get_rows(filters=[name_contains_not_A])
    for row in rows_not_containing_A:
        print(row.content)

