Baserow Client Class
====================

The ``Baserow`` client is the authenticated request boundary for the hosted
database-token API. It constructs Tables, discovers token-visible Tables,
uploads files, and translates request and response failures into package
exceptions.

Initialization
--------------

``token`` is required and must be a non-empty database token. ``url`` defaults
to ``https://api.baserow.io``. ``timeout`` sets the request timeout in seconds,
and ``read_retries`` sets the number of retries for safe reads.

.. code-block:: python

    from baserowapi import Baserow

    baserow = Baserow(token="mytoken")

    baserow = Baserow(
        url="https://baserow.example.com",
        token="mytoken",
        timeout=20,
        read_retries=2,
    )

The default timeout is 10 seconds and the default safe-read retry count is two.
Retries apply only to ``GET`` and ``HEAD`` requests after a timeout, connection
failure, or a ``429``, ``502``, ``503``, or ``504`` response. They use
exponential backoff and honor ``Retry-After``. Mutating ``POST``, ``PATCH``, and
``DELETE`` requests are never retried automatically.

The package emits ordinary Python logging records but does not configure root
logging, handlers, levels, or files. Applications retain full control of their
logging configuration.

Table discovery and schema snapshots
------------------------------------

``get_tables`` uses Baserow's database-token discovery endpoint and returns a
list of Tables visible to the token:

.. code-block:: python

    for table in baserow.get_tables():
        print(table.id, table.name, table.database_id, table.order)

Each discovered Table retains the complete returned metadata in its read-only
``metadata`` mapping. ``get_table(table_id)`` remains useful when an ID is
already known.

Every call to ``get_table`` returns a new Table. A Table loads and caches its
field schema only when ``fields`` is first accessed. After a schema change made
through the Baserow UI or a separate administrative client, construct a new
Table to obtain a new schema snapshot:

.. code-block:: python

    table = baserow.get_table(table.id)

Low-level request escape hatch
------------------------------

``make_api_request`` supports database-token endpoints not yet modeled by the
package:

.. code-block:: python

    response = baserow.make_api_request("/api/database/example/")

It provides authentication, timeouts, safe-read retries, response parsing, and
package exceptions. It does not add Field semantics or guarantee that an
unmodeled Baserow endpoint will remain stable.

Relative endpoints must start with ``/``. Absolute URLs are accepted for
Baserow pagination, but their scheme, host, and port must match the configured
Baserow URL. This prevents the database token from being sent to another
origin. Per-request headers cannot replace the database-token Authorization
header.

A per-request timeout may override the client default:

.. code-block:: python

    response = baserow.make_api_request("/api/database/example/", timeout=30)

Error handling
--------------

All package-defined exceptions inherit from
:class:`baserowapi.exceptions.BaserowAPIError`. Low-level requests raise:

* :class:`~baserowapi.exceptions.BaserowTimeoutError` after the permitted safe
  read retries are exhausted;
* :class:`~baserowapi.exceptions.BaserowConnectionError` when a connection
  cannot be established;
* :class:`~baserowapi.exceptions.BaserowRequestError` for another request
  execution failure;
* :class:`~baserowapi.exceptions.BaserowHTTPError` for every non-2xx response;
* :class:`~baserowapi.exceptions.BaserowResponseError` when advertised JSON or
  a modeled response shape cannot be interpreted.

The original ``requests`` exception is available through ``__cause__``.
``BaserowHTTPError`` provides ``status_code``, ``method``, ``url``,
``error_code``, and ``description``. Higher-level Table and Row operations
retain their operation-specific exceptions and chain the request failure.

Successful JSON responses are decoded and returned. A 204 response returns the
integer ``204``, an empty response returns ``None``, and non-JSON content is
returned as text when its content type does not advertise JSON.

Token handling
--------------

Store database tokens outside source code, such as in environment variables or
a credential manager. The client owns the Authorization header and will not
allow a per-request header mapping to replace it.
