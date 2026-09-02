Working with Select Fields
==========================

Select reads preserve the option identity returned by Baserow. A single-select
value is a :class:`baserowapi.SelectOption` or ``None``; a multiple-select value
is a list of ``SelectOption`` records. Each record exposes ``id``, ``value``,
``color``, and the complete returned metadata in ``raw``.

.. code-block:: python

    row = table.get_row(1)
    selected = row['Status']
    print(selected.id, selected.value, selected.color)

    for option in table.fields['Status'].options:
        print(option.id, option.value)

Writes accept the forms documented by Baserow. A single-select field accepts an
option ID, label, returned object, ``SelectOption``, or ``None``. A
multiple-select field accepts lists of IDs, labels, returned objects, or
``SelectOption`` records, as well as Baserow's comma-separated label form. Use
an empty list to clear a multiple-select field; baserow.io rejects ``None`` for
that operation.

.. code-block:: python

    row.update({'Status': selected})
    row.update({'Status': selected.id})
    row.update({'Status': 'Open'})
    row.update({'Tags': ['Urgent', 'Customer']})
    row.update({'Tags': 'Urgent, Customer'})
    row.update({'Tags': []})

Baserow resolves label writes. When code needs deterministic local resolution,
``field.resolve_option(label)`` returns the unique configured option and raises
``FieldValidationError`` if the label is missing or duplicated. Prefer an ID or
``SelectOption`` for writes that must remain unambiguous.
