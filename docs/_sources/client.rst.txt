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

The `Baserow` client class is designed to handle errors in a systematic and consistent manner when interacting with the Baserow API. 

1. **Predefined Error Messages**:
    The client has a predefined set of error messages for specific HTTP status codes:

    - **400 Bad Request**: The request contains invalid values, or the JSON couldn't be parsed.
    - **401 Unauthorized**: Accessing an endpoint without a valid database token.
    - **404 Not Found**: The requested row or table is not found.
    - **413 Request Entity Too Large**: The request exceeded the allowed payload size.
    - **415 Unsupported Media Type**: The media type in the request is not supported.
    - **500 Internal Server Error**: An unexpected condition was encountered by the server.
    - **502 Bad Gateway**: Baserow is restarting, or an unexpected outage is ongoing.
    - **503 Service Unavailable**: The server couldn't process the request in time.

2. **Logging**:
    Error messages are logged to the configured logger. Depending on the severity and type of the error, the client will use different log levels (`ERROR`, `WARNING`, `DEBUG`). The logs can be directed to the console or to a file, based on how you configure the Baserow client.

3. **Raising Exceptions**:
    In case of an error response from the Baserow server:

    - If the status code matches one of the predefined error codes, the corresponding error message is logged and raised as a `requests.exceptions.HTTPError`.
    - A timeout during the request will raise a `requests.exceptions.Timeout`.
    - Other request-related issues, such as connectivity problems, will raise a `requests.exceptions.RequestException`.
    - Any unexpected issues will raise a generic `Exception`.

4. **Response Parsing**:
    Once a response is received from the server, the client attempts to parse it:

    - If the response has a status code of 204 (No Content), it simply returns the status code.
    - If the response contains JSON data, it's parsed and returned as a dictionary.
    - If JSON parsing fails, the raw response text is returned.

Token Management
-----------------
The Baserow client requires an authentication token (token) during initialization to ensure authorized access. This token is used in the request headers for authentication purposes. Users are advised to manage and store their tokens securely. Avoid hardcoding tokens directly into your codebase, and instead, consider using environment variables, configuration files, or secure vaults. Regularly rotate your tokens, and ensure that old tokens are invalidated to maintain the security of your API interactions.
