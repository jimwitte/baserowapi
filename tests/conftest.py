import os
import pytest
from dotenv import load_dotenv, find_dotenv
import logging

from baserowapi.baserow import Baserow

# Configure logging to display log messages in the console
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Now we can import the Baserow class
from baserowapi import Baserow, Table

# Load environment variables
dotenv_path = find_dotenv()
load_dotenv()

print(f"Dotenv file used: {dotenv_path}")

# Print to verify loading
print(f"BASEROW_URL: {os.getenv('BASEROW_URL')}")
print(f"BASEROW_TOKEN: {os.getenv('BASEROW_TOKEN')}")
print(f"BASEROW_TABLE_ID: {os.getenv('BASEROW_TABLE_ID')}")

@pytest.fixture(scope="session")
def baserow_client():
    BASEROW_URL = os.getenv("BASEROW_URL")
    BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")
    if not all([BASEROW_URL, BASEROW_TOKEN]):
        raise EnvironmentError(
            "Both BASEROW_URL and BASEROW_TOKEN must be set in the .env file."
        )
    return Baserow(url=BASEROW_URL, token=BASEROW_TOKEN)


@pytest.fixture(scope="session")
def test_table(baserow_client):
    BASEROW_TABLE_ID = os.getenv("BASEROW_TABLE_ID")
    if not BASEROW_TABLE_ID:
        raise EnvironmentError("BASEROW_TABLE_ID must be set in the .env file.")
    table_id = int(BASEROW_TABLE_ID)
    return baserow_client.get_table(table_id)

import pytest


@pytest.fixture(scope="function")
def test_row_manager(test_table):
    created_rows = []

    def add_row(data):
        row = test_table.add_row(data)
        created_rows.append(row.id)
        return row

    yield add_row

    # Cleanup: delete all created rows after each test
    if created_rows:
        try:
            test_table.delete_rows(created_rows)
        except Exception as e:
            # Log the exception and continue, so other tests are not affected
            print(f"Error during cleanup: {e}")
