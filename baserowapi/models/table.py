from baserowapi.models.row import Row
from baserowapi.models.field import Field, FieldList
from baserowapi.validators.field_validator import FieldValidator
from baserowapi.validators.filter_validator import FilterValidator
import logging
import urllib.parse

class Table:
    def __init__(self, table_id, client):
        self.table_id = table_id
        self.client = client
        self._fields = None
        self._primary_field = None
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        """String representation of the Table object."""
        try:
            num_fields = len(self.fields)
            max_fields_to_show = 5
            field_names = [field.name for field in self.fields]
            
            if len(field_names) > max_fields_to_show:
                field_names = field_names[:max_fields_to_show] + ['...']
            
            fields_str = ', '.join(field_names)
            return f"Table(id={self.table_id}, {num_fields} fields: [{fields_str}])"
        except:
            return f"Table(id={self.table_id})"


    @property
    def primary_field(self):
        if self._primary_field is None:
            self._set_primary_field()
        return self._primary_field

    def _set_primary_field(self):
        for field in self.fields:
            if field.is_primary:
                self._primary_field = field.name
                return
        self.logger.error(f"No primary field found for table {self.table_id}.")
        raise ValueError(f"Table {self.table_id} does not have a primary field.")

    @property
    def fields(self):
        if self._fields is None:
            endpoint = f"/api/database/fields/table/{self.table_id}/"
            try:
                response = self.client.make_api_request(endpoint)
                fields_data = response
                field_objects = [Field(field_data['name'], field_data) for field_data in fields_data]
                self._fields = FieldList(field_objects)
            except Exception as e:
                self.logger.error(f"Failed to fetch fields for table {self.table_id}. Error: {e}")
                raise Exception("Unexpected error when fetching fields.") from e
        return self._fields

    def get_field_names(self):
        try:
            return [field.name for field in self.fields]
        except Exception as e:
            self.logger.error(f"Failed to get field names for table {self.table_id}. Error: {e}")
            raise

    def get_field_type(self, field_name):
        for field in self.fields:
            if field.name == field_name:
                return field.type

        self.logger.error(f"Field '{field_name}' not found in table {self.table_id}.")
        raise ValueError(f"Field '{field_name}' not found in table {self.table_id}.")

    def get_field(self, field_name):
        for field in self.fields:
            if field.name == field_name:
                return field

        self.logger.error(f"Field '{field_name}' not found in table {self.table_id}.")
        raise ValueError(f"Field '{field_name}' not found in table {self.table_id}.")

    
    def _build_request_url(self, include=None, exclude=None, search=None, order_by=None, 
                        filter_type=None, filters=None, view_id=None, page_size=None, **kwargs):
        """
        Constructs the URL for the Baserow API request based on the given parameters.

        Args:
            include (str, optional): A comma-separated list of field names to include.
            exclude (str, optional): A comma-separated list of field names to exclude.
            search (str, optional): Search string to search the table.
            order_by (list, optional): List of field names to order results by.
            filter_type (str, optional): The type of filter to apply.
            filters (list, optional): List containing the Filter objects to apply.
            view_id (int, optional): The ID of the view to apply its filters and sorts.
            page_size (int, optional): Number of rows per page for each API call.
            kwargs: Additional parameters that can be passed.

        Returns:
            str: The constructed request URL

        Raises:
            ValueError: If any of the parameters are invalid.
        """

        # Base URL construction with user_field_names=true
        base_url = f"/api/database/rows/table/{self.table_id}/?user_field_names=true"

        # Convert dictionary to query parameters
        query_params_parts = []

        # Handle include and exclude parameters, ensuring they're lists and converting to comma-separated strings
        if include:
            if not isinstance(include, list):
                self.logger.error(f"'include' should be a list, got {type(include)} instead.")
                raise ValueError("'include' parameter should be a list of field names.")
            encoded_include = urllib.parse.quote(','.join(include))
            query_params_parts.append(f"include={encoded_include}")

        if exclude:
            if not isinstance(exclude, list):
                self.logger.error(f"'exclude' should be a list, got {type(exclude)} instead.")
                raise ValueError("'exclude' parameter should be a list of field names.")
            encoded_exclude = urllib.parse.quote(','.join(exclude))
            query_params_parts.append(f"exclude={encoded_exclude}")

        # Handle search parameter, ensuring the search string is URL encoded
        if search:
            if not isinstance(search, str):
                self.logger.error(f"'search' should be a string, got {type(search)} instead.")
                raise ValueError("'search' parameter should be a string.")
            encoded_search = urllib.parse.quote(search)
            query_params_parts.append(f"search={encoded_search}")

        # Handle order_by parameter, converting the list to a comma-separated string and URL encoding
        if order_by:
            if not isinstance(order_by, list):
                self.logger.error(f"order_by should be a list, got {type(order_by)} instead.")
                raise ValueError("order_by parameter should be a list.")
            encoded_order = urllib.parse.quote(','.join(order_by))
            query_params_parts.append(f"order_by={encoded_order}")

        # Handle view_id and page_size parameters
        if view_id:
            if not isinstance(view_id, int):
                self.logger.error(f"'view_id' should be an integer, got {type(view_id)} instead.")
                raise ValueError("'view_id' parameter should be an integer.")
            query_params_parts.append(f"view_id={view_id}")

        if page_size:
            if not isinstance(page_size, int):
                self.logger.error(f"'page_size' should be an integer, got {type(page_size)} instead.")
                raise ValueError("'page_size' parameter should be an integer.")
            query_params_parts.append(f"page_size={page_size}")

        # Handle filters using the Filter objects' query_string property
        if filters:
            try:
                # Validate filters against table
                FilterValidator.validate_filters_against_table(filters, self)
            except ValueError as ve:
                self.logger.error(f"Failed filter validation for table {self.table_id}. Error: {ve}")
                raise ValueError(f"Failed filter validation for table {self.table_id}. Error: {ve}")

            for filter_obj in filters:
                query_params_parts.append(filter_obj.query_string)

        # Handle filter_type (OR or AND) if present
        if filter_type:
            if filter_type not in ["AND", "OR"]:
                self.logger.error(f"'filter_type' should be either 'AND' or 'OR', got '{filter_type}' instead.")
                raise ValueError("'filter_type' should be either 'AND' or 'OR'.")
            query_params_parts.append(f"filter_type={filter_type}")

        query_params = "&".join(query_params_parts)

        # Return the fully constructed URL with concatenated query parameters
        return f"{base_url}&{query_params}" if query_params else base_url


    def _parse_row_data(self, response_data):
        """
        Parses the raw data from the API response and transforms it into a list of Row objects.

        Args:
        - response_data (dict): The raw response data from the Baserow API.

        Returns:
        - list[Row]: List of Row objects.
        """

        if not response_data or "results" not in response_data:
            self.logger.warning("Received invalid or empty response data from the API.")
            return []

        parsed_rows = []
        for row_data in response_data["results"]:
            parsed_rows.append(Row(row_data=row_data, table=self, client=self.client))

        return parsed_rows

    class RowIterator:
        def __init__(self, table, initial_url):
            """
            Initializes the RowIterator.

            Args:
            - table (Table): The table instance.
            - initial_url (string): The initial url to pass to the table for data fetching.

            Attributes:
            - table (Table): Reference to the table.
            - params (dict): Params for the API request.
            - next_page_url (str): URL to fetch the next page.
            - current_rows (list): Rows of the current page.
            - index (int): Index for iteration over current_rows.
            """
            self.table = table
            self.initial_url = initial_url
            self.next_page_url = None
            self.current_rows = []
            self.index = 0

            self.logger = logging.getLogger(__name__)
            self.logger.debug("RowIterator initialized.")

        def _fetch_next_page(self):
            """
            Fetches the next page of data and updates self.current_rows with the new rows.
            """
            try:
                if not self.next_page_url and not self.initial_url:
                    # No more pages left to fetch
                    self.current_rows = []
                    return

                # If there's no next_page_url set, use the initial_url
                url_to_fetch = self.next_page_url if self.next_page_url else self.initial_url

                response_data = self.table.client.make_api_request(url_to_fetch)

                if not response_data:
                    self.current_rows = []
                elif 'results' not in response_data or 'next' not in response_data:
                    # Added check for missing fields in response data
                    raise Exception("Error fetching next page of rows")
                else:
                    self.next_page_url = response_data.get('next', None)
                    self.current_rows = self.table._parse_row_data(response_data)

                # Once the initial URL has been used once, we should set it to None so it's not used again
                if url_to_fetch == self.initial_url:
                    self.initial_url = None

                # Reset index to start iterating over new rows.
                self.index = 0
            except Exception as e:
                self.logger.error(f"Error fetching next page of rows: {e}")
                raise


        def __iter__(self):
            return self

        def __next__(self):
            # If there are no more rows or the index is out of range, fetch the next page.
            if not self.current_rows or self.index >= len(self.current_rows):
                self._fetch_next_page()
                
                # If after fetching, we still have no rows, it means we have iterated over all rows.
                if not self.current_rows:
                    self.logger.debug("End of rows reached.")
                    raise StopIteration

            # Get the row at the current index and increment the index.
            row = self.current_rows[self.index]
            self.index += 1
            return row

    def get_rows(self, include=None, exclude=None, search=None, order_by=None, 
                filter_type=None, filters=None, view_id=None, page_size=None, return_single=False, **kwargs):
        """
        Retrieves rows from the table using provided parameters.
        
        Args:
            include (str, optional): A comma-separated list of field names to include in the results.
            exclude (str, optional): A comma-separated list of field names to exclude from the results.
            search (str, optional): A search string to apply on the table data.
            order_by (str, optional): Field by which the results should be ordered.
            filter_type (str, optional): The type of filter to be applied.
            filters (list, optional): A list containing Filter objects to be applied.
            view_id (int, optional): ID of the view to consider its filters and sorts.
            page_size (int, optional): The number of rows per page in the response.
            return_single (bool, optional): If True, returns a single Row object instead of an iterator.
            kwargs: Additional parameters for the API request.

        Returns:
            Row or RowIterator: Depending on return_single, either a single Row object or a RowIterator.

        Raises:
            Exception: If any error occurs during the process.
        """

        # Construct the request URL with all parameters
        try:
            request_url = self._build_request_url(include=include, exclude=exclude, search=search, 
                                                order_by=order_by, filter_type=filter_type, 
                                                filters=filters, view_id=view_id, page_size=page_size, **kwargs)
        except Exception as e:
            self.logger.error(f"Error constructing request URL: {e}")
            raise Exception(f"Invalid parameters: {e}")

        if return_single:
            try:
                response_data = self.client.make_api_request(request_url)
                rows = self._parse_row_data(response_data)
                return rows[0] if rows else None
            except Exception as e:
                self.logger.error(f"Error fetching single row: {e}")
                raise e

        # Return a RowIterator for the constructed URL
        return self.RowIterator(self, initial_url=request_url)

    def get_row(self, row_id):
        """
        Fetch a specific row by its ID from the table.
        Args:
            row_id (int): The ID of the row to fetch.
        Returns:
            Row: An instance of the Row model representing the fetched row.
        """
        try:
            endpoint = f"/api/database/rows/table/{self.table_id}/{row_id}/?user_field_names=true"
            response = self.client.make_api_request(endpoint)
            row_data = response
            return Row(row_data=row_data, table=self, client=self.client)
        except Exception as e:
            self.logger.error(f"Failed to get row with ID {row_id} from table {self.table_id}. Error: {e}")
            raise

    def add_row(self, fields):
        """
        Add a new row (or multiple rows) to the table.
        Args:
            fields (dict or list[dict]): A dictionary representing the fields of the row 
                                        to add or a list of dictionaries for multiple rows.
        Returns:
            Row or list[Row]: An instance of the Row model representing the added row or 
                            a list of Row instances for multiple rows.
        """
        try:
            FieldValidator.validate_fields_against_table(fields, self)
            if isinstance(fields, list):
                endpoint = f"/api/database/rows/table/{self.table_id}/batch/?user_field_names=true"
                response = self.client.make_api_request(endpoint, method="POST", data={'items': fields})
                rows_data = response
                added_rows = rows_data['items']
                return [Row(row_data=row_data, table=self, client=self.client) for row_data in added_rows]
            else:
                endpoint = f"/api/database/rows/table/{self.table_id}/?user_field_names=true"
                response = self.client.make_api_request(endpoint, method="POST", data=fields)
                row_data = response
                return Row(row_data=row_data, table=self, client=self.client)
        except Exception as e:
            error_message = f"Failed to add row to table {self.table_id}. Error: {e}"
            self.logger.error(error_message)
            raise Exception(error_message)

    def update_rows(self, rows_data):
        """
        Updates multiple rows in the table using the Baserow batch update endpoint.

        Args:
        - rows_data (list[Union[dict, Row]]): A list of dictionaries or Row objects. 
        Each dictionary should contain the field values for updating a specific row and 
        include the ID of the row to be updated.

        Returns:
        - list[Row]: A list of Row objects representing the updated rows.

        Raises:
        - Exception: If the API request results in any error responses.
        - TypeError: If an item in rows_data is neither a dictionary nor a Row object.
        """
        if not rows_data:
            warning_msg = "The rows_data list is empty. Nothing to update."
            self.logger.warning(warning_msg)
            raise ValueError(warning_msg)

        # Convert Row objects to dictionaries
        formatted_data = []
        for item in rows_data:
            if isinstance(item, dict):
                formatted_data.append(item)
            elif isinstance(item, Row):
                row_data = item.fields.copy()  # Extract fields from the Row object
                row_data["id"] = item.id  # Ensure the row ID is also included
                formatted_data.append(row_data)
            else:
                raise TypeError(f"Unsupported type {type(item)} in rows_data. Expected dict or Row object.")

        try:
            FieldValidator.validate_fields_against_table(formatted_data, self, is_update=True)
            endpoint = f"/api/database/rows/table/{self.table_id}/batch/?user_field_names=true"
            response = self.client.make_api_request(endpoint, method="PATCH", data={'items': formatted_data})

            # Convert the response to a list of Row objects
            updated_rows = [Row(row_data=item, table=self, client=self.client) for item in response['items']]
            
            return updated_rows
        except Exception as e:
            self.logger.error(f"Failed to update rows in table {self.table_id}. Error: {e}")
            raise

    def delete_rows(self, rows_data):
        """
        Deletes multiple rows from the table using the Baserow batch-delete endpoint.

        Args:
        - rows_data (list[Union[Row, dict]]): A list of Row objects or dictionaries. 
        Each dictionary should include the ID of the row to be deleted.

        Returns:
        - int: HTTP status code of the API response.

        Raises:
        - Exception: If the API request results in any error responses.
        - TypeError: If an invalid input type is provided.
        """
        # Convert Row objects to their respective IDs
        row_ids = []
        for item in rows_data:
            if isinstance(item, Row):
                row_ids.append(item.id)
            elif isinstance(item, dict) and "id" in item:
                row_ids.append(item["id"])
            else:
                raise TypeError(f"Unsupported type {type(item)} in rows_data. Expected Row object or dict with an 'id' key.")

        if not row_ids:
            raise ValueError("The rows_data list is empty. Nothing to delete.")

        try:
            endpoint = f"/api/database/rows/table/{self.table_id}/batch-delete/"
            response = self.client.make_api_request(endpoint, method="POST", data={'items': row_ids})
            return response
        except Exception as e:
            self.logger.error(f"Failed to delete rows from table {self.table_id}. Error: {e}")
            raise

