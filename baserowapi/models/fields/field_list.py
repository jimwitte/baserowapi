from typing import List, Iterator
import logging
from baserowapi.models.fields.field import Field

class FieldList:
    """
    Represents a list of Field objects.

    :ivar fields: A list containing the Field objects.
    :vartype fields: List[Field]
    :ivar logger: A logger instance for the class.
    :vartype logger: logging.Logger
    """

    def __init__(self, fields: List[Field]) -> None:
        """
        Initialize a FieldList with a list of Field objects.

        :param fields: A list of Field objects.
        :type fields: List[Field]
        """
        self.fields = fields
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized FieldList with {len(fields)} fields.")

    def __repr__(self) -> str:
        """
        Provide a string representation of the FieldList object.

        :return: A string representing the FieldList.
        :rtype: str
        """
        max_fields_to_show = 5
        fields_names = [field.name for field in self.fields]

        if len(fields_names) > max_fields_to_show:
            fields_names = fields_names[:max_fields_to_show] + ["..."]

        fields_str = ", ".join(fields_names)
        return f"FieldList({len(self.fields)} fields: [{fields_str}])"

    def __getitem__(self, field_name: str) -> Field:
        """
        Retrieve a field by its name.

        :param field_name: The name of the desired field.
        :type field_name: str
        :return: The desired Field object.
        :rtype: Field
        :raises KeyError: If the field_name doesn't match any fields in the list.
        """
        for field in self.fields:
            if field.name == field_name:
                return field
        self.logger.error(f"Field '{field_name}' not found.")
        raise KeyError(f"Field '{field_name}' not found.")

    def __iter__(self) -> Iterator[Field]:
        """
        Return an iterator over the fields.

        :return: An iterator over the Field objects.
        :rtype: Iterator[Field]
        """
        return iter(self.fields)

    def __len__(self) -> int:
        """
        Return the number of fields in the list.

        :return: The number of fields.
        :rtype: int
        """
        return len(self.fields)

    def __contains__(self, field_name: str) -> bool:
        """
        Check if a field with the given name exists in the FieldList.

        :param field_name: The name of the field to check.
        :type field_name: str
        :return: True if the field exists, otherwise False.
        :rtype: bool
        """
        exists = any(field.name == field_name for field in self.fields)
        if not exists:
            self.logger.warning(f"Field '{field_name}' not found in FieldList.")
        return exists
