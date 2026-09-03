from baserowapi.models.fields.base_text_class import BaseTextClass


class UrlField(BaseTextClass):
    """
    Represents a URL field in Baserow.

    :ivar TYPE: The type of the field, which is 'url'.
    :vartype TYPE: str
    """

    TYPE = "url"
