from typing import Union, List, Any
from baserowapi.models.row_values.row_value import RowValue


class RowValueList:
    """
    A list-like container for RowValue objects.

    :ivar row_values: A list of RowValue objects.
    :vartype row_values: List[RowValue]
    """

    def __init__(self, row_values: Union[List["RowValue"], None] = None) -> None:
        """
        Initializes a RowValueList instance.

        :param row_values: A list of RowValue objects. Defaults to an empty list if not provided.
        :type row_values: Union[List[RowValue], None], optional
        """
        self.row_values = row_values if row_values else []

    def __repr__(self) -> str:
        """
        Provides a string representation of the RowValueList object.

        :return: A string representation of the RowValueList object.
        :rtype: str
        """
        max_values_to_show = 5
        value_names = [value.field.name for value in self.row_values]

        if len(value_names) > max_values_to_show:
            value_names = value_names[:max_values_to_show] + ["..."]

        values_str = ", ".join(value_names)
        return f"RowValueList({len(self.row_values)} values: [{values_str}])"

    def __getitem__(self, field_name: str) -> "RowValue":
        """
        Retrieve a RowValue object from the list by its field name.

        :param field_name: The name of the field to search for.
        :type field_name: str
        :raises KeyError: If the field name is not found in the list.
        :return: The found RowValue object.
        :rtype: RowValue
        """
        for value in self.row_values:
            if value.field.name == field_name:
                return value
        raise KeyError(f"RowValue with field name '{field_name}' not found.")

    def __iter__(self):
        """
        Allows iteration over the RowValue objects in the list.

        :return: An iterator over the RowValue objects.
        :rtype: Iterator[RowValue]
        """
        return iter(self.row_values)

    def __len__(self) -> int:
        """
        Returns the number of RowValue objects in the list.

        :return: The number of RowValue objects.
        :rtype: int
        """
        return len(self.row_values)

    def add(self, row_value: "RowValue") -> None:
        """
        Add a RowValue object to the list.

        :param row_value: The RowValue object to be added.
        :type row_value: RowValue
        :raises TypeError: If the provided object is not an instance of RowValue.
        """
        if not isinstance(row_value, RowValue):
            raise TypeError(
                "The provided object is not an instance of the RowValue class."
            )

        self.row_values.append(row_value)
