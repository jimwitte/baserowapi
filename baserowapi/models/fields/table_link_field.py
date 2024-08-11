from typing import Any, Dict, List, Union, Optional
from baserowapi.models.fields.field import Field


class TableLinkField(Field):
    """
    Represents a field that links to rows in another table.

    :ivar TYPE: The type of the field, which is 'link_row'.
    :vartype TYPE: str
    """

    TYPE = "link_row"
    _COMPATIBLE_FILTERS = [
        "link_row_has",
        "link_row_has_not",
        "link_row_contains",
        "link_row_not_contains",
        "empty",
        "not_empty",
    ]

    def __init__(
        self, name: str, field_data: Dict[str, Any], client: Optional[Any] = None
    ):
        """
        Initializes a TableLinkField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        :raises ValueError: If the field type doesn't match the expected type.
        """
        super().__init__(name, field_data, client)
        if self.type != self.TYPE:
            self.logger.error(
                f"Invalid type for TableLinkField. Expected {self.TYPE}, got {self.type}."
            )
            raise ValueError(
                f"Invalid type for TableLinkField. Expected {self.TYPE}, got {self.type}."
            )

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this TableLinkField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    def format_for_api(
        self, value: Union[int, str, List[Union[int, str]]]
    ) -> List[Union[int, str]]:
        """
        Format the value for API submission. This method normalizes and validates the input value,
        returning a list of IDs or values suitable for API submission.

        :param value: A single ID, a comma-separated string of names, or a list of IDs/values.
        :type value: Union[int, str, List[Union[int, str]]]
        :return: A list of IDs or values suitable for API submission.
        :rtype: List[Union[int, str]]
        :raises ValueError: If the provided value is not in an expected format.
        """
        # Normalize input into a list
        if isinstance(value, int) or (
            isinstance(value, str) and not value.strip().startswith("[")
        ):
            # Handle single ID or comma-separated string
            if isinstance(value, str) and "," in value:
                value = [v.strip() for v in value.split(",")]
            else:
                value = [value]
        elif isinstance(value, list):
            # No change needed if it's already a list
            pass
        else:
            raise ValueError(
                "The provided value should be an integer, string, or list of integers/strings."
            )

        # Validate the normalized value
        self.validate_value(value)

        # Return the value as-is after validation, as it's now guaranteed to be in the correct format
        return value

    @property
    def link_row_table_id(self) -> Optional[int]:
        """
        Retrieve the link_row_table_id of the field from field_data.

        :return: The link_row_table_id of the field.
        :rtype: Optional[int]
        """
        return self.field_data.get("link_row_table_id", None)

    @property
    def link_row_related_field_id(self) -> Optional[int]:
        """
        Retrieve the link_row_related_field_id of the field from field_data.

        :return: The link_row_related_field_id of the field.
        :rtype: Optional[int]
        """
        return self.field_data.get("link_row_related_field_id", None)

    @property
    def link_row_limit_selection_view_id(self) -> Optional[int]:
        """
        Retrieve the link_row_limit_selection_view_id of the field from field_data.

        :return: The link_row_limit_selection_view_id of the field.
        :rtype: Optional[int]
        """
        return self.field_data.get("link_row_limit_selection_view_id", None)

    def get_options(self) -> List[str]:
        """
        Fetches and returns the primary values from the related table that are possible
        for the TableLinkRowValue.

        This method retrieves the rows from the related table and extracts the primary
        field values from each row.

        :return: A list of primary field values from the related table.
        :rtype: List[str]
        :raises ValueError: If there's an error fetching the primary values from the related table.
        """
        if self.client is None:
            self.logger.error("Baserow client not provided.")
            raise ValueError("Baserow client not provided.")

        try:
            related_table = self.client.get_table(self.link_row_table_id)
            primary_field_name = related_table.primary_field
            returned_rows = related_table.get_rows(include=[primary_field_name])
            options = [row[primary_field_name] for row in returned_rows]

            self.logger.debug(
                f"Retrieved {len(options)} options for TableLinkField '{self.name}' from related table {related_table.id}"
            )
            return options
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve options for TableLinkField '{self.name}'. Error: {e}"
            )
            raise ValueError(
                f"Failed to retrieve options from the related table. Error: {e}"
            )

    def validate_value(self, value: Union[int, str, List[Union[int, str]]]) -> None:
        """
        Validate the value for the TableLinkField. Ensure it's a list of integers or strings,
        or a single integer or string that can be converted to a list.

        This method checks whether the provided value is valid according to the rules defined
        for the TableLinkField. If the value is not valid, it raises a ValueError.

        :param value: The value to be validated. It can be an integer, a string, or a list of these.
        :type value: Union[int, str, List[Union[int, str]]]
        :raises ValueError: If the value is not in the expected format.
        """
        if isinstance(value, (int, str)):
            # A single integer or string is valid, but will be converted to a list.
            value = [value]
        elif not isinstance(value, list):
            # If the value is not a list, integer, or string, it's invalid.
            self.logger.error(
                "Value provided for TableLinkField should be a list, integer, or string."
            )
            raise ValueError(
                "Value provided for TableLinkField should be a list, integer, or string."
            )
