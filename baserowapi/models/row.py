from baserowapi.validators.field_validator import FieldValidator
import logging

class Row:
    """
    Represents a row in a Baserow table. Provides methods to update and delete the row.
    """
    
    logger = logging.getLogger(__name__)

    def __init__(self, row_data, table, client):
        """
        Initializes a Row instance.

        Args:
        - row_data (dict): The data for the row.
        - table (Table): An instance of the Table object that this row belongs to.
        - client (Baserow): An instance of the Baserow client to make API requests.
        """
        self.id = row_data.get('id')
        self.order = row_data.get('order')
        self.fields = row_data
        self.table = table
        self.table_id = table.table_id
        self.client = client

    def __repr__(self):
        return f"Row id {self.id} of table {self.table_id}"
    
    def __getitem__(self, key):
        """
        Retrieve a value from the row's fields using dictionary-style access.

        Args:
            key (str): The field name to retrieve.

        Returns:
            The value of the specified field. If the field does not exist, 
            None is returned.
        """
        value = self.fields.get(key)
        if value is None:
            self.logger.warning(f"Field '{key}' not found in row.")
        return value

    def __setitem__(self, key, value):
        """
        Set a value for a specific field in the row using dictionary-style access.

        Args:
            key (str): The field name to set.
            value: The value to set for the specified field.

        Note:
            This modifies the in-memory representation of the row.
        """
        if key not in self.fields:
            self.logger.warning(f"Setting new field '{key}' in row. Consider checking field validity.")
        self.fields[key] = value
    
    def update_fields(self, fields):
        """
        Updates the in-memory fields of the row object.

        Args:
        - fields (dict): A dictionary containing the field names and values for updating the row.

        Returns:
        - None

        Raises:
        - ValueError: If a provided field doesn't exist in the current row's fields.
        """
        for key, value in fields.items():
            if key not in self.fields:
                raise ValueError(f"Field '{key}' does not exist in the current row.")
            self.fields[key] = value

    def update(self, fields=None):
        """
        Updates the row in the table using the Baserow update endpoint.

        Args:
        - fields (dict, optional): A dictionary containing the field values for updating the row.
                                Defaults to self.fields.

        Returns:
        - Row: A Row object representing the updated row.

        Raises:
        - Exception: If the API request results in any error responses.
        """
        try:
            # Defaulting fields to self.fields if not provided
            if fields is None:
                fields = self.fields

            # Add the id to the fields dictionary for validation
            fields_with_id = fields.copy()
            fields_with_id['id'] = self.id

            # Validate the fields against the table schema
            FieldValidator.validate_fields_against_table(fields_with_id, self.table, is_update=True)

            endpoint = f"/api/database/rows/table/{self.table_id}/{self.id}/?user_field_names=true"
            response = self.client.make_api_request(endpoint, method="PATCH", data=fields)

            # The updated row data from the response
            updated_row_data = response

            # Creating a new Row object with the updated data
            updated_row = Row(table=self.table, client=self.client, row_data=updated_row_data)

            return updated_row

        except Exception as e:
            self.logger.error(f"Failed to update row with ID {self.id} in table {self.table_id}. Error: {e}")
            raise


    def delete(self):
        """
        Deletes the row from the table using the Baserow delete endpoint.

        Returns:
        - bool: True if deletion was successful, otherwise raises an Exception.

        Raises:
        - Exception: If the API request results in any error responses.
        """
        try:
            endpoint = f"/api/database/rows/table/{self.table_id}/{self.id}/"
            response_code = self.client.make_api_request(endpoint, method="DELETE")
            
            if response_code == 204:
                return response_code
            else:
                raise Exception(f"Unexpected status code received: {response_code}")
        except Exception as e:
            self.logger.error(f"Failed to delete row with ID {self.id} from table {self.table_id}. Error: {e}")
            raise e

