from baserowapi.models.fields.field import Field


class AutonumberField(Field):
    """A read-only Baserow-assigned row number."""

    TYPE = "autonumber"
    _COMPATIBLE_FILTERS = (
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "starts_with",
        "higher_than",
        "higher_than_or_equal",
        "lower_than",
        "lower_than_or_equal",
        "is_even_and_whole",
    )

    @property
    def is_read_only(self) -> bool:
        return True
