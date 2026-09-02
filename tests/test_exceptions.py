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
    FieldValueError,
    FilterError,
    InvalidFieldNameError,
    InvalidOperatorError,
    RowAddError,
    RowDeleteError,
    RowError,
    RowFetchError,
    RowMoveError,
    RowUpdateError,
    RowWriteError,
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
        FieldValueError,
        InvalidFieldNameError,
        InvalidOperatorError,
        RowAddError,
        RowDeleteError,
        RowFetchError,
        RowMoveError,
        RowUpdateError,
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
        issubclass(exception_class, RowWriteError)
        for exception_class in (RowAddError, RowUpdateError)
    )
    assert all(
        issubclass(exception_class, FilterError)
        for exception_class in (InvalidFieldNameError, InvalidOperatorError)
    )
    assert all(
        issubclass(exception_class, FieldError)
        for exception_class in (
            FieldDataRetrievalError,
            FieldValidationError,
            FieldValueError,
        )
    )
