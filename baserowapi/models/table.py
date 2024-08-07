from typing import TYPE_CHECKING, List, Union, Optional, Dict, Any

from baserowapi.models.filter import Filter
from baserowapi.models.row import Row
from baserowapi.models.field import (
    Field,
    FieldList,
    TextField,
    LongTextField,
    BooleanField,
    NumberField,
    RatingField,
    DateField,
    LastModifiedField,
    CreatedOnField,
    UrlField,
    EmailField,
    FileField,
    SingleSelectField,
    MultipleSelectField,
    PhoneNumberField,
    FormulaField,
    TableLinkField,
    CountField,
    LookupField,
    MultipleCollaboratorsField,
    GenericField,
    PasswordField
)
from baserowapi.validators.filter_validator import FilterValidator
import logging
import urllib.parse
import json
import re

if TYPE_CHECKING:
    from baserowapi import Baserow


class Table:
    """
    Represents a table in Baserow with functionalities to manipulate and query rows, fields, etc.
    """

    FIELD_TYPE_CLASS_MAP: Dict[str, type] = {
        TextField.TYPE: TextField,
        LongTextField.TYPE: LongTextField,
        BooleanField.TYPE: BooleanField,
        NumberField.TYPE: NumberField,
        RatingField.TYPE: RatingField,
        DateField.TYPE: DateField,
        LastModifiedField.TYPE: LastModifiedField,
        CreatedOnField.TYPE: CreatedOnField,
        UrlField.TYPE: UrlField,
        EmailField.TYPE: EmailField,
        FileField.TYPE: FileField,
        SingleSelectField.TYPE: SingleSelectField,
        MultipleSelectField.TYPE: MultipleSelectField,
        PhoneNumberField.TYPE: PhoneNumberField,
        FormulaField.TYPE: FormulaField,
        TableLinkField.TYPE: TableLinkField,
        CountField.TYPE: CountField,
        LookupField.TYPE: LookupField,
        MultipleCollaboratorsField.TYPE: MultipleCollaboratorsField,
        GenericField.TYPE: GenericField,
        PasswordField.TYPE: PasswordField
    }

    def __init__(self, table_id: int, client: "Baserow"):
        """
        Initialize a Table object.

        :param table_id: The unique identifier for the table.
        :param client: The Baserow client instance to make API requests.
        """
        self.id = table_id
        self.client = client
        self._fields = None
        self._primary_field = None
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized Table id {self.id}")

    def __repr__(self) -> str:
        """
        Provide a string representation of the Table object.

        :return: A string describing the Table object, including its ID.
        """
        return f"Table(id={self.id})"

    @staticmethod
    def _field_class_from_data(field_data: Dict[str, Any]) -> type:
        """
        Determine the appropriate Field class based on the provided field data.

        Given the data for a field, this method determines the most suitable
        class to represent the field, using the field's type as a key to look it up.
        If the field's type isn't recognized, it defaults to the base Field class.

        :param field_data: A dictionary containing field data, especially the 'type' key.
        :type field_data: dict
        :return: The class (not an instance) best suited to represent the field.
        :rtype: type
        """
        field_type = field_data.get("type")
        return Table.FIELD_TYPE_CLASS_MAP.get(
            field_type, GenericField
        )  # Default to base Field class if type not found

    @property
    def fields(self) -> FieldList:
        """
        Retrieve the fields associated with the table.

        If the fields haven't been fetched yet, this property sends an API request
        to retrieve them. Once retrieved, the fields are cached to avoid unnecessary
        API requests in subsequent calls.

        :return: A FieldList containing all the Field objects associated with this table.
        :rtype: FieldList
        :raises Exception: If there's an unexpected error when fetching the fields.
        """
        if self._fields is None:
            endpoint = f"/api/database/fields/table/{self.id}/"
            try:
                response = self.client.make_api_request(endpoint)
                fields_data = response
                field_objects = []
                for fd in fields_data:
                    FieldClass = self._field_class_from_data(fd)
                    field_objects.append(FieldClass(fd["name"], fd, client=self.client))
                self._fields = FieldList(field_objects)
            except Exception as e:
                self.logger.error(f"Failed to fetch fields for table {self.id}. Error: {e}")
                raise Exception("Unexpected error when fetching fields.") from e
        return self._fields

    @property
    def primary_field(self) -> str:
        """
        Retrieve the primary field of the table.

        If the primary field hasn't been determined yet, this property will
        invoke the method to set it. Once set, the primary field is cached
        to avoid unnecessary computations in subsequent calls.

        :return: The primary field of the table.
        :rtype: str
        """
        if self._primary_field is None:
            self._set_primary_field()
        return self._primary_field

    def _set_primary_field(self) -> None:
        """
        Set the primary field of the table.

        This method iterates through all the fields of the table to find
        the primary field. Once found, it sets the `_primary_field` attribute
        with the name of that field.

        :raises ValueError: If no primary field is found for the table.
        """
        for field in self.fields:
            if field.is_primary:
                self._primary_field = field.name
                return
        self.logger.error(f"No primary field found for table {self.id}.")
        raise ValueError(f"Table {self.id} does not have a primary field.")

    @property
    def field_names(self) -> List[str]:
        """
        Retrieve the names of all fields in the table, sorted by field.order.

        :return: A list of field names.
        :rtype: List[str]
        :raises Exception: If there's an error while fetching the field names.
        """
        try:
            # Sort fields based on 'order' property
            # If 'order' is None, sort those fields last
            sorted_fields = sorted(
                self.fields, key=lambda field: (field.order is None, field.order)
            )

            return [field.name for field in sorted_fields]
        except Exception as e:
            self.logger.error(
                f"Failed to get field names for table {self.id}. Error: {e}"
            )
            raise

    def _build_request_url(
        self,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        search: Optional[str] = None,
        order_by: Optional[List[str]] = None,
        filter_type: Optional[str] = None,  # Set to None initially
        filters: Optional[List[Filter]] = None,
        view_id: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        Constructs the URL for the Baserow API request based on the given parameters.
        """
        # Base URL construction with user_field_names=true
        base_url = f"/api/database/rows/table/{self.id}/?user_field_names=true"

        # Convert dictionary to query parameters
        query_params_parts = []

        # Handle include and exclude parameters, ensuring they're lists and converting to comma-separated strings
        if include:
            if not isinstance(include, list):
                self.logger.error(
                    "'include' should be a list, got {type(include)} instead."
                )
                raise ValueError("'include' parameter should be a list of field names.")
            encoded_include = urllib.parse.quote(",".join(include))
            query_params_parts.append(f"include={encoded_include}")

        if exclude:
            if not isinstance(exclude, list):
                self.logger.error(
                    "'exclude' should be a list, got {type(exclude)} instead."
                )
                raise ValueError("'exclude' parameter should be a list of field names.")
            encoded_exclude = urllib.parse.quote(",".join(exclude))
            query_params_parts.append(f"exclude={encoded_exclude}")

        # Handle search parameter, ensuring the search string is URL encoded
        if search:
            if not isinstance(search, str):
                self.logger.error(
                    "'search' should be a string, got {type(search)} instead."
                )
                raise ValueError("'search' parameter should be a string.")
            encoded_search = urllib.parse.quote(search)
            query_params_parts.append(f"search={encoded_search}")

        # Handle order_by parameter, converting the list to a comma-separated string and URL encoding
        if order_by:
            if not isinstance(order_by, list):
                self.logger.error(
                    "order_by should be a list, got {type(order_by)} instead."
                )
                raise ValueError("order_by parameter should be a list.")
            encoded_order = urllib.parse.quote(",".join(order_by))
            query_params_parts.append(f"order_by={encoded_order}")

        # Handle view_id and size parameters
        if view_id:
            if not isinstance(view_id, int):
                self.logger.error(
                    "'view_id' should be an integer, got {type(view_id)} instead."
                )
                raise ValueError("'view_id' parameter should be an integer.")
            query_params_parts.append(f"view_id={view_id}")

        if size:
            if not isinstance(size, int):
                self.logger.error(
                    "'size' should be an integer, got {type(size)} instead."
                )
                raise ValueError("'size' parameter should be an integer.")
            query_params_parts.append(f"size={size}")

        # Handle filters using the Filter objects' query_string property
        if filters:
            if not isinstance(filters, list) or not all(
                isinstance(f, Filter) for f in filters
            ):
                self.logger.error("filters should be a list of Filter objects.")
                raise ValueError(
                    "filters parameter should be a list of Filter objects."
                )

            # Ensure filter_type defaults to "AND" if not specified
            if filter_type is None:
                filter_type = "AND"

            # Validate the filter_type
            if filter_type not in ["AND", "OR"]:
                self.logger.error(
                    f"'filter_type' should be either 'AND' or 'OR', got '{filter_type}' instead."
                )
                raise ValueError("'filter_type' should be either 'AND' or 'OR'")

            # Construct the filter tree
            filter_dicts = [
                {"field": f.field_name, "type": f.operator, "value": f.value}
                for f in filters
            ]
            filter_tree = {
                "filter_type": filter_type,
                "filters": filter_dicts,
                "groups": [],
            }

            # Log the filter tree before encoding
            self.logger.debug(f"Filter tree: {filter_tree}")

            # Serialize and URL encode the filter tree
            filter_string = urllib.parse.quote(json.dumps(filter_tree))
            query_params_parts.append(f"filters={filter_string}")

        query_params = "&".join(query_params_parts)

        # Return the fully constructed URL with concatenated query parameters
        full_request_url = f"{base_url}&{query_params}" if query_params else base_url
        self.logger.debug(f"built request url: '{full_request_url}'")
        return full_request_url

    def _parse_row_data(self, response_data: Dict[str, Any]) -> List[Row]:
        """
        Parses the raw data from the API response and transforms it into a list of Row objects.

        :param response_data: The raw response data from the Baserow API.
        :type response_data: dict
        :return: List of Row objects.
        :rtype: list[Row]
        """

        if not response_data or "results" not in response_data:
            self.logger.warning("Received invalid or empty response data from the API.")
            return []

        parsed_rows = []
        for row_data in response_data["results"]:
            parsed_rows.append(Row(row_data=row_data, table=self, client=self.client))

        return parsed_rows

    class RowIterator:
        """
        An iterator class to iterate over rows fetched from Baserow, handling pagination and next page fetches.
        """

        MAX_CONSECUTIVE_EMPTY_FETCHES = 5

        def __init__(self, table: "Table", initial_url: str, fetch_data_fn=None) -> None:
            self.table = table
            self.initial_url = initial_url
            self.next_page_url: Optional[str] = None
            self.current_rows: List[Row] = []
            self.index = 0
            self.empty_fetch_count = 0
            self.logger = logging.getLogger(__name__)
            self.logger.debug(
                "RowIterator initialized with initial URL: %s", self.initial_url
            )

            # Use the provided fetch function or default to the table's method
            self.fetch_data_fn = fetch_data_fn or self.table.client.make_api_request

            # Store the initial state for resetting
            self._initial_state = {
                "initial_url": initial_url,
                "next_page_url": None,
                "current_rows": [],
                "index": 0,
                "empty_fetch_count": 0,
            }

        def _fetch_next_page(self) -> None:
            if not self.current_rows or self.index >= len(self.current_rows):
                if not self.next_page_url and not self.initial_url:
                    # No more pages left to fetch
                    self.current_rows = []
                    return

                url_to_fetch = self.next_page_url or self.initial_url

                try:
                    response_data = self.fetch_data_fn(url_to_fetch)
                except Exception as e:
                    self.logger.error(
                        f"API fetch failed for URL {url_to_fetch}. Error: {e}"
                    )
                    self.current_rows = []
                    return

                if response_data and "results" in response_data:
                    self.next_page_url = response_data.get("next", None)
                    self.current_rows = self.table._parse_row_data(response_data)
                else:
                    self.logger.warning(
                        f"Received unexpected response data: {response_data}"
                    )
                    self.current_rows = []

                if url_to_fetch == self.initial_url:
                    self.initial_url = None

                if not self.current_rows:
                    self.empty_fetch_count += 1
                    if self.empty_fetch_count > self.MAX_CONSECUTIVE_EMPTY_FETCHES:
                        self.logger.error(
                            f"Reached maximum consecutive empty fetches ({self.MAX_CONSECUTIVE_EMPTY_FETCHES}). Stopping iteration."
                        )
                        raise StopIteration

                self.index = 0

        def __iter__(self) -> "Table.RowIterator":
            """Returns the iterator instance."""
            return self

        def __next__(self) -> Row:
            """
            Returns the next row in the iterator. Fetches the next page of rows if necessary.
            """
            if not self.current_rows or self.index >= len(self.current_rows):
                self._fetch_next_page()

                if not self.current_rows:
                    self.logger.debug("End of rows reached.")
                    raise StopIteration

            row = self.current_rows[self.index]
            self.index += 1
            return row

        def reset(self) -> None:
            """
            Resets the iterator to its initial state.
            """
            self.initial_url = self._initial_state["initial_url"]
            self.next_page_url = self._initial_state["next_page_url"]
            self.current_rows = self._initial_state["current_rows"]
            self.index = self._initial_state["index"]
            self.empty_fetch_count = self._initial_state["empty_fetch_count"]
            self.logger.debug("RowIterator reset.")

        def reset_index(self) -> None:
            """
            Resets the iterator's index to the beginning without refetching data from the API.
            """
            self.index = 0
            self.logger.debug("RowIterator index reset to 0.")

    def get_rows(
        self,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        search: Optional[str] = None,
        order_by: Optional[List[str]] = None,
        filter_type: Optional[str] = None,
        filters: Optional[List[str]] = None,
        view_id: Optional[int] = None,
        size: Optional[int] = None,
        return_single: bool = False,
        **kwargs,
    ) -> Union[Row, "Table.RowIterator"]:
        """
        Retrieves rows from the table using provided parameters.

        :param include: A list of field names to include in the results.
        :type include: list, optional
        :param exclude: A list of field names to exclude from the results.
        :type exclude: list, optional
        :param search: A search string to apply on the table data.
        :type search: str, optional
        :param order_by: Field by which the results should be ordered.
        :type order_by: list, optional
        :param filter_type: The type of filter to be applied.
        :type filter_type: str, optional
        :param filters: A list containing Filter objects to be applied.
        :type filters: list, optional
        :param view_id: ID of the view to consider its filters and sorts.
        :type view_id: int, optional
        :param size: The number of rows per page in the response.
        :type size: int, optional
        :param return_single: If True, returns a single Row object instead of an iterator.
        :type return_single: bool, optional
        :param kwargs: Additional parameters for the API request.
        :type kwargs: dict

        :return: Depending on return_single, either a single Row object or a RowIterator.
        :rtype: Union[Row, RowIterator]

        :raises Exception: If any error occurs during the process.
        :raises ValueError: If parameters are not valid.
        """

        # Construct the request URL with all parameters
        try:
            request_url = self._build_request_url(
                include=include,
                exclude=exclude,
                search=search,
                order_by=order_by,
                filter_type=filter_type,
                filters=filters,
                view_id=view_id,
                size=size,
                **kwargs,
            )
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

    def get_row(self, row_id: Union[int, str]) -> Row:
        """
        Retrieve a specific row by its ID from the table.

        :param row_id: The unique identifier of the row to retrieve.
        :type row_id: int or str
        :return: An instance of the Row model representing the fetched row.
        :rtype: Row
        :raises ValueError: If the provided row_id is not valid.
        :raises Exception: If there's any error during the API request or if the row is not found.
        """
        # Validate the row_id
        if not row_id:
            raise ValueError("The provided row_id is not valid.")

        # Ensure fields are fetched
        # _ = self.fields

        # Construct the API endpoint to retrieve the specific row
        endpoint = f"/api/database/rows/table/{self.id}/{row_id}/?user_field_names=true"

        try:
            response = self.client.make_api_request(endpoint)
            # Return a Row object initialized with the fetched data
            return Row(row_data=response, table=self, client=self.client)

        except Exception as e:
            error_message = f"Failed to retrieve row with ID {row_id} from table {self.id}. Error: {e}"
            self.logger.error(error_message)
            raise Exception(error_message)

    def add_row(
        self,
        rows_data: Union[Dict[str, Any], List[Dict[str, Any]]],
        batch_size: Optional[int] = None,
    ) -> Union[Row, List[Row]]:
        """
        Add a new row (or multiple rows) to the table.

        :param rows_data: A dictionary representing the fields and values
                        of the row to add, or a list of dictionaries for
                        adding multiple rows.
        :type rows_data: dict or list[dict]

        :param batch_size: The number of rows to include in each batch request when adding multiple rows.
                        Defaults to the client's batch_size.
        :type batch_size: int

        :return: An instance of the Row model representing the added row or
                a list of Row instances for multiple rows.
        :rtype: Row or list[Row]

        :raises ValueError: If parameters are not valid.
        :raises Exception: If there's any error during the API request.
        """

        def _add_rows_chunk(chunk):
            """
            Helper function to add a chunk of rows.
            """
            api_endpoint = (
                f"/api/database/rows/table/{self.id}/batch/?user_field_names=true"
            )
            data_payload = {"items": chunk}
            response = self.client.make_api_request(
                api_endpoint, method="POST", data=data_payload
            )
            return [
                Row(row_data=row_data_item, table=self, client=self.client)
                for row_data_item in response["items"]
            ]

        if isinstance(rows_data, dict):
            # Single row addition
            api_endpoint = f"/api/database/rows/table/{self.id}/?user_field_names=true"
            data_payload = rows_data
            try:
                response = self.client.make_api_request(
                    api_endpoint, method="POST", data=data_payload
                )
                return Row(row_data=response, table=self, client=self.client)
            except Exception as e:
                error_message = f"Failed to add row to table {self.id}. Error: {e}"
                self.logger.error(error_message)
                raise Exception(error_message)
        elif isinstance(rows_data, list):
            # Multiple rows addition with batching
            if batch_size is None:
                batch_size = self.client.batch_size

            added_rows = []
            for i in range(0, len(rows_data), batch_size):
                chunk = rows_data[i : i + batch_size]
                try:
                    added_rows.extend(_add_rows_chunk(chunk))
                except Exception as e:
                    error_message = f"Failed to add row(s) to table {self.id}. Error: {e}"
                    self.logger.error(error_message)
                    raise Exception(error_message)
            return added_rows
        else:
            raise ValueError(
                "Invalid input: rows_data must be a dictionary or a list of dictionaries."
            )

    def update_rows(
        self,
        rows_data: Union[List[Union[Dict[str, Any], Row]], RowIterator],
        batch_size: Optional[int] = None,
    ) -> List[Row]:
        """
        Updates multiple rows in the table using the Baserow batch update endpoint.

        :param rows_data: A list of dictionaries or Row objects, or a RowIterator.
                        Each dictionary should contain the field values for updating
                        a specific row and include the ID of the row to be updated.
                        Row objects represent the rows to be updated.
        :type rows_data: list[Union[dict, Row]] or RowIterator
        :param batch_size: The number of rows to process in each batch.
        :type batch_size: int

        :return: A list of Row objects representing the updated rows.
        :rtype: list[Row]

        :raises ValueError: If parameters are not valid.
        :raises KeyError: If a dictionary contains a key that doesn't correspond to any field in the table or is missing the 'id' key.
        :raises TypeError: If an item in rows_data is neither a dictionary nor a Row object.
        :raises Exception: If the API request results in any error responses.
        """

        if not rows_data:
            warning_msg = "The rows_data list is empty. Nothing to update."
            self.logger.warning(warning_msg)
            raise ValueError(warning_msg)

        # Handle RowIterator input by converting it to a list
        if isinstance(rows_data, Table.RowIterator):
            rows_data = list(rows_data)

        # Convert Row objects to dictionaries and validate dictionaries
        formatted_data = []
        for item in rows_data:
            if isinstance(item, dict):
                if "id" not in item:
                    raise KeyError(
                        "The 'id' key is missing, which is required for updating a row."
                    )

                for key, value in item.items():
                    if key == "id":
                        continue

                    if key == "order":
                        if not isinstance(value, (int, float)) or value <= 0:
                            raise ValueError(
                                f"Invalid 'order' value: {value}. 'order' should be a positive numeric value."
                            )
                        continue

                    if key not in self.fields:
                        raise KeyError(f"Field '{key}' not found in table fields.")

                    field_object = self.fields[key]

                    if field_object.is_read_only:
                        raise ValueError(
                            f"Field '{key}' is read-only and cannot be updated."
                        )

                    try:
                        field_object.validate_value(value)
                    except ValueError as ve:
                        raise ValueError(f"Invalid value for field '{key}': {ve}") from ve

                formatted_data.append(item)

            elif isinstance(item, Row):
                row_data = {"id": item.id}
                for rv in item.values:
                    if not rv.is_read_only:
                        row_data[rv.name] = rv.format_for_api()
                formatted_data.append(row_data)

            else:
                raise TypeError(
                    f"Unsupported type {type(item)} in rows_data. Expected dict or Row object."
                )

        try:
            endpoint = f"/api/database/rows/table/{self.id}/batch/?user_field_names=true"
            updated_rows = []

            # Process in batches
            if batch_size is None:
                batch_size = self.client.batch_size

            for i in range(0, len(formatted_data), batch_size):
                batch_data = formatted_data[i : i + batch_size]
                response = self.client.make_api_request(
                    endpoint, method="PATCH", data={"items": batch_data}
                )

                # Convert the response to a list of Row objects
                updated_rows.extend(
                    [
                        Row(row_data=item, table=self, client=self.client)
                        for item in response["items"]
                    ]
                )

            return updated_rows
        except Exception as e:
            self.logger.error(f"Failed to update rows in table {self.id}. Error: {e}")
            raise

    def delete_rows(
        self, rows_data: List[Union[Row, int]], batch_size: Optional[int] = None
    ) -> bool:
        """
        Deletes multiple rows from the table using the Baserow batch-delete endpoint.

        This method accepts a list of Row objects or integers. For each item:
        - If it's a Row object, the method extracts its ID for deletion.
        - If it's an integer, it represents the ID of the row to be deleted.

        :param rows_data: A list of Row objects or integers. Row objects represent
                        the rows to be deleted, while integers represent the row IDs
                        to be deleted.
        :type rows_data: list[Union[Row, int]]

        :param batch_size: The number of rows to include in each batch request when deleting multiple rows.
                        Defaults to None, in which case the client's batch_size will be used.
        :type batch_size: int, optional

        :return: True if rows are successfully deleted, otherwise an exception is raised.
        :rtype: bool

        :raises ValueError: If parameters are not valid.
        :raises TypeError: If an item in rows_data is neither an integer nor a Row object.
        :raises Exception: If the API request results in any error responses.
        """

        # Convert Row objects to their respective IDs and validate integer inputs
        row_ids = []
        for item in rows_data:
            if isinstance(item, Row):
                row_ids.append(item.id)
            elif isinstance(item, int):
                if item <= 0:
                    raise ValueError(
                        f"Invalid row ID: {item}. Row IDs should be positive integers."
                    )
                row_ids.append(item)
            else:
                raise TypeError(
                    f"Unsupported type {type(item)} in rows_data. Expected Row object or positive integer."
                )

        if not row_ids:
            raise ValueError("The rows_data list is empty. Nothing to delete.")

        def _delete_rows_chunk(chunk):
            """
            Helper function to delete a chunk of rows.
            """
            endpoint = f"/api/database/rows/table/{self.id}/batch-delete/"
            self.client.make_api_request(endpoint, method="POST", data={"items": chunk})

        try:
            # Batch delete rows using the specified batch size
            if batch_size is None:
                batch_size = self.client.batch_size

            for i in range(0, len(row_ids), batch_size):
                chunk = row_ids[i : i + batch_size]
                _delete_rows_chunk(chunk)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete rows from table {self.id}. Error: {e}")
            raise
