import logging

class FieldValidator:
    """
    FieldValidator is a utility class that provides methods for validating 
    field data against a table's structure.

    Attributes:
    - METADATA_FIELDS (list[str]): A list of fields that are considered as metadata 
                                   and are not validated as regular table fields.
    - logger (Logger): Logging interface for the validator.
    """

    logger = logging.getLogger(__name__)
    METADATA_FIELDS = ['order']

    @staticmethod
    def validate_fields_against_table(fields, table, is_update=False):
        """
        Validates field data against the structure of a provided table.

        Args:
        - fields (Union[dict, list[dict]]): Field data for validation. Can be a single
                                           dictionary or a list of dictionaries.
        - table (Table): The table against which the fields are validated.
        - is_update (bool, optional): If True, assumes that the fields are meant 
                                      for updating rows and validates accordingly.
                                      Defaults to False.

        Raises:
        - ValueError: For any validation errors encountered.
        """
        valid_field_names = table.get_field_names()
        readonly_field_names = [field.name for field in table.fields if field.is_read_only]

        if is_update:
            required_metadata = ['id']
        else:
            required_metadata = []

        # Log information about the fields being validated
        FieldValidator.logger.debug(f"Validating fields against table with valid field names: {valid_field_names}")

        # Determine if we are dealing with a single dictionary or a list of dictionaries
        if isinstance(fields, list):
            for field_dict in fields:
                FieldValidator._validate_single_field_dict(field_dict, valid_field_names, readonly_field_names, required_metadata, is_update)
        else:
            FieldValidator._validate_single_field_dict(fields, valid_field_names, readonly_field_names, required_metadata, is_update)

    @staticmethod
    def _validate_single_field_dict(field_dict, valid_field_names, readonly_field_names, required_metadata, is_update):
        """
        Validates a single dictionary of field data against a list of valid field names,
        read-only fields, and required metadata fields.

        Args:
        - field_dict (dict): The dictionary of field data for validation.
        - valid_field_names (list[str]): List of valid field names for the table.
        - readonly_field_names (list[str]): List of fields that are read-only.
        - required_metadata (list[str]): List of metadata fields required for the operation.
        - is_update (bool): If True, assumes that the field_dict is meant for updating rows.

        Raises:
        - ValueError: For any validation errors encountered.
        """
        for field in required_metadata:
            if field not in field_dict:
                # Log the error
                FieldValidator.logger.error(f"Validation error: '{field}' is required for updating rows.")
                raise ValueError(f"'{field}' is required for updating rows.")

        for field_name in field_dict:
            # Skipping the validation for metadata
            if field_name in (required_metadata + FieldValidator.METADATA_FIELDS):
                continue
            if field_name not in valid_field_names:
                # Log the error
                FieldValidator.logger.error(f"Validation error: '{field_name}' is not a valid field in the table.")
                raise ValueError(f"'{field_name}' is not a valid field in the table.")
            if field_name in readonly_field_names:
                # Log the error for readonly fields
                FieldValidator.logger.error(f"Validation error: '{field_name}' is read-only and cannot be updated.")
                raise ValueError(f"'{field_name}' is read-only and cannot be updated.")
