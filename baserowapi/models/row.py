import logging
from typing import TYPE_CHECKING, Dict, Any, List, Type, Optional

if TYPE_CHECKING:
    from baserowapi.models.table import Table
    from baserowapi.baserow import Baserow as Client
    from baserowapi.models.fields.field import Field

from baserowapi.exceptions import (
    RowFetchError,
    RowUpdateError,
    RowDeleteError,
    RowMoveError,
)
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.models.row_values import (
    RowValueList,
    TextRowValue,
    LongTextRowValue,
    UrlRowValue,
    EmailRowValue,
    PhoneNumberRowValue,
    BooleanRowValue,
    RatingRowValue,
    NumberRowValue,
    DateRowValue,
    LastModifiedRowValue,
    CreatedOnRowValue,
    SingleSelectRowValue,
    MultipleSelectRowValue,
    FormulaRowValue,
    TableLinkRowValue,
    CountRowValue,
    LookupRowValue,
    MultipleCollaboratorsRowValue,
    FileRowValue,
    GenericRowValue,
    PasswordRowValue,
)


ROW_VALUE_TYPE_MAPPING: Dict[str, Type[RowValue]] = {
    "text": TextRowValue,
    "long_text": LongTextRowValue,
    "url": UrlRowValue,
    "email": EmailRowValue,
    "phone_number": PhoneNumberRowValue,
    "boolean": BooleanRowValue,
    "number": NumberRowValue,
    "rating": RatingRowValue,
    "date": DateRowValue,
    "last_modified": LastModifiedRowValue,
    "created_on": CreatedOnRowValue,
    "file": FileRowValue,
    "single_select": SingleSelectRowValue,
    "multiple_select": MultipleSelectRowValue,
    "formula": FormulaRowValue,
    "link_row": TableLinkRowValue,
    "count": CountRowValue,
    "lookup": LookupRowValue,
    "multiple_collaborators": MultipleCollaboratorsRowValue,
    "generic": GenericRowValue,
    "password": PasswordRowValue,
}


class Row:
    """
    Represents a row in a Baserow table. Provides methods to update, delete, and manipulate the row.
    """

    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self, row_data: Dict[str, Any], table: "Table", client: "Client"
    ) -> None:
        """
        Initializes a Row instance.

        :param row_data: Dictionary containing the row data.
        :type row_data: dict[str, Any]
        :param table: The table associated with the row.
        :type table: Table
        :param client: The client used for making requests.
        :type client: Client
        """
        self.id: Optional[int] = row_data.get("id")
        self.order: Optional[int] = row_data.get("order")
        self.table: "Table" = table
        self.table_id: int = table.id
        self.client: "Client" = client
        self._row_data: Dict[str, Any] = row_data
        self._values: Optional[RowValueList] = None

        self.logger.debug(f"Initialized Row id {self.id}")

    @property
    def values(self) -> RowValueList:
        """
        Retrieves the RowValueList for this row. If not yet created, it lazily loads
        the list using the stored row data and synchronizes the internal state.

        :return: RowValueList representing the values for this row.
        :rtype: RowValueList
        :raises RowFetchError: If there's an error creating the RowValueList.
        """
        if self._values is None:
            try:
                self._values = self._create_row_value_list(self._row_data)
                self.logger.debug(
                    f"RowValueList for Row id {self.id} successfully created."
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to create RowValueList for Row id {self.id}. Error: {e}"
                )
                raise RowFetchError(
                    f"Failed to create RowValueList for Row id {self.id}."
                ) from e
        return self._values

    @property
    def fields(self) -> List[str]:
        """
        Lazily retrieves a list of all field names from the Row's values.

        :return: A list of field names.
        :rtype: List[str]
        """
        if not hasattr(self, "_fields"):
            self._fields = self.values.fields
        return self._fields

    def _create_row_value_list(self, row_data: Dict[str, Any]) -> RowValueList:
        """
        Create a RowValueList based on the given row data and table fields.

        Metadata fields such as "id" and "order" are excluded from processing.

        :param row_data: Data representing the row.
        :type row_data: dict[str, Any]
        :return: RowValueList containing RowValue objects derived from the row data.
        :rtype: RowValueList
        :raises RowFetchError: If there's an error creating a RowValue object.
        """
        row_value_objects: List[RowValue] = []
        for field_name, value in row_data.items():
            # Skip metadata fields
            if field_name in ["id", "order"]:
                continue

            field_object = self._get_field_object(field_name)
            row_value_class = self._get_row_value_class(field_object.type)

            try:
                row_value_obj = row_value_class(
                    field=field_object, client=self.client, raw_value=value
                )
                row_value_objects.append(row_value_obj)
            except Exception as e:
                self.logger.error(
                    f"Failed to create RowValue object for field '{field_name}'. Error: {e}"
                )
                raise RowFetchError(
                    f"Failed to create RowValue object for field '{field_name}'."
                ) from e

        return RowValueList(row_value_objects)

    def _get_field_object(self, field_name: str) -> "Field":
        """
        Retrieve the corresponding Field object from the table.

        :param field_name: The name of the field to retrieve.
        :type field_name: str
        :return: The Field object corresponding to the given field name.
        :rtype: Field
        :raises KeyError: If the specified field name is not found in the table fields.
        """
        try:
            return self.table.fields[field_name]
        except KeyError:
            self.logger.error(f"Field '{field_name}' not found in table fields.")
            raise KeyError(f"Field '{field_name}' not found in table fields.")

    def _get_row_value_class(self, field_type: str) -> Type[RowValue]:
        """
        Get the appropriate RowValue class based on the field's type.

        :param field_type: The type of the field.
        :type field_type: str
        :return: The RowValue class corresponding to the given field type.
        :rtype: Type[RowValue]
        """
        row_value_class = ROW_VALUE_TYPE_MAPPING.get(field_type)
        if not row_value_class:
            self.logger.warning(
                f"Field type '{field_type}' not supported, using GenericRowValue."
            )
            row_value_class = (
                GenericRowValue  # Use GenericRowValue for unsupported types
            )
        return row_value_class

    def __repr__(self) -> str:
        """
        Return a string representation of the Row object.

        :return: A string indicating the Row's ID and associated table ID.
        :rtype: str
        """
        return f"Row id {self.id} of table {self.table_id}"

    def __getitem__(self, key: str) -> Any:
        """
        Retrieve a value from the row's values using dictionary-style access.

        :param key: The field name to retrieve.
        :type key: str
        :return: The value of the specified field.
        :rtype: Any
        :raises KeyError: If the specified field name is not found in the row values.
        """
        try:
            row_value = self.values[key]
            return row_value.value
        except KeyError:
            self.logger.warning(f"Field '{key}' not found in row values.")
            raise KeyError(f"Field '{key}' not found in the row values.")

    def __setitem__(self, key: str, new_value: Any) -> None:
        """
        Set a value for a specific field in the row using dictionary-style access.

        :param key: The field name to set.
        :type key: str
        :param new_value: The value to set for the specified field.
        :type new_value: Any
        :note: This modifies the in-memory representation of the row.
        :raises KeyError: If the specified field name is not found in the row values or is unrecognized.
        """
        try:
            row_value = self.values[key]
            row_value.value = new_value  # Using the value setter of the RowValue object

            # Synchronize _row_data with the updated value
            self._row_data[key] = new_value
        except KeyError:
            # Field not found in the Row's values
            self.logger.error(
                f"Attempted to set a value for an unrecognized field '{key}' in the row. Ensure the field exists in the table first."
            )
            raise KeyError(f"Field '{key}' not found in the row values.")

    def __eq__(self, other: object) -> bool:
        """
        Overridden equality method to compare two Row objects based on their id and table_id.

        :param other: Another object to compare with this Row instance.
        :type other: object
        :return: True if both objects are Rows and have the same id and table_id, otherwise False.
        :rtype: bool
        """
        if isinstance(other, Row):
            return getattr(self, "id", None) == getattr(other, "id", None) and getattr(
                self, "table_id", None
            ) == getattr(other, "table_id", None)
        return False

    def __contains__(self, key: str) -> bool:
        """
        Check if a field name exists in the row's values.

        :param key: The field name to check.
        :type key: str
        :return: True if the field name exists in the row's values, False otherwise.
        :rtype: bool
        """
        return key in self.values

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Row's values to a dictionary.

        :return: A dictionary representation of the row's values.
        :rtype: dict[str, Any]
        """
        if self._values is None:
            # Lazily load the row values if they haven't been loaded yet
            self.values  # Accessing the property to trigger lazy loading

        return {row_value.name: row_value.value for row_value in self.values}

    def update(
        self, values: Optional[Dict[str, Any]] = None, memory_only: bool = False
    ) -> "Row":
        """
        Updates the row in the table and synchronizes the internal state.

        :param values: A dictionary containing field values for updating the row.
                    Defaults to values from the self.values property.
        :type values: dict[str, Any], optional
        :param memory_only: If True, only updates the in-memory row and skips the API request. Defaults to False.
        :type memory_only: bool, optional
        :return: A Row object representing the updated row.
        :rtype: Row
        :raises RowUpdateError: If the API request results in any error responses.
        """
        try:
            # Prepare the payload for the API
            payload = {}

            # If no values dict is provided, use the in-memory row values
            if values is None:
                for rv in self.values:
                    if not rv.is_read_only:
                        payload[rv.name] = rv.format_for_api()

            else:
                for field_name, value in values.items():
                    if field_name not in self.table.writable_fields:
                        raise KeyError(
                            f"Field '{field_name}' is either read-only or does not exist in the table."
                        )

                    # Get the field object
                    field_object = self.table.fields[field_name]

                    # Validate the value
                    try:
                        field_object.validate_value(value)
                    except ValueError as ve:
                        raise ValueError(
                            f"Invalid value for field '{field_name}': {ve}"
                        ) from ve

                    # Format the value for API submission
                    formatted_value = field_object.format_for_api(value)
                    payload[field_name] = formatted_value

                    # Update the in-memory value (this does not change the original value)
                    self[field_name] = value

            # Debugging: Print the payload
            self.logger.debug(f"Payload for API request: {payload}")

            # Synchronize _row_data with the current state of _values
            self._row_data.update(self.to_dict())

            if memory_only:
                self.logger.debug(
                    f"Memory-only update for row with ID {self.id}. Skipping API request."
                )
                return self

            if not payload:
                self.logger.warning("Update called, but no fields were updated.")

            # Make the API request to update the row in the Baserow table
            endpoint = (
                f"/api/database/rows/table/{self.table_id}/{self.id}/?user_field_names=true"
            )
            response = self.client.make_api_request(endpoint, method="PATCH", data=payload)

            # Update _row_data and _values with the new data from the API
            self._row_data = response
            self._values = self._create_row_value_list(self._row_data)
            self.logger.debug(f"Successfully updated row with ID {self.id}.")

            return self

        except Exception as e:
            self.logger.error(
                f"Failed to update row with ID {self.id} in table {self.table_id}. Error: {e}"
            )
            raise RowUpdateError(f"Failed to update row with ID {self.id}.") from e

    def delete(self) -> bool:
        """
        Deletes the row from the table using the Baserow delete endpoint.

        :return: True if deletion was successful.
        :rtype: bool
        :raises RowDeleteError: For errors during the delete operation.
        """
        self.logger.debug(
            f"Attempting to delete row with ID {self.id} from table {self.table_id}."
        )
        try:
            endpoint = f"/api/database/rows/table/{self.table_id}/{self.id}/"
            response_code = self.client.make_api_request(endpoint, method="DELETE")

            if response_code == 204:
                self.logger.debug(
                    f"Successfully deleted row with ID {self.id} from table {self.table_id}."
                )
                return True
            else:
                self.logger.warning(
                    f"Unexpected status code {response_code} received when trying to delete row with ID {self.id}."
                )
                raise RowDeleteError(
                    f"Unexpected status code received: {response_code}"
                )

        except ValueError as e:
            raise RowDeleteError(f"Failed to delete row with ID {self.id}.") from e
        except Exception as e:
            self.logger.error(
                f"Failed to delete row with ID {self.id} from table {self.table_id}. Error: {e}"
            )
            raise RowDeleteError(f"Failed to delete row with ID {self.id}.") from e

    def move(self, before_id: Optional[int] = None) -> "Row":
        """
        Moves the current row to a position before the row specified by before_id.

        :param before_id: The ID of the row before which the current row should be moved. If not specified, the row will be moved to the last position.
        :type before_id: int, optional
        :return: A Row object representing the updated row.
        :rtype: Row
        :raises RowMoveError: If there's an error during the move operation.
        """
        self.logger.debug(
            f"Attempting to move row with ID {self.id} in table {self.table_id}."
        )
        try:
            endpoint = f"/api/database/rows/table/{self.table_id}/{self.id}/move/?user_field_names=true"
            if before_id is not None:
                endpoint += f"&before_id={before_id}"

            response = self.client.make_api_request(endpoint, method="PATCH")

            moved_row_data = response
            moved_row = Row(
                table=self.table, client=self.client, row_data=moved_row_data
            )
            self.logger.debug(
                f"Successfully moved row with ID {self.id} in table {self.table_id}."
            )

            return moved_row

        except Exception as e:
            self.logger.error(
                f"Failed to move row with ID {self.id} in table {self.table_id}. Error: {e}"
            )
            raise RowMoveError(f"Failed to move row with ID {self.id}.") from e
