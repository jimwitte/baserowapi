import os
import json
from pathlib import Path
from types import MappingProxyType
from unittest.mock import Mock

import pytest
from dotenv import load_dotenv

from baserowapi import Baserow
from baserowapi.exceptions import BaserowHTTPError, RowAddError, RowDeleteError
from baserowapi.models.row import Row
from baserowapi.models.table import Table


FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"


@pytest.fixture
def characterized_field_metadata():
    with (FIXTURE_DIRECTORY / "field_metadata.json").open(encoding="utf-8") as stream:
        return json.load(stream)


@pytest.fixture
def characterized_row_response():
    with (FIXTURE_DIRECTORY / "row_response.json").open(encoding="utf-8") as stream:
        return json.load(stream)


@pytest.fixture
def characterized_table(characterized_field_metadata):
    client = Mock()
    client.batch_size = 10
    table = Table(10, client)
    fields = [
        Table._field_class_from_data(field_data)(
            field_data["name"], field_data, client=client
        )
        for field_data in characterized_field_metadata
    ]
    table._fields = MappingProxyType({field.name: field for field in fields})
    return table


@pytest.fixture
def characterized_row(characterized_table, characterized_row_response):
    return Row(
        row_data=characterized_row_response,
        table=characterized_table,
        client=characterized_table.client,
    )


@pytest.fixture(scope="session")
def integration_environment():
    load_dotenv()
    required_variables = (
        "BASEROW_URL",
        "BASEROW_TOKEN",
        "BASEROW_TABLE_ID",
    )
    missing_variables = [
        variable for variable in required_variables if not os.getenv(variable)
    ]
    if missing_variables:
        missing_names = ", ".join(missing_variables)
        raise pytest.UsageError(
            f"Integration tests require these environment variables: {missing_names}"
        )


@pytest.fixture(scope="session")
def baserow_client(integration_environment):
    token = os.getenv("BASEROW_TOKEN")
    url = os.getenv("BASEROW_URL")
    return Baserow(token=token, url=url)


@pytest.fixture(scope="session")
def all_fields_table(baserow_client):
    table_id = os.getenv("BASEROW_TABLE_ID")
    return baserow_client.get_table(table_id)


def _is_missing_row_error(error):
    current = error
    while current is not None:
        if isinstance(current, BaserowHTTPError) and current.status_code == 404:
            return True
        current = current.__cause__
    return False


def _record_added_rows(add_rows, created_row_ids, *args, **kwargs):
    """Record successful rows, including completed chunks from a failed batch."""
    try:
        rows = add_rows(*args, **kwargs)
    except RowAddError as error:
        created_row_ids.extend(error.completed_row_ids)
        raise
    created_row_ids.extend(row.id for row in rows)
    return rows


@pytest.fixture(autouse=True)
def cleanup_integration_rows(request, monkeypatch):
    if request.node.get_closest_marker("integration") is None:
        yield
        return

    table = request.getfixturevalue("all_fields_table")
    created_row_ids = []
    original_add_row = table.add_row
    original_add_rows = table.add_rows

    def tracked_add_row(*args, **kwargs):
        row = original_add_row(*args, **kwargs)
        created_row_ids.append(row.id)
        return row

    def tracked_add_rows(*args, **kwargs):
        return _record_added_rows(
            original_add_rows, created_row_ids, *args, **kwargs
        )

    monkeypatch.setattr(table, "add_row", tracked_add_row)
    monkeypatch.setattr(table, "add_rows", tracked_add_rows)

    try:
        yield
    finally:
        cleanup_errors = []
        for row_id in dict.fromkeys(reversed(created_row_ids)):
            try:
                table.delete_row(row_id)
            except RowDeleteError as error:
                if not _is_missing_row_error(error):
                    cleanup_errors.append(error)
        if cleanup_errors:
            raise cleanup_errors[0]

@pytest.fixture
def single_row_data(all_fields_table):
    return {
        "Name": {
            "input": "Test Name",
            "expected": "Test Name",
            "read_only": False,
        },
        "Notes": {
            "input": "Sample note for testing",
            "expected": "Sample note for testing",
            "read_only": False,
        },
        "Active": {
            "input": True,
            "expected": True,
            "read_only": False,
        },
        "Number": {
            "input": 42,
            "expected": "42.00",
            "read_only": False,
        },
        "Rating": {
            "input": 5,
            "expected": 5,
            "read_only": False,
        },
        "US Date Time": {
            "input": "2023-08-12T12:00:00Z",
            "expected": "2023-08-12T12:00:00Z",
            "read_only": False,
        },
        "Last modified": {
            "input": None,
            "expected": "2023-08-12T13:00:00Z",
            "read_only": True,
        },
        "Created on": {
            "input": None,
            "expected": None,
            "read_only": True,
        },
        "EU Date": {
            "input": "2023-12-08",
            "expected": "2023-12-08",
            "read_only": False,
        },
        "ISO Date": {
            "input": "2024-03-17",
            "expected": "2024-03-17",
            "read_only": False,
        },
        "URL": {
            "input": "https://example.com",
            "expected": "https://example.com",
            "read_only": False,
        },
        "Email": {
            "input": "test@example.com",
            "expected": "test@example.com",
            "read_only": False,
        },
        "FileField": {
            "input": [],
            "expected": [],
            "read_only": False,
        },
        "SingleSelect": {
            "input": "option 1",
            "expected": all_fields_table.fields["SingleSelect"].resolve_option(
                "option 1"
            ),
            "read_only": False,
        },
        "MultipleSelect": {
            "input": ["option 1", "option 2"],
            "expected": [
                all_fields_table.fields["MultipleSelect"].resolve_option("option 1"),
                all_fields_table.fields["MultipleSelect"].resolve_option("option 2"),
            ],
            "read_only": False,
        },
        "Phone": {
            "input": "+1234567890",
            "expected": "+1234567890",
            "read_only": False,
        },
        "Formula": {
            "input": None,
            "expected": None,
            "read_only": True,
        },
        "TableLink": {
            "input": [],
            "expected": [],
            "read_only": False,
        },
        "Count": {
            "input": None,
            "expected": None,
            "read_only": True,
        },
        "Lookup": {
            "input": None,
            "expected": None,
            "read_only": True,
        },
        "Collaborators": {
            "input": [],
            "expected": [],
            "read_only": False,
        },
        "Last name": {
            "input": "Doe",
            "expected": "Doe",
            "read_only": False,
        },
        "UUID": {
            "input": None,
            "expected": None,
            "read_only": True,
        },
        "Autonumber": {
            "input": None,
            "expected": None,
            "read_only": True,
        },
        "Password": {
            "input": 'password',
            "expected": True,
            "read_only": False,
        },
    }
