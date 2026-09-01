Baserow Client Class
====================

Introduction
------------
The `Baserow` class provides the main entry point to interact with the Baserow API. This class serves as the API client and facilitates all the API calls. For any other classes that require API access, this class is passed as a reference to ensure smooth and coherent operations.

Initialization Options
----------------------
When creating an instance of the `Baserow` class, you can specify several parameters to customize your connection and interactions with the Baserow server.

Parameters:

- **token** (str): 
  - Required. The authentication token for Baserow.
- **url** (str, optional): 
  - The base URL for the Baserow server. Default is `'https://api.baserow.io'`.
- **logging_level** (str, optional): 
  - The desired logging level. Available options include: `'INFO'`, `'ERROR'`, and `'DEBUG'`. If unspecified, logging will be disabled.
- **log_file** (str, optional): 
  - Specify a file path to log the interactions. Useful if you want to persist logs for later analysis. This parameter will be ignored if `logging_level` is not specified.

Examples
--------
.. code-block:: python

    from baserowapi import Baserow

    # Default baserow client
    baserow = Baserow(token='mytoken')

    # Specify a custom server URL
    baserow = Baserow(url='https://baserow.example.com', token='mytoken')

    # Enable logging at DEBUG level
    baserow = Baserow(url='https://baserow.example.com', token='mytoken', logging_level='DEBUG')

    # Enable logging to a file
    baserow = Baserow(url='https://baserow.example.com', token='mytoken', logging_level='DEBUG', log_file='log.txt')


Error Handling
---------------

All package-defined exceptions inherit from
:class:`baserowapi.exceptions.BaserowAPIError`. Low-level calls made through
:meth:`Baserow.make_api_request` use these exceptions:

* :class:`~baserowapi.exceptions.BaserowTimeoutError` when a request times out.
* :class:`~baserowapi.exceptions.BaserowConnectionError` when a connection cannot be established.
* :class:`~baserowapi.exceptions.BaserowRequestError` for another request execution failure.
* :class:`~baserowapi.exceptions.BaserowHTTPError` for every non-2xx response, not only a predefined set of status codes.
* :class:`~baserowapi.exceptions.BaserowResponseError` when a response advertised as JSON cannot be decoded.

The original ``requests`` exception is available through the raised
exception's ``__cause__``. ``BaserowHTTPError`` provides ``status_code``,
``method``, ``url``, ``error_code``, and ``description`` attributes. The last
two contain Baserow's structured error details when the response supplies
them.

Higher-level table and row operations retain operation-specific exceptions,
such as :class:`~baserowapi.exceptions.RowFetchError` and
:class:`~baserowapi.exceptions.RowUpdateError`. Their ``__cause__`` contains
the lower-level failure. Caller validation errors remain distinct and are not
converted into request errors.

Successful JSON responses are decoded and returned. A 204 response returns
the integer ``204``, and an empty response returns ``None``. A non-JSON
response is returned as text when its content type does not advertise JSON.

Token Management
-----------------
The Baserow client requires an authentication token (token) during initialization to ensure authorized access. This token is used in the request headers for authentication purposes. Users are advised to manage and store their tokens securely. Avoid hardcoding tokens directly into your codebase, and instead, consider using environment variables, configuration files, or secure vaults. Regularly rotate your tokens, and ensure that old tokens are invalidated to maintain the security of your API interactions.
