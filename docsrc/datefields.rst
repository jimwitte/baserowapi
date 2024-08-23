Working with Date Fields in Baserow API
=======================================

The Baserow API provides a convenient way to work with date fields. When working with dates, you might need to retrieve them, format them according to certain settings, or even modify them. This guide provides a comprehensive overview of how to achieve these tasks.

Setting Up
----------

Start by initializing the Baserow client and getting a table instance:

.. code-block:: python

    from baserowapi import Baserow

    # Initialize the Baserow client
    baserow = Baserow(url='https://api.baserow.io', token='mytoken')
    table = baserow.get_table(1234567)

Accessing Date Field Settings
-----------------------------

Every date field in Baserow has associated settings, which can be accessed from the field object:

.. code-block:: python

    print(table.fields['myDate'].date_format)

Fetching and Formatting Dates
-----------------------------

Baserow stores date values as UTC strings. You can retrieve these values directly or as Python datetime objects:

.. code-block:: python

    # Retrieve the date as a string
    myRow = table.get_row(1)
    print(myRow['myDate'])

    # Note that the value returned by the API is not formatted according to the field settings.
    '2024-08-15' # if table.fields['myDate'].date_include_time == false
    '2024-08-15T18:00:00Z' # if table.fields['myDate'].date_include_time == true

    # Convert the date into a Python datetime object
    print(myRow.values['myDate'].as_datetime())

    # Fetch the date as a formatted string based on the field's settings
    print(myRow.values['myDate'].formatted_date)

Updating Date Values
--------------------

Dates can be updated using strings. 

.. code-block:: python

    # Update the date value using a UTC string
    myRow['myDate'] = '2023-10-02T18:38:45Z'

    # Update the date value using a bare date string
    myRow['myDate'] = '2023-10-02'

    # Update the date value 

    # Manipulate the date using Python's datetime library
    import datetime
    from datetime import timedelta

    field_date = myRow.values['myDate'].as_datetime()

    # Add one day to the date
    new_date = field_date + timedelta(days=1)
    print(new_date)

    # Update the row with the new date value
    myRow['myDate'] = new_date
    myRow.update()

