import pytest
from baserowapi import Baserow
import os
from dotenv import load_dotenv

@pytest.fixture(scope="session")
def baserow_config():
    """Load environment variables and provide them as a dictionary."""
    
    # Load environment variables
    load_dotenv()

    # Read variables from the environment
    config = {
        "url": os.getenv("BASEROW_URL"),
        "token": os.getenv("BASEROW_TOKEN"),
        "table_id": int(os.getenv("BASEROW_TABLE_ID")),
        "view_id": int(os.getenv("BASEROW_VIEW_ID")),
    }

    # Ensure environment variables are set
    if not all(config.values()):
        raise EnvironmentError("ENV not set.")
    
    return config

@pytest.fixture(scope="session")
def baserow_client(baserow_config):
    """Fixture to provide a Baserow client instance for the test session."""
    return Baserow(url=baserow_config["url"], token=baserow_config["token"])

@pytest.fixture(scope="session")
def table(baserow_client, baserow_config):
    """Fixture to provide a specific table for testing."""
    return baserow_client.get_table(table_id=baserow_config["table_id"])
