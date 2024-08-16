import pytest
from baserowapi import Baserow
from dotenv import load_dotenv
import os


@pytest.fixture(scope="session")
def baserow_client():
    load_dotenv()
    token = os.getenv("BASEROW_TOKEN")
    url = os.getenv("BASEROW_URL")
    return Baserow(token=token, url=url)


@pytest.fixture(scope="session")
def all_fields_table(baserow_client):
    table_id = os.getenv("BASEROW_TABLE_ID")
    return baserow_client.get_table(table_id)


@pytest.fixture(scope="session")
def link_field_table(baserow_client):
    link_table_id = os.getenv("LINK_TABLE_ID")  # Set this in your .env file
    return baserow_client.get_table(link_table_id)


@pytest.fixture
def single_row_data():
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
            "expected": "option 1",
            "read_only": False,
        },
        "MultipleSelect": {
            "input": ["option 1", "option 2"],
            "expected": ["option 1", "option 2"],
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
