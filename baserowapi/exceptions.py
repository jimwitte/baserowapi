"""Exceptions raised by :mod:`baserowapi`."""

from typing import Iterable, Optional


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


class RowWriteError(RowError):
    """Base class for create and update failures.

    Batch writes are not atomic. When an earlier request chunk succeeded before
    a later chunk failed, ``completed_row_ids`` identifies the rows known to
    have been written and ``failed_batch_number`` identifies the one-based
    request chunk that failed.
    """

    def __init__(
        self,
        message: str,
        *,
        failed_batch_number: Optional[int] = None,
        completed_row_ids: Iterable[int] = (),
    ) -> None:
        self.message = message
        self.failed_batch_number = failed_batch_number
        self.completed_row_ids = tuple(completed_row_ids)
        self.completed_count = len(self.completed_row_ids)
        super().__init__(message)


class RowAddError(RowWriteError):
    """Raised when adding rows fails."""


class RowUpdateError(RowWriteError):
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


class FieldValueError(FieldError):
    """Raised when an explicit field value conversion cannot be completed."""


class FieldDataRetrievalError(FieldError):
    """Raised when data required by a field cannot be retrieved."""
