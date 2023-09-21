import pytest
from baserowapi.validators.field_validator import FieldValidator


class MockTable:
    def __init__(self, field_names, readonly_fields=None):
        self.fields = [MockField(name) for name in field_names]
        for field in self.fields:
            if readonly_fields and field.name in readonly_fields:
                field.is_read_only = True

    def get_field_names(self):
        return [field.name for field in self.fields]


class MockField:
    def __init__(self, name):
        self.name = name
        self.is_read_only = False


@pytest.fixture
def sample_table():
    return MockTable(["name", "age", "address"], readonly_fields=["address"])


def test_valid_fields_against_table(sample_table):
    fields = {"name": "Alice", "age": 30}
    FieldValidator.validate_fields_against_table(fields, sample_table)
    # If no exception is raised, the test passes


def test_invalid_fields_against_table(sample_table):
    fields = {"name": "Alice", "birthday": "2000-01-01"}
    with pytest.raises(ValueError, match="'birthday' is not a valid field in the table."):
        FieldValidator.validate_fields_against_table(fields, sample_table)


def test_readonly_fields_for_update(sample_table):
    fields = [{"id": 1, "name": "Alice", "address": "Wonderland St."}]
    with pytest.raises(ValueError, match="'address' is read-only and cannot be updated."):
        FieldValidator.validate_fields_against_table(fields, sample_table, is_update=True)


def test_missing_required_metadata_for_update(sample_table):
    fields = [{"name": "Alice"}]
    with pytest.raises(ValueError, match="'id' is required for updating rows."):
        FieldValidator.validate_fields_against_table(fields, sample_table, is_update=True)


def test_validating_list_of_field_dicts(sample_table):
    fields = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    FieldValidator.validate_fields_against_table(fields, sample_table)
    # If no exception is raised, the test passes


def test_validating_list_with_invalid_field_dicts(sample_table):
    fields = [{"name": "Alice", "age": 30}, {"name": "Bob", "occupation": "Engineer"}]
    with pytest.raises(ValueError, match="'occupation' is not a valid field in the table."):
        FieldValidator.validate_fields_against_table(fields, sample_table)
