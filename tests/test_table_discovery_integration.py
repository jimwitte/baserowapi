import os

import pytest


pytestmark = pytest.mark.integration


def test_hosted_database_token_discovers_configured_table(baserow_client):
    tables = baserow_client.get_tables()
    configured_table_id = int(os.environ["BASEROW_TABLE_ID"])
    discovered = next(table for table in tables if table.id == configured_table_id)

    assert discovered.name
    assert isinstance(discovered.database_id, int)
    assert list(discovered.fields)
