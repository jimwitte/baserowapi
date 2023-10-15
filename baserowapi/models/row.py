import logging
from typing import TYPE_CHECKING, Dict, Any, Union, List, Type, Optional

if TYPE_CHECKING:
    from baserowapi.models.table import Table
    from baserowapi.baserow import Baserow as Client
    from baserowapi.models.field import Field

from baserowapi.models.row_value import (
    RowValueList,
    RowValue,
    TextRowValue,
    LongTextRowValue,
    UrlRowValue,
    EmailRowValue,
    PhoneNumberRowValue,
    BooleanRowValue,
    RatingRowValue,
    NumberRowValue,
    BaseDateRowValue,
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

        :param Dict[str, Any] row_data: Dictionary containing the row data.
        :param Table table: The table associated with the row.
        :param Client client: The client used for making requests.
        """

        self.id = row_data.get("id")
        self.order = row_data.get("order")
        self.table: "Table" = table
        self.table_id: int = table.id
        self.client: "Client" = client
        self._row_data = row_data
        self._values = None

        self.logger.debug(f"Initialized Row id {self.id}")

    @property
    def values(self) -> RowValueList:
        """
        Retrieves the RowValueList for this row. If not yet created, it lazily loads
        the list using the stored row data.

        :return: RowValueList representing the values for this row.
        :rtype: RowValueList
        :raises Exception: If there's an error creating the RowValueList.
        """

        if self._values is None:
            try:
                row_data = self._row_data

                # remove metadata values before constructing RowValueList
                row_data.pop("id", None)
                row_data.pop("order", None)
                # construct RowValueList
                self._values = self._create_row_value_list(row_data)
                self.logger.debug(
                    f"RowValueList for Row id {self.id} successfully created."
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to create RowValueList for Row id {self.id}. Error: {e}"
                )
                raise Exception(
                    f"Unexpected error when creating RowValueList for Row id {self.id}."
                ) from e
        return self._values

    def _create_row_value_list(self, row_data: Dict[str, Any]) -> RowValueList:
        """
        Create a RowValueList based on the given row data and table fields.

        :param Dict[str, Any] row_data: Data representing the row.
        :return: RowValueList containing RowValue objects derived from the row data.
        :rtype: RowValueList
        :raises Exception: If there's an error creating a RowValue object.
        """

        row_value_objects = []
        for field_name, value in row_data.items():
            field_object = self._get_field_object(field_name)

            row_value_class = self._get_row_value_class(field_object.type)

            try:
                # Instantiate the RowValue object
                row_value_obj = row_value_class(
                    field=field_object, client=self.client, raw_value=value
                )
                row_value_objects.append(row_value_obj)
            except Exception as e:
                self.logger.error(
                    f"Failed to create RowValue object for field '{field_name}'. Error: {e}"
                )
                raise

        return RowValueList(row_value_objects)

    def _get_field_object(self, field_name: str) -> "Field":
        """
        Retrieve the corresponding Field object from the table.

        :param str field_name: The name of the field to retrieve.
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

        :param str field_type: The type of the field.
        :return: The RowValue class corresponding to the given field type.
        :rtype: Type[RowValue]
        :raises ValueError: If the specified field type is not supported.
        """

        row_value_class = ROW_VALUE_TYPE_MAPPING.get(field_type)
        if not row_value_class:
            self.logger.error(f"Field type '{field_type}' not supported.")
            raise ValueError(f"Field type '{field_type}' not supported.")
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

        :param str key: The field name to retrieve.
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

        :param str key: The field name to set.
        :param Any new_value: The value to set for the specified field.
        :note: This modifies the in-memory representation of the row.
        :raises KeyError: If the specified field name is not found in the row values or is unrecognized.
        """

        try:
            row_value = self.values[key]
            row_value.value = new_value  # Using the value setter of the RowValue object
        except KeyError:
            # Field not found in the Row's values
            self.logger.error(
                f"Attempted to set a value for an unrecognized field '{key}' in the row. Ensure the field exists in the table first."
            )
            raise KeyError(f"Field '{key}' not found in the row values.")

    def __eq__(self, other: object) -> bool:
        """
        Overridden equality method to compare two Row objects based on their id and table_id.

        :param object other: Another object to compare with this Row instance.
        :return: True if both objects are Rows and have the same id and table_id, otherwise False.
        :rtype: bool
        """

        if isinstance(other, Row):
            return getattr(self, "id", None) == getattr(other, "id", None) and getattr(
                self, "table_id", None
            ) == getattr(other, "table_id", None)
        return False

    @property
    def content(self) -> Dict[str, Any]:
        """
        Get the dictionary representation of the row's values derived from RowValue objects.

        :return: Dictionary representation of the row's values.
        :rtype: Dict[str, Any]
        """

        return {row_value.name: row_value.value for row_value in self.values}

    def update(
        self, values: Optional[Dict[str, Any]] = None, memory_only: bool = False
    ) -> "Row":
        """
        Updates the row in the table.

        :param Optional[Dict[str, Any]] values: A dictionary containing field values for updating the row. Defaults to values from the self.values property.
        :param bool memory_only: If True, only updates the in-memory row and skips the API request. Defaults to False.
        :return: A Row object representing the updated row.
        :rtype: Row
        :raises KeyError: If the specified field name is not found in the row.
        :raises Exception: If the API request results in any error responses.
        """

        try:
            # Update the RowValue objects based on the provided dictionary, if any
            if values:
                for field_name, value in values.items():
                    valid_field_names = {row_value.name for row_value in self.values}
                    if field_name not in valid_field_names:
                        self.logger.error(f"Field '{field_name}' not found in row.")
                        raise KeyError(f"Field '{field_name}' not found in row.")
                    self[field_name] = value  # Using __setitem__ to update values

            self.logger.debug(f"Constructing payload for row with ID {self.id}.")

            # Construct the API payload
            payload = {}
            for row_value in self.values:
                if not row_value.is_read_only:  # Exclude read-only values
                    payload[row_value.name] = row_value.format_for_api()

            # If memory_only is True, skip the API request
            if memory_only:
                self.logger.debug(
                    f"Memory-only update for row with ID {self.id}. Skipping API request."
                )
                return self

            # Make the API request to update the row in the Baserow table
            endpoint = f"/api/database/rows/table/{self.table_id}/{self.id}/?user_field_names=true"
            self.logger.debug(f"Sending update request to endpoint: {endpoint}.")
            response = self.client.make_api_request(
                endpoint, method="PATCH", data=payload
            )

            # The updated row data from the response
            updated_row_data = response

            # Creating a new Row object with the updated data
            updated_row = Row(
                table=self.table, client=self.client, row_data=updated_row_data
            )
            self.logger.debug(f"Successfully updated row with ID {self.id}.")

            return updated_row

        except Exception as e:
            self.logger.error(
                f"Failed to update row with ID {self.id} in table {self.table_id}. Error: {e}"
            )
            raise

    def delete(self) -> bool:
        """
        Deletes the row from the table using the Baserow delete endpoint.

        :return: True if deletion was successful.
        :rtype: bool
        :raises ValueError: If an unexpected status code is received.
        :raises Exception: For other errors during the delete operation.
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
                raise ValueError(f"Unexpected status code received: {response_code}")
        except ValueError:
            raise  # Re-raise the ValueError
        except Exception as e:
            self.logger.error(
                f"Failed to delete row with ID {self.id} from table {self.table_id}. Error: {e}"
            )
            raise

    def move(self, before_id: Optional[int] = None) -> "Row":
        """
        Moves the current row to a position before the row specified by before_id.

        :param Optional[int] before_id: The ID of the row before which the current row should be moved. If not specified, the row will be moved to the last position. Defaults to None.
        :return: A Row object representing the updated row.
        :rtype: Row
        :raises Exception: If there's an error during the move operation.
        """

        self.logger.debug(
            f"Attempting to move row with ID {self.id} in table {self.table_id}."
        )

        try:
            # Construct the endpoint for the move operation
            endpoint = f"/api/database/rows/table/{self.table_id}/{self.id}/move/?user_field_names=true"
            if before_id is not None:
                endpoint += f"&before_id={before_id}"

            # Send the API request to move the row in the Baserow table
            response = self.client.make_api_request(endpoint, method="PATCH")

            # The updated row data from the response
            moved_row_data = response

            # Creating a new Row object with the updated data
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
            raise
