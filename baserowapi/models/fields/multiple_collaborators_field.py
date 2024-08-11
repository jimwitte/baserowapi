from typing import Any, Dict, List
from baserowapi.models.fields.field import Field


class MultipleCollaboratorsField(Field):
    """
    Represents a list of Baserow collaborators.

    :ivar TYPE: The type of the field, which is 'multiple_collaborators'.
    :vartype TYPE: str
    """

    TYPE = "multiple_collaborators"
    _COMPATIBLE_FILTERS = [
        "multiple_collaborators_has",
        "multiple_collaborators_has_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initializes a MultipleCollaboratorsField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this MultipleCollaboratorsField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def notify_user_when_added(self) -> bool:
        """
        Determine if the user should be notified when added.

        :return: True if the user should be notified, False otherwise.
        :rtype: bool
        """
        return self.field_data.get("notify_user_when_added", False)

    def validate_value(self, value: List[Dict[str, Any]]) -> None:
        """
        Validate the value for a MultipleCollaboratorsField.

        :param value: A list of dictionaries representing collaborator data.
        :type value: List[Dict[str, Any]]
        :raises ValueError: If the provided value is not a list or if the format is incorrect.
        """
        if not isinstance(value, list):
            raise ValueError(
                f"Expected a list for MultipleCollaboratorsField but got {type(value)}"
            )
        for collaborator in value:
            if not isinstance(collaborator, dict) or "id" not in collaborator:
                raise ValueError(
                    "Each collaborator in MultipleCollaboratorsField should be a dictionary with an 'id' key"
                )
