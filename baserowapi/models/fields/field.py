from typing import Any, Dict, Union
import logging

from baserowapi.exceptions import InvalidOperatorError
from baserowapi.models.filter import FilterCompatibility, KNOWN_FILTER_OPERATORS


class Field:
    """
    Represents a field in Baserow and provides methods to interact with its properties.
    """

    _COMPATIBLE_FILTERS: tuple[str, ...] = ()

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a Field object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        :raises ValueError: If the name is empty or if field_data is not a valid dictionary.
        """
        self.logger = logging.getLogger(__name__)

        if not name:
            self.logger.error("Name not provided for Field initialization.")
            raise ValueError("Name should not be empty.")

        if not field_data or not isinstance(field_data, dict):
            self.logger.error("Invalid field data provided for Field initialization.")
            raise ValueError("Field data should be a non-empty dictionary.")

        self.name = name
        self.field_data = field_data
        self.client = client
        self.logger.debug(
            f"Initialized field '{self.name}' with attributes '{self.field_data}'"
        )

    def __repr__(self) -> str:
        """
        Provide a string representation of the Field object.

        :return: String representation of the Field.
        :rtype: str
        """
        return f"Baserow field '{self.name}' with id '{self.id}' of type '{self.type}' of table '{self.table_id}'"

    def __getitem__(self, key: str) -> Any:
        """
        Retrieve an attribute from field_data.

        :param key: The attribute's key.
        :type key: str
        :return: The desired attribute.
        :rtype: Any
        :raises KeyError: If the key doesn't exist in field_data.
        """
        try:
            return self.field_data[key]
        except KeyError:
            self.logger.error(f"Attribute '{key}' not found in field '{self.name}'.")
            raise

    def validate_value(self, value: Any) -> None:
        """
        Validate the value against the field's criteria.

        Child classes can override for custom rules.

        :param value: The value to be validated.
        :type value: Any
        """
        pass

    def decode_value(self, raw_value: Any) -> Any:
        """Decode a raw Baserow response value for ordinary row access.

        Unknown and scalar values are lossless pass-through values unless a
        field subclass defines a Baserow-specific structured representation.
        """
        return raw_value

    def encode_value(self, value: Any) -> Any:
        """Validate and encode a caller value for the Baserow API."""
        self.validate_value(value)
        return value

    def filter_compatibility(self, operator: str) -> FilterCompatibility:
        """Return advisory compatibility without blocking unknown operators."""
        if not isinstance(operator, str) or not operator.strip():
            raise InvalidOperatorError("operator must be a non-empty string.")
        if operator in getattr(self, "compatible_filters", ()):
            return FilterCompatibility.SUPPORTED
        if operator in KNOWN_FILTER_OPERATORS:
            return FilterCompatibility.UNSUPPORTED
        return FilterCompatibility.UNKNOWN

    @property
    def compatible_filters(self) -> tuple[str, ...]:
        """Return immutable advisory filter names documented for this Field."""
        return tuple(self._COMPATIBLE_FILTERS)

    def format_for_api(self, value: Any) -> Any:
        """Compatibility alias for :meth:`encode_value`.

        :param value: The value to be formatted for the API.
        :type value: Any
        :return: The formatted value.
        :rtype: Any
        """
        return self.encode_value(value)

    @property
    def id(self) -> Union[int, None]:
        """
        Retrieve the ID of the field.

        :return: The ID of the field or None if not present.
        :rtype: Union[int, None]
        """
        field_id = self.field_data.get("id", None)
        if field_id is None:
            self.logger.warning(f"Field ID missing for field {self.name}.")
        return field_id

    @property
    def table_id(self) -> Union[int, None]:
        """
        Retrieve the table ID associated with the field.

        :return: The table ID or None if not present.
        :rtype: Union[int, None]
        """
        table_id = self.field_data.get("table_id", None)
        if table_id is None:
            self.logger.warning(f"Table ID missing for field {self.name}.")
        return table_id

    @property
    def order(self) -> Union[int, None]:
        """
        Retrieve the order of the field.

        :return: The order of the field or None if not present.
        :rtype: Union[int, None]
        """
        order = self.field_data.get("order", None)
        if order is None:
            self.logger.warning(f"Order missing for field {self.name}.")
        return order

    @property
    def type(self) -> Union[str, None]:
        """
        Retrieve the type of the field.

        :return: The type of the field or None if not present.
        :rtype: Union[str, None]
        """
        field_type = self.field_data.get("type", None)
        if field_type is None:
            self.logger.warning(f"Field type missing for field {self.name}.")
        return field_type

    @property
    def is_primary(self) -> bool:
        """
        Determine if the field is primary.

        :return: True if the field is primary, otherwise False.
        :rtype: bool
        """
        return self.field_data.get("primary", False)

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the field is read-only.

        :return: True if the field is read-only, otherwise False.
        :rtype: bool
        """
        return self.field_data.get("read_only", False)
