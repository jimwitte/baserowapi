Working with Date Fields in Baserow API
=======================================

Baserow date fields expose both wire values and display metadata. Ordinary row
access preserves the wire representation: date-only values remain ISO date
strings and datetime values remain ISO timestamp strings. Conversion to Python
objects and display formatting are explicit operations on the field.

Accessing field settings
------------------------

The field metadata distinguishes date-only values from datetimes and describes
Baserow's display configuration:

.. code-block:: python

    field = table.fields["Due date"]
    print(field.date_include_time)
    print(field.date_format)
    print(field.date_time_format)
    print(field.date_show_tzinfo)
    print(field.date_force_timezone)

Reading and parsing values
--------------------------

Row access returns the Baserow value unchanged:

.. code-block:: python

    row = table.get_row(1)
    raw_value = row["Due date"]
    # "2026-09-01" for a date-only field
    # "2026-09-01T12:30:00Z" for a datetime field

Use ``parse_value`` when a Python object is useful. It returns ``date`` for a
date-only field and a timezone-aware ``datetime`` for a datetime field:

.. code-block:: python

    parsed_value = field.parse_value(raw_value)

Formatting for display
----------------------

``format_value`` applies the field's date format, time format, timezone display,
and forced-timezone metadata:

.. code-block:: python

    display_value = field.format_value(raw_value)

    # An explicit display timezone overrides date_force_timezone.
    local_display = field.format_value(
        raw_value,
        target_timezone="America/Chicago",
    )

If neither the caller nor the field specifies a display timezone, the helper
retains the timestamp's supplied offset. It does not use the executing
computer's local timezone implicitly.

Writing date values
-------------------

Date-only fields accept ``None``, a Python ``date``, or a complete ISO date
string in ``YYYY-MM-DD`` form. Datetime fields accept ``None``, a timezone-aware
Python ``datetime``, or a complete ISO timestamp with an explicit offset or
``Z`` suffix.

.. code-block:: python

    from datetime import date, datetime, timezone

    row.update({"Due date": date(2026, 9, 1)})
    row.update({"Meeting": "2026-09-01T12:30:00Z"})
    row.update(
        {"Meeting": datetime(2026, 9, 1, 12, 30, tzinfo=timezone.utc)}
    )

The client rejects incomplete or ambiguous values rather than guessing. It does
not expand two-digit years, normalize slash-separated dates, strip a time from a
date-only value, add midnight to a datetime field, assign a timezone to a naive
``datetime``, or append ``Z`` to an offset-free timestamp.
