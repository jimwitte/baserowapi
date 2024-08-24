Working with Single Select and Multiple Select Fields in Baserow API
=====================================================================

Baserow provides both single and multiple selection fields for your data tables, allowing you to define a set of predefined options and select one or multiple of them for each row. Understanding how to work with these fields can help streamline your data input and validation processes.

Basics of Selection Fields
--------------------------

**Single Select Fields**:

- Allows you to choose one option from a list of predefined values.
- If no option is chosen, the value can be set to `None`.

**Multiple Select Fields**:

- Allows you to choose multiple options from a list of predefined values.
- The values are represented as a list of chosen options.
- An empty list signifies no options have been selected.

Working with Selection Fields: Examples
---------------------------------------

.. code-block:: python

    # Fetch a specific row for this example
    single_row = table.get_row(1)

    # Retrieve available options for a select field
    my_options = table.fields['mySelectField'].options
    print(f"Available Options: {my_options}")

    # Set a specific option for a single select field in-memory
    single_row['mySelectField'] = 'option 1'

    # Deselect any option for the single select field
    single_row['mySelectField'] = None

    # For a multiple selection field, use a list to set multiple options
    single_row['myMultiSelectField'] = ['option 1', 'option 2']

    # Alternatively, update a multiple selection field with a dictionary and save changes to the server
    single_row.update(
        {'myMultiSelectField': ['option 1', 'option 2']}
    )

    # Set no options for a multiple selection field
    single_row['myMultiSelectField'] = []

    # Finally, persist changes to the server
    single_row.update()

