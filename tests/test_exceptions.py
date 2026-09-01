import pytest

from baserowapi.exceptions import (
    BaserowAPIError,
    BaserowConnectionError,
    BaserowHTTPError,
    BaserowRequestError,
    BaserowResponseError,
    BaserowTimeoutError,
    FieldDataRetrievalError,
    FieldError,
    FieldValidationError,
    FilterError,
    InvalidFieldNameError,
    InvalidOperatorError,
    InvalidRowValueError,
    ReadOnlyValueError,
    RowAddError,
    RowDeleteError,
    RowError,
    RowFetchError,
    RowMoveError,
    RowUpdateError,
    RowValueError,
    RowValueOperationError,
)

pytestmark = pytest.mark.offline


def test_package_exceptions_share_a_common_base():
    exception_classes = (
        BaserowConnectionError,
        BaserowHTTPError,
        BaserowRequestError,
        BaserowResponseError,
        BaserowTimeoutError,
        FieldDataRetrievalError,
        FieldValidationError,
        InvalidFieldNameError,
        InvalidOperatorError,
        InvalidRowValueError,
        ReadOnlyValueError,
        RowAddError,
        RowDeleteError,
        RowFetchError,
        RowMoveError,
        RowUpdateError,
        RowValueOperationError,
    )

    assert all(
        issubclass(exception_class, BaserowAPIError)
        for exception_class in exception_classes
    )


def test_domain_exception_groups_are_consistent():
    assert all(
        issubclass(exception_class, BaserowRequestError)
        for exception_class in (BaserowConnectionError, BaserowTimeoutError)
    )
    assert all(
        issubclass(exception_class, RowError)
        for exception_class in (
            RowAddError,
            RowDeleteError,
            RowFetchError,
            RowMoveError,
            RowUpdateError,
        )
    )
    assert all(
        issubclass(exception_class, FilterError)
        for exception_class in (InvalidFieldNameError, InvalidOperatorError)
    )
    assert all(
        issubclass(exception_class, FieldError)
        for exception_class in (FieldDataRetrievalError, FieldValidationError)
    )
    assert all(
        issubclass(exception_class, RowValueError)
        for exception_class in (
            InvalidRowValueError,
            ReadOnlyValueError,
            RowValueOperationError,
        )
    )
