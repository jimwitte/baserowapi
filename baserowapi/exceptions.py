# baserow client exceptions

class BaserowAPIError(Exception):
    """Base class for exceptions."""

    pass


class BaserowHTTPError(BaserowAPIError):
    """Exception raised for HTTP errors."""

    def __init__(self, status_code: int, message: str):
        """
        :param status_code: The HTTP status code.
        :type status_code: int
        :param message: The error message.
        :type message: str
        """
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        :return: The string representation of the error.
        :rtype: str
        """
        return f"HTTP {self.status_code}: {self.message}"


# row exceptions

class RowError(Exception):
    """Base class for all Row-related exceptions."""

    pass


class RowFetchError(RowError):
    """Raised when fetching row values fails."""

    pass


class RowUpdateError(RowError):
    """Raised when updating a row fails."""

    pass


class RowDeleteError(RowError):
    """Raised when deleting a row fails."""

    pass


class RowMoveError(RowError):
    """Raised when moving a row fails."""

    pass


# table exceptions

class RowFetchError(BaserowAPIError):
    """Raised when fetching rows fails."""

    pass


class RowAddError(BaserowAPIError):
    """Raised when adding rows fails."""

    pass


class RowUpdateError(BaserowAPIError):
    """Raised when updating rows fails."""

    pass


class RowDeleteError(BaserowAPIError):
    """Raised when deleting rows fails."""

    pass


# filter exceptions

class FilterError(BaserowAPIError):
    """Base exception class for filter-related errors."""

    pass


class InvalidFieldNameError(FilterError):
    """Raised when the field name in a filter is invalid."""

    pass


class InvalidOperatorError(FilterError):
    """Raised when the operator in a filter is invalid."""

    pass


# field exceptions

class FieldValidationError(Exception):
    """Raised when a field value fails validation."""

    pass


class FieldDataRetrievalError(Exception):
    """Raised when there is an error retrieving data for a field."""

    pass


# row_value exceptions

class InvalidRowValueError(Exception):
    """Raised when a row value is invalid or incompatible with its corresponding field."""

    pass


class RowValueOperationError(Exception):
    """Raised when a row value operation fails, such as formatting or data conversion."""

    pass


class ReadOnlyValueError(Exception):
    """Raised when an attempt is made to set a value on a read-only row value."""

    pass
