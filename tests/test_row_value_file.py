from pathlib import Path

import pytest

from baserowapi import BaserowFile

pytestmark = pytest.mark.integration


def empty_file_row(all_fields_table, single_row_data):
    single_row_data["FileField"]["input"] = []
    input_data = {
        key: value["input"]
        for key, value in single_row_data.items()
        if not value["read_only"]
    }
    return all_fields_table.add_row(input_data)


def test_upload_file_returns_unattached_file_for_explicit_assignment(
    baserow_client, all_fields_table, single_row_data
):
    created_row = empty_file_row(all_fields_table, single_row_data)
    file_path = Path(__file__).with_name("bike.png")

    uploaded = baserow_client.upload_file(file_path)

    assert isinstance(uploaded, BaserowFile)
    assert uploaded.name
    assert uploaded.original_name == "bike.png"
    assert created_row["FileField"] == []

    created_row.update({"FileField": [uploaded]})
    stored_files = all_fields_table.get_row(created_row.id)["FileField"]
    assert len(stored_files) == 1
    assert stored_files[0].name == uploaded.name


def test_upload_via_url_returns_unattached_file_for_explicit_assignment(
    baserow_client, all_fields_table, single_row_data
):
    created_row = empty_file_row(all_fields_table, single_row_data)
    source = baserow_client.upload_file(Path(__file__).with_name("bike.png"))

    imported = baserow_client.upload_file_via_url(source.url)

    assert isinstance(imported, BaserowFile)
    assert imported.name
    assert created_row["FileField"] == []

    created_row.update({"FileField": [imported]})
    stored_files = all_fields_table.get_row(created_row.id)["FileField"]
    assert len(stored_files) == 1
    assert stored_files[0].name == imported.name
