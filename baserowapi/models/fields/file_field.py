from typing import Any, Dict, List
import logging
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class FileField(Field):
    """
    Represents a field in Baserow that handles file data.

    :ivar TYPE: The type of the field, which is 'file'.
    :vartype TYPE: str
    """

    TYPE = "file"
    _COMPATIBLE_FILTERS = ["filename_contains", "has_file_type", "empty", "not_empty"]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a FileField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this FileField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    def validate_value(self, value: List[Dict[str, Any]]) -> None:
        """
        Validates the value for a FileField.

        :param value: A list of file objects to validate.
        :type value: List[Dict[str, Any]]

        :raises FieldValidationError: If the value is not a list or if a file object is missing
                            the 'name' attribute.
        """
        if not isinstance(value, list):
            self.logger.error(f"Expected a list for FileField but got {type(value)}")
            raise FieldValidationError(
                f"Expected a list for FileField but got {type(value)}"
            )

        for file_obj in value:
            if not file_obj.get("name"):
                self.logger.error("File object is missing the 'name' attribute.")
                raise FieldValidationError(
                    "File object is missing the 'name' attribute."
                )
