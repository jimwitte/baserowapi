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

- **RowValue Objects**: Representing the value for a particular field in a specified row, RowValues can be accessed or modified using setters and getters. Additional methods provided in the Row class include deleting, updating, and moving rows. For batch operations on rows, consider using methods from the table object.

Note: Some `RowValue` objects offer utility functions. For instance, there are methods for converting date values into datetime objects or for uploading and downloading files for a file field value.

Filter Objects
--------------

Designed for use with the `table.get_rows()` function. Filters can be initiated independently from tables. On application, each filter is validated against the table field to ensure the existence of a compatible field with the correct name.


