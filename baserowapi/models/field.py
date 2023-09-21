import logging

class Field:
    def __init__(self, name, field_data):
        """
        Initialize a Field object.

        :param name: Name of the field.
        :param field_data: Dictionary containing data about the field.
        """
        self.logger = logging.getLogger(__name__)

        if not field_data or not isinstance(field_data, dict):
            self.logger.error("Invalid field data provided for Field initialization.")
            raise ValueError("Field data should be a non-empty dictionary.")

        self.name = name
        self.field_data = field_data

    def __repr__(self):
        """String representation of the Field instance."""
        return f"Baserow field '{self.name}' with id {self.id} of table {self.table_id}"

    def __getitem__(self, key):
        """Support dictionary-style getting of attributes."""
        try:
            return self.field_data[key]
        except KeyError:
            self.logger.error(f"Attribute '{key}' not found in field '{self.name}'.")
            raise KeyError(f"Attribute '{key}' not found in field '{self.name}'.")

    @property
    def attributes(self):
        """Retrieve all attributes from field data."""
        return self.field_data

    @property
    def id(self):
        """Retrieve the id of the field from field_data."""
        field_id = self.field_data.get('id', None)
        if field_id is None:
            self.logger.warning(f"Field ID missing for field {self.name}.")
        return field_id

    @property
    def table_id(self):
        """Retrieve the table_id of the field from field_data."""
        table_id = self.field_data.get('table_id', None)
        if table_id is None:
            self.logger.warning(f"Table ID missing for field {self.name}.")
        return table_id

    @property
    def order(self):
        """Retrieve the order of the field from field_data."""
        order = self.field_data.get('order', None)
        if order is None:
            self.logger.warning(f"Order missing for field {self.name}.")
        return order

    @property
    def type(self):
        """Retrieve the type of the field from field_data."""
        field_type = self.field_data.get('type', None)
        if field_type is None:
            self.logger.warning(f"Field type missing for field {self.name}.")
        return field_type

    @property
    def is_primary(self):
        """Determine if the field is primary."""
        primary = self.field_data.get('primary', False)
        return primary

    @property
    def is_read_only(self):
        """Determine if the field is read-only."""
        read_only = self.field_data.get('read_only', False)
        return read_only

class FieldList:
    def __init__(self, fields):
        self.fields = fields

    def __repr__(self):
        """String representation of the FieldList object."""
        max_fields_to_show = 5
        fields_names = [field.name for field in self.fields]
        
        if len(fields_names) > max_fields_to_show:
            fields_names = fields_names[:max_fields_to_show] + ['...']
        
        fields_str = ', '.join(fields_names)
        return f"FieldList({len(self.fields)} fields: [{fields_str}])"

    def __getitem__(self, field_name):
        for field in self.fields:
            if field.name == field_name:
                return field
        raise KeyError(f"Field '{field_name}' not found.")

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)
