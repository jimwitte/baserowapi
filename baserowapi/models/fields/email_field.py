from baserowapi.models.fields.base_text_class import BaseTextClass


class EmailField(BaseTextClass):
    """
    Represents an email field in Baserow.

    :ivar TYPE: The type of the field, which is 'email'.
    :vartype TYPE: str
    """

    TYPE = "email"
