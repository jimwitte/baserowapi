from typing import Any, Dict, List, Optional
from baserowapi.models.fields.field import Field


class FormulaField(Field):
    """
    Represents a field that computes its value based on a formula.

    :ivar TYPE: The type of the field, which is 'formula'.
    :vartype TYPE: str
    """

    TYPE = "formula"
    _COMPATIBLE_FILTERS = []

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initializes a FormulaField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)

        # Attributes specific to the FormulaField
        self._formula = field_data.get("formula")
        self._formula_type = field_data.get("formula_type")
        self._error = field_data.get("error")
        self._array_formula_type = field_data.get("array_formula_type")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this FormulaField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def formula(self) -> Optional[str]:
        """
        Retrieve the formula of the field.

        :return: The formula of the field.
        :rtype: Optional[str]
        """
        return self._formula

    @property
    def formula_type(self) -> Optional[str]:
        """
        Retrieve the formula type of the field.

        :return: The formula type of the field.
        :rtype: Optional[str]
        """
        return self._formula_type

    @property
    def error(self) -> Optional[str]:
        """
        Retrieve the error (if any) associated with the formula.

        :return: The error associated with the formula.
        :rtype: Optional[str]
        """
        return self._error

    @property
    def array_formula_type(self) -> Optional[str]:
        """
        Retrieve the array formula type of the field.

        :return: The array formula type of the field.
        :rtype: Optional[str]
        """
        return self._array_formula_type

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the field is read-only.

        :return: Always returns True for a FormulaField.
        :rtype: bool
        """
        return True
