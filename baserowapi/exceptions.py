"""Exceptions raised by :mod:`baserowapi`."""

from typing import Optional


class BaserowAPIError(Exception):
    """Base class for all exceptions intentionally raised by this package."""


class BaserowRequestError(BaserowAPIError):
    """Raised when an API request cannot be completed."""

    def __init__(
        self,
        message: str,
        *,
        method: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        self.message = message
        self.method = method
        self.url = url
        super().__init__(message)


class BaserowTimeoutError(BaserowRequestError):
    """Raised when an API request exceeds its timeout."""


class BaserowConnectionError(BaserowRequestError):
    """Raised when a connection to Baserow cannot be established."""


class BaserowHTTPError(BaserowAPIError):
    """Raised when Baserow returns a non-successful HTTP response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        method: Optional[str] = None,
        url: Optional[str] = None,
        error_code: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.method = method
        self.url = url
        self.error_code = error_code
        self.description = description
        super().__init__(message)

    def __str__(self) -> str:
        return f"HTTP {self.status_code}: {self.message}"


class BaserowResponseError(BaserowAPIError):
    """Raised when a Baserow response cannot be interpreted as advertised."""

    def __init__(
        self,
        message: str,
        *,
        method: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        self.message = message
        self.method = method
        self.url = url
        super().__init__(message)


class RowError(BaserowAPIError):
    """Base class for row operation errors."""


class RowFetchError(RowError):
    """Raised when fetching rows fails."""


class RowAddError(RowError):
    """Raised when adding rows fails."""


class RowUpdateError(RowError):
    """Raised when updating rows fails."""


class RowDeleteError(RowError):
    """Raised when deleting rows fails."""


class RowMoveError(RowError):
    """Raised when moving a row fails."""


class FilterError(BaserowAPIError):
    """Base class for filter-related errors."""


class InvalidFieldNameError(FilterError):
    """Raised when a filter field name is invalid."""


class InvalidOperatorError(FilterError):
    """Raised when a filter operator is invalid."""


class FieldError(BaserowAPIError):
    """Base class for field-related errors."""


class FieldValidationError(FieldError):
    """Raised when a field value fails validation."""


class FieldDataRetrievalError(FieldError):
    """Raised when data required by a field cannot be retrieved."""


class RowValueError(BaserowAPIError):
    """Base class for row-value errors."""


class InvalidRowValueError(RowValueError):
    """Raised when a value is incompatible with its field."""


class RowValueOperationError(RowValueError):
    """Raised when row-value formatting or conversion fails."""


class ReadOnlyValueError(RowValueError):
    """Raised when attempting to set a read-only row value."""
