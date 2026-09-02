Code Structure
==============

The public workflow is ``Baserow`` to ``Table`` to ``Row``. Fields hold schema
knowledge, while a small set of independent records preserve identity for
structured Baserow values.

Baserow Class
-------------

``Baserow`` is the client and request boundary. It owns authentication,
transport errors, table construction, and file upload operations.

Table Class
-----------

``Table`` owns schema metadata and row operations. ``fields`` and
``writable_fields`` are ordered, read-only mappings from field name to Field.
Specific Field classes expose Baserow metadata and own decoding, validation,
and API encoding. Recreate the Table to retrieve changed hosted schema.

Row Class
---------

``Row`` holds one raw Baserow response and delegates value decoding to the
Table's Fields. Indexing and ``values`` expose decoded values; ``raw_values``
exposes the original Baserow values. Rows do not stage mutations. ``update``,
``move``, and ``delete`` are thin conveniences over Table operations.

Identity-bearing Values
-----------------------

Select options, linked rows, files, collaborators, and lookup results use small
independent records that preserve Baserow IDs and raw metadata. These records
contain no HTTP behavior and can be passed back to the corresponding writable
Field. Scalar reads remain ordinary Python values.

Filter Objects
--------------

Filters describe Baserow row-query conditions. Field/operator compatibility is
advisory because hosted Baserow is not version-pinned; normal queries allow
unknown operators to reach the service.
