from unittest.mock import Mock

import pytest

from baserowapi.exceptions import RowAddError
from tests.conftest import _record_added_rows


pytestmark = pytest.mark.offline


def test_resource_tracker_records_rows_completed_before_batch_add_failure():
    created_row_ids = []
    failure = RowAddError(
        "second batch failed",
        failed_batch_number=2,
        completed_row_ids=[101, 102],
    )
    add_rows = Mock(side_effect=failure)

    with pytest.raises(RowAddError) as raised:
        _record_added_rows(add_rows, created_row_ids, [{"Name": "test"}])

    assert raised.value is failure
    assert created_row_ids == [101, 102]


def test_resource_tracker_records_every_successful_batch_add_result():
    rows = [Mock(id=101), Mock(id=102)]
    created_row_ids = []

    returned = _record_added_rows(Mock(return_value=rows), created_row_ids, [])

    assert returned is rows
    assert created_row_ids == [101, 102]
