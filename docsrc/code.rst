Code Structure
==============

The Baserow API client library offers a structured approach to work with the Baserow database. The following provides an overview of the primary classes and their relationships.

Baserow Class
-------------

The main entrypoint for interacting with the library. This client class is in charge of making API calls. It is passed to other classes requiring API access. Notably, the Baserow class provides functionality to instantiate table objects.

Table Class
-----------

This class represents the tables in Baserow. Each table comprises various fields characterized by the following:

- **Fields Property**: A property that holds the value of a `FieldList` object, which encompasses various field objects corresponding to each field present in the table.

- **Field Objects**: All field objects possess properties such as `id`, `table_id`, `order`, `type`, `is_primary`, and `is_read_only`. Specific field types may have additional properties. If any alterations are made to table fields, it is recommended to re-instantiate the table object.

Row Class
---------

This class represents rows in a Baserow table, encompassing:

- **Values Property**: A property containing the value of a `RowValueList` object. The `RowValueList` embeds multiple `RowValue` objects, each correlating to a specific field object.

- **RowValue Objects**: Compatibility objects currently back each field value.
  Their decoding, validation, and encoding delegate to the associated Field.
  Additional methods on Row include deleting, updating, and moving rows. For
  batch operations, use the Table methods.

Date RowValues retain explicit parsing and display helpers for compatibility.
File upload is a Baserow client operation and returns an unattached file record;
row assignment is a separate explicit update.

Identity-bearing Values
-----------------------

Select options, linked rows, files, collaborators, and lookup results use small
independent records that preserve Baserow IDs and raw metadata. These records
contain no HTTP behavior and can be passed back to the corresponding writable
Field. Scalar reads remain ordinary Python values.

Filter Objects
--------------

Designed for use with the `table.get_rows()` function. Filters can be initiated independently from tables. On application, each filter is validated against the table field to ensure the existence of a compatible field with the correct name.

