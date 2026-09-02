Working with Linked Fields
==========================

A link-row field describes a complete relationship set. Updating the field
replaces that set; an empty list clears it. Returned values are
:class:`baserowapi.LinkedRow` records containing the linked ``table_id``, row
``id``, display ``value``, and complete returned metadata in ``raw``.

The field exposes Baserow relationship metadata through
``link_row_table_id``, ``link_row_related_field_id``, and
``link_row_limit_selection_view_id``. ``get_linked_rows()`` retrieves the rows
that may be selected, retaining their stable row IDs and honoring a configured
selection-limiting view.

.. code-block:: python

    field = table.fields['Related']
    choices = field.get_linked_rows()

    for choice in choices:
        print(choice.id, choice.value)

    row = table.get_row(1)
    row.update({'Related': choices[:2]})

Writes also accept the Baserow-documented forms: one ID or primary-field label,
a returned linked-row object, a list of those values, or comma-separated
primary-field labels. Baserow performs ordinary label resolution. For code that
requires a unique match, ``field.resolve_linked_row(label)`` raises
``FieldValidationError`` when no selectable row or more than one selectable row
has that display value.

Do not model adding and removing links as atomic operations: the row endpoint
writes the complete relationship set.
