from typing import TYPE_CHECKING, List, Union, Optional, Dict, Any, Generator

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
        filter_type: Optional[str] = None,
        filters: Optional[List[Filter]] = None,
        view_id: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        Constructs the URL for the Baserow API request based on the given parameters.

        :param include: A list of field names to include in the results.
        :type include: list[str], optional
        :param exclude: A list of field names to exclude from the results.
        :type exclude: list[str], optional
        :param search: A search string to apply on the table data.
        :type search: str, optional
        :param order_by: Field by which the results should be ordered.
        :type order_by: list[str], optional
        :param filter_type: The type of filter to be applied (AND/OR).
        :type filter_type: str, optional
        :param filters: A list containing Filter objects to be applied.
        :type filters: list[Filter], optional
        :param view_id: ID of the view to consider its filters and sorts.
        :type view_id: int, optional
        :param size: The number of rows per page in the response.
        :type size: int, optional
        :param kwargs: Additional parameters for the API request.
        :type kwargs: Any

        :return: The constructed request URL.
        :rtype: str

        :raises ValueError: If filter_type is not 'AND' or 'OR'.
        """
        base_url = f"/api/database/rows/table/{self.id}/?user_field_names=true"
        query_params_parts = []

        self._append_query_param(query_params_parts, "include", include)
        self._append_query_param(query_params_parts, "exclude", exclude)
        self._append_query_param(query_params_parts, "search", search)
        self._append_query_param(query_params_parts, "order_by", order_by)
        self._append_query_param(query_params_parts, "view_id", view_id)
        self._append_query_param(query_params_parts, "size", size)

        if filters:
            filter_type = filter_type or "AND"
            if filter_type not in ["AND", "OR"]:
                raise ValueError("'filter_type' should be either 'AND' or 'OR'")
            filter_tree = self._construct_filter_tree(filters, filter_type)
            filter_string = urllib.parse.quote(json.dumps(filter_tree))
            query_params_parts.append(f"filters={filter_string}")

        query_params = "&".join(query_params_parts)
        full_request_url = f"{base_url}&{query_params}" if query_params else base_url
        self.logger.debug(f"Built request URL: '{full_request_url}'")
        return full_request_url

    def _append_query_param(
        self,
        params_list: List[str],
        param_name: str,
        param_value: Optional[Union[str, int, List[str]]],
    ) -> None:
        """
        Helper function to append query parameters to the URL.

        :param params_list: List to hold query parameters.
        :type params_list: list[str]
        :param param_name: Name of the query parameter.
        :type param_name: str
        :param param_value: Value of the query parameter.
        :type param_value: Union[str, int, list[str]], optional
        """
        if param_value is not None:
            if isinstance(param_value, list):
                encoded_value = urllib.parse.quote(",".join(param_value))
            else:
                encoded_value = urllib.parse.quote(str(param_value))
            params_list.append(f"{param_name}={encoded_value}")

    def _construct_filter_tree(
        self, filters: List[Filter], filter_type: str
    ) -> Dict[str, Any]:
        """
        Helper function to construct the filter tree for the request URL.

        :param filters: List of Filter objects.
        :type filters: list[Filter]
        :param filter_type: Type of filter (AND/OR).
        :type filter_type: str
        :return: Dictionary representing the filter tree.
        :rtype: dict[str, Any]
        """
        filter_dicts = [
            {"field": f.field_name, "type": f.operator, "value": f.value} for f in filters
        ]
        return {"filter_type": filter_type, "filters": filter_dicts, "groups": []}

    def _parse_row_data(self, response_data: Dict[str, Any]) -> List[Row]:
        """
        Parses the raw data from the API response and transforms it into a list of Row objects.

        :param response_data: The raw response data from the Baserow API.
        :type response_data: dict[str, Any]
        :return: List of Row objects.
        :rtype: list[Row]
        """
        if not response_data or "results" not in response_data:
            self.logger.warning("Received invalid or empty response data from the API.")
            return []

        return [
            Row(row_data=row_data, table=self, client=self.client)
            for row_data in response_data["results"]
        ]

    def row_generator(
        self,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        search: Optional[str] = None,
        order_by: Optional[List[str]] = None,
        filter_type: Optional[str] = None,
        filters: Optional[List[Filter]] = None,
        view_id: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs,
    ) -> Generator[Row, None, None]:
        """
        Generator function to retrieve rows from the table in a paginated manner.

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
        :param kwargs: Additional parameters for the API request.
        :type kwargs: dict

        :yield: Yields Row objects as they are fetched.
        :rtype: Generator[Row, None, None]
        :raises Exception: If any error occurs during the process.
        :raises ValueError: If parameters are not valid.
        """
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

        while request_url:
            self.logger.debug(f"Fetching data from URL: {request_url}")
            try:
                response_data = self.client.make_api_request(request_url)
                rows = self._parse_row_data(response_data)

                for row in rows:
                    yield row

                request_url = response_data.get("next", None)
                if request_url:
                    self.logger.debug(f"Next page URL: {request_url}")
                else:
                    self.logger.debug("No more pages to fetch.")
            except Exception as e:
                self.logger.error(f"Error fetching rows: {e}")
                raise e

    def get_rows(
        self,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        search: Optional[str] = None,
        order_by: Optional[List[str]] = None,
        filter_type: Optional[str] = None,
        filters: Optional[List[Filter]] = None,
        view_id: Optional[int] = None,
        size: Optional[int] = None,
        return_single: bool = False,
        **kwargs,
    ) -> Union[Row, Generator[Row, None, None]]:
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
        :param return_single: If True, returns a single Row object instead of a generator.
        :type return_single: bool, optional
        :param kwargs: Additional parameters for the API request.
        :type kwargs: dict

        :return: Depending on return_single, either a single Row object or a generator of Row objects.
        :rtype: Union[Row, Generator[Row, None, None]]

        :raises Exception: If any error occurs during the process.
        :raises ValueError: If parameters are not valid.
        """
        generator = self.row_generator(
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

        if return_single:
            try:
                return next(generator)
            except StopIteration:
                return None

        return generator

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
        if not row_id:
            raise ValueError("The provided row_id is not valid.")

        endpoint = f"/api/database/rows/table/{self.id}/{row_id}/?user_field_names=true"
        try:
            response = self.client.make_api_request(endpoint)
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
        rows_data: Union[List[Union[Dict[str, Any], Row]], Generator[Row, None, None]],
        batch_size: Optional[int] = None,
    ) -> List[Row]:
        """
        Updates multiple rows in the table using the Baserow batch update endpoint.

        :param rows_data: A list of dictionaries or Row objects.
                        Each dictionary should contain the field values for updating
                        a specific row and include the ID of the row to be updated.
                        Row objects represent the rows to be updated.
        :type rows_data: list[Union[dict, Row]]
        :param batch_size: The number of rows to process in each batch.
        :type batch_size: int

        :return: A list of Row objects representing the updated rows.
        :rtype: list[Row]

        :raises ValueError: If parameters are not valid.
        :raises KeyError: If a dictionary contains a key that doesn't correspond to any field in the table or is missing the 'id' key.
        :raises TypeError: If an item in rows_data is neither a dictionary nor a Row object, or if a generator is passed.
        :raises Exception: If the API request results in any error responses.
        """

        if not rows_data:
            warning_msg = "The rows_data list is empty. Nothing to update."
            self.logger.warning(warning_msg)
            raise ValueError(warning_msg)

        if isinstance(rows_data, Generator):
            raise TypeError(
                "The update_rows method does not accept generator objects. Please provide a list of rows."
            )

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

            if batch_size is None:
                batch_size = self.client.batch_size

            for i in range(0, len(formatted_data), batch_size):
                batch_data = formatted_data[i : i + batch_size]
                response = self.client.make_api_request(
                    endpoint, method="PATCH", data={"items": batch_data}
                )

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
        self, rows_data: Union[List[Union[Row, int]], Generator[Union[Row, int], None, None]], batch_size: Optional[int] = None
    ) -> bool:
        """
        Deletes multiple rows from the table using the Baserow batch-delete endpoint.

        This method accepts a list or generator of Row objects or integers. For each item:
        - If it's a Row object, the method extracts its ID for deletion.
        - If it's an integer, it represents the ID of the row to be deleted.

        :param rows_data: A list or generator of Row objects or integers. Row objects represent
                        the rows to be deleted, while integers represent the row IDs
                        to be deleted.
        :type rows_data: list[Union[Row, int]] or Generator[Union[Row, int], None, None]

        :param batch_size: The number of rows to include in each batch request when deleting multiple rows.
                        Defaults to None, in which case the client's batch_size will be used.
        :type batch_size: int, optional

        :return: True if rows are successfully deleted, otherwise an exception is raised.
        :rtype: bool

        :raises ValueError: If parameters are not valid.
        :raises TypeError: If an item in rows_data is neither an integer nor a Row object.
        :raises Exception: If the API request results in any error responses.
        """

        # Handle Generator input by converting it to a list
        if isinstance(rows_data, Generator):
            rows_data = list(rows_data)

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
