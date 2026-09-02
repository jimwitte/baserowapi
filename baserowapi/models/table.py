from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, List, Union, Optional, Dict, Any, Generator
from baserowapi.exceptions import (
    BaserowResponseError,
    FieldDataRetrievalError,
    RowFetchError,
    RowAddError,
    RowUpdateError,
    RowDeleteError,
)
from baserowapi.models.filter import Filter
from baserowapi.models.row import Row
from baserowapi.models.fields import (
    AutonumberField,
    Field,
    TextField,
    LongTextField,
    BooleanField,
    NumberField,
    RatingField,
    DateField,
    LastModifiedField,
    CreatedOnField,
    UrlField,
    UUIDField,
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
    PasswordField,
)
import logging
import urllib.parse
import json

if TYPE_CHECKING:
    from baserowapi import Baserow


class Table:
    """
    Represents a table in Baserow with functionalities to manipulate and query rows, fields, etc.
    """

    FIELD_TYPE_CLASS_MAP: Dict[str, type] = {
        AutonumberField.TYPE: AutonumberField,
        TextField.TYPE: TextField,
        LongTextField.TYPE: LongTextField,
        BooleanField.TYPE: BooleanField,
        NumberField.TYPE: NumberField,
        RatingField.TYPE: RatingField,
        DateField.TYPE: DateField,
        LastModifiedField.TYPE: LastModifiedField,
        CreatedOnField.TYPE: CreatedOnField,
        UrlField.TYPE: UrlField,
        UUIDField.TYPE: UUIDField,
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
        PasswordField.TYPE: PasswordField,
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
    def fields(self) -> Mapping[str, Field]:
        """
        Retrieve the fields associated with the table.

        If the fields haven't been fetched yet, this property sends an API request
        to retrieve them. Once retrieved, the fields are cached to avoid unnecessary
        API requests in subsequent calls.

        :return: An ordered, read-only mapping from field name to Field.
        :rtype: Mapping[str, Field]
        :raises FieldDataRetrievalError: If the table fields cannot be retrieved or parsed.
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
                field_objects.sort(
                    key=lambda field: (field.order is None, field.order)
                )
                fields_by_name = {field.name: field for field in field_objects}
                if len(fields_by_name) != len(field_objects):
                    raise BaserowResponseError(
                        "Field names must be unique when user_field_names is enabled."
                    )
                self._fields = MappingProxyType(fields_by_name)
            except Exception as e:
                self.logger.error(
                    f"Failed to fetch fields for table {self.id}. Error: {e}"
                )
                raise FieldDataRetrievalError(
                    f"Failed to retrieve fields for table {self.id}."
                ) from e
        return self._fields

    @property
    def writable_fields(self) -> Mapping[str, Field]:
        """
        Retrieve the list of writable fields for the table.

        This property lazily loads the fields using the `fields` property and then
        filters them to include only those fields where `is_read_only` is False.

        :return: An ordered, read-only mapping of writable fields.
        :rtype: Mapping[str, Field]
        """
        if not hasattr(self, "_writable_fields") or self._writable_fields is None:
            writable_fields = {
                name: field
                for name, field in self.fields.items()
                if not field.is_read_only
            }
            self._writable_fields = MappingProxyType(writable_fields)
        return self._writable_fields

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
        for field in self.fields.values():
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
        :raises FieldDataRetrievalError: If the table fields cannot be retrieved or parsed.
        """
        try:
            return list(self.fields)
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
            {"field": f.field_name, "type": f.operator, "value": f.value}
            for f in filters
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
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> Generator[Row, None, None]:
        """
        Generator function to retrieve rows from the table in a paginated manner,
        optionally limiting the number of rows returned.

        :param include: A list of field names to include in the results.
        :type include: list[str], optional
        :param exclude: A list of field names to exclude from the results.
        :type exclude: list[str], optional
        :param search: A search string to apply on the table data.
        :type search: str, optional
        :param order_by: Field by which the results should be ordered.
        :type order_by: list[str], optional
        :param filter_type: The type of filter to be applied.
        :type filter_type: str, optional
        :param filters: A list containing Filter objects to be applied.
        :type filters: list[Filter], optional
        :param view_id: ID of the view to consider its filters and sorts.
        :type view_id: int, optional
        :param size: The number of rows per page in the response.
        :type size: int, optional
        :param limit: The maximum number of rows to return.
        :type limit: int, optional
        :param kwargs: Additional parameters for the API request.
        :type kwargs: dict

        :yield: Yields Row objects as they are fetched, up to the specified limit.
        :rtype: Generator[Row, None, None]
        :raises RowFetchError: If any error occurs during the process.
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

        yielded_rows = 0  # Tracks the number of rows yielded

        while request_url:
            self.logger.debug(f"Fetching data from URL: {request_url}")
            try:
                response_data = self.client.make_api_request(request_url)
                rows = self._parse_row_data(response_data)

                for row in rows:
                    yield row
                    yielded_rows += 1

                    if limit and yielded_rows >= limit:
                        self.logger.debug(f"Reached the limit of {limit} rows.")
                        return

                request_url = response_data.get("next", None)
                if request_url:
                    self.logger.debug(f"Next page URL: {request_url}")
                else:
                    self.logger.debug("No more pages to fetch.")
            except Exception as e:
                self.logger.error(f"Error fetching rows: {e}")
                raise RowFetchError(f"Error fetching rows: {e}") from e

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
        limit: Optional[int] = None,
        iterator: bool = False,
        **kwargs: Any,
    ) -> Union[List[Row], Generator[Row, None, None]]:
        """
        Retrieves rows from the table using provided parameters, with an optional limit on the number of rows.

        :param include: A list of field names to include in the results.
        :type include: list[str], optional
        :param exclude: A list of field names to exclude from the results.
        :type exclude: list[str], optional
        :param search: A search string to apply on the table data.
        :type search: str, optional
        :param order_by: Field by which the results should be ordered.
        :type order_by: list[str], optional
        :param filter_type: The type of filter to be applied.
        :type filter_type: str, optional
        :param filters: A list containing Filter objects to be applied.
        :type filters: list[Filter], optional
        :param view_id: ID of the view to consider its filters and sorts.
        :type view_id: int, optional
        :param size: The number of rows per page in the response.
        :type size: int, optional
        :param limit: The maximum number of rows to return.
        :type limit: int, optional
        :param iterator: If True, returns a generator of Row objects. If False, returns a list of Row objects.
        :type iterator: bool, optional
        :param kwargs: Additional parameters for the API request.
        :type kwargs: dict

        :return: A list or generator of Row objects, depending on the iterator parameter.
        :rtype: Union[List[Row], Generator[Row, None, None]]

        :raises RowFetchError: If rows cannot be retrieved or parsed.
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
            limit=limit,
            **kwargs,
        )

        if iterator:
            return generator
        else:
            return list(generator)

    def get_row(self, row_id: Union[int, str]) -> Row:
        """
        Retrieve a specific row by its ID from the table.

        :param row_id: The unique identifier of the row to retrieve. This can be either an integer
                    or a string that can be converted to an integer.
        :type row_id: int or str
        :return: An instance of the Row model representing the fetched row.
        :rtype: Row
        :raises ValueError: If the provided row_id is not valid or cannot be converted to an integer.
        :raises RowFetchError: If there's any error during the API request or if the row is not found.
        """
        row_id = self._validated_row_id(row_id)

        endpoint = f"/api/database/rows/table/{self.id}/{row_id}/?user_field_names=true"
        try:
            response = self.client.make_api_request(endpoint)
            return self._row_from_response(response)
        except Exception as e:
            error_message = f"Failed to retrieve row with ID {row_id} from table {self.id}. Error: {e}"
            self.logger.error(error_message)
            raise RowFetchError(f"Failed to retrieve row: {e}") from e

    @staticmethod
    def _validated_row_id(row_id: Union[int, str]) -> int:
        if isinstance(row_id, bool) or not isinstance(row_id, (int, str)):
            raise TypeError("row_id must be a positive integer or numeric string.")
        try:
            validated_id = int(row_id)
        except ValueError as error:
            raise ValueError(f"row_id {row_id!r} is not a valid integer.") from error
        if validated_id <= 0:
            raise ValueError("row_id must be greater than zero.")
        return validated_id

    def _validated_batch_size(self, batch_size: Optional[int]) -> int:
        if batch_size is None:
            batch_size = self.client.batch_size
        if isinstance(batch_size, bool) or not isinstance(batch_size, int):
            raise TypeError("batch_size must be a positive integer.")
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")
        return batch_size

    def _encode_row_values(
        self, values: Mapping[str, Any], *, allow_order: bool = False
    ) -> Dict[str, Any]:
        """Validate and encode one row mapping through its Field definitions."""
        if not isinstance(values, Mapping):
            raise TypeError("Row values must be provided as a mapping.")

        encoded: Dict[str, Any] = {}
        for field_name, value in values.items():
            if not isinstance(field_name, str):
                raise TypeError("Row field names must be strings.")
            if field_name == "order" and allow_order:
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or value <= 0
                ):
                    raise ValueError("order must be a positive number.")
                encoded[field_name] = value
                continue
            if field_name not in self.fields:
                raise KeyError(f"Field {field_name!r} does not exist in the table.")
            field = self.fields[field_name]
            if field.is_read_only:
                raise KeyError(f"Field {field_name!r} is read-only.")
            encoded[field_name] = field.encode_value(value)
        return encoded

    def _row_from_response(self, response: Any) -> Row:
        if not isinstance(response, Mapping):
            raise BaserowResponseError("A row response must be an object.")
        if "id" not in response:
            raise BaserowResponseError("A row response is missing its 'id'.")
        try:
            row_data = dict(response)
            row_data["id"] = self._validated_row_id(response["id"])
            return Row(row_data=row_data, table=self, client=self.client)
        except (TypeError, ValueError) as error:
            raise BaserowResponseError("A row response has an invalid 'id'.") from error

    def _rows_from_batch_response(
        self, response: Any, expected_count: int
    ) -> List[Row]:
        if not isinstance(response, Mapping) or not isinstance(
            response.get("items"), list
        ):
            raise BaserowResponseError(
                "A batch row response must contain an 'items' list."
            )
        items = response["items"]
        if len(items) != expected_count:
            raise BaserowResponseError(
                f"A batch row response returned {len(items)} item(s); "
                f"{expected_count} were expected."
            )
        return [self._row_from_response(item) for item in items]

    def add_rows(
        self,
        rows_data: List[Mapping[str, Any]],
        batch_size: Optional[int] = None,
    ) -> List[Row]:
        """
        Add multiple rows to the table.

        :param rows_data: A non-empty list of field-value mappings.
        :type rows_data: list[dict]

        :param batch_size: The number of rows to include in each batch request when adding multiple rows.
                        Defaults to the client's batch_size.
        :type batch_size: int

        :return: The added rows in input order.
        :rtype: list[Row]

        :raises ValueError: If parameters are not valid.
        :raises RowAddError: If rows cannot be added or parsed.
        """

        if isinstance(rows_data, Mapping) or not isinstance(rows_data, list):
            raise TypeError("add_rows expects a list; use add_row for one row.")
        if not rows_data:
            raise ValueError("rows_data must contain at least one row.")

        encoded_rows = [self._encode_row_values(row) for row in rows_data]
        batch_size = self._validated_batch_size(batch_size)
        endpoint = f"/api/database/rows/table/{self.id}/batch/?user_field_names=true"
        added_rows: List[Row] = []
        for offset in range(0, len(encoded_rows), batch_size):
            chunk = encoded_rows[offset : offset + batch_size]
            batch_number = offset // batch_size + 1
            try:
                response = self.client.make_api_request(
                    endpoint, method="POST", data={"items": chunk}
                )
                added_rows.extend(self._rows_from_batch_response(response, len(chunk)))
            except Exception as error:
                raise RowAddError(
                    f"Failed to add batch {batch_number} to table {self.id}; "
                    f"{len(added_rows)} row(s) were already added.",
                    failed_batch_number=batch_number,
                    completed_row_ids=[row.id for row in added_rows],
                ) from error
        return added_rows

    def add_row(self, values: Mapping[str, Any]) -> Row:
        """Add one row and return it."""
        encoded_values = self._encode_row_values(values)
        endpoint = f"/api/database/rows/table/{self.id}/?user_field_names=true"
        try:
            response = self.client.make_api_request(
                endpoint, method="POST", data=encoded_values
            )
            return self._row_from_response(response)
        except Exception as error:
            raise RowAddError(f"Failed to add a row to table {self.id}.") from error

    def update_rows(
        self,
        rows_data: List[Mapping[str, Any]],
        batch_size: Optional[int] = None,
    ) -> List[Row]:
        """
        Updates multiple rows in the table using the Baserow batch update endpoint.

        :param rows_data: A list of dictionaries.
                        Each dictionary should contain the field values for updating
                        a specific row and include the ID of the row to be updated.
        :type rows_data: list[dict]
        :param batch_size: The number of rows to process in each batch.
        :type batch_size: int

        :return: A list of Row objects representing the updated rows.
        :rtype: list[Row]

        :raises ValueError: If parameters are not valid.
        :raises KeyError: If a dictionary contains a key that doesn't correspond to any writable field in the table or is missing the 'id' key.
        :raises TypeError: If an item in rows_data is not a mapping, or if a generator is passed.
        :raises RowUpdateError: If rows cannot be updated or parsed.
        """

        if not isinstance(rows_data, list):
            raise TypeError("update_rows expects a list; use update_row for one row.")
        if not rows_data:
            raise ValueError("rows_data must contain at least one row.")

        formatted_data = []
        for item in rows_data:
            if isinstance(item, Mapping):
                item = dict(item)
                if "id" not in item:
                    raise KeyError(
                        "The 'id' key is missing, which is required for updating a row."
                    )

                row_id = self._validated_row_id(item.pop("id"))
                formatted_data.append(
                    {"id": row_id, **self._encode_row_values(item, allow_order=True)}
                )

            else:
                raise TypeError(
                    f"Unsupported type {type(item)} in rows_data. Expected a mapping."
                )

        endpoint = f"/api/database/rows/table/{self.id}/batch/?user_field_names=true"
        updated_rows: List[Row] = []
        batch_size = self._validated_batch_size(batch_size)
        for offset in range(0, len(formatted_data), batch_size):
            batch_data = formatted_data[offset : offset + batch_size]
            batch_number = offset // batch_size + 1
            try:
                response = self.client.make_api_request(
                    endpoint, method="PATCH", data={"items": batch_data}
                )
                updated_rows.extend(
                    self._rows_from_batch_response(response, len(batch_data))
                )
            except Exception as error:
                raise RowUpdateError(
                    f"Failed to update batch {batch_number} in table {self.id}; "
                    f"{len(updated_rows)} row(s) were already updated.",
                    failed_batch_number=batch_number,
                    completed_row_ids=[row.id for row in updated_rows],
                ) from error
        return updated_rows

    def update_row(
        self, row_id: Union[int, str], values: Mapping[str, Any]
    ) -> Row:
        """Update one row and return the server representation."""
        validated_id = self._validated_row_id(row_id)
        encoded_values = self._encode_row_values(values, allow_order=True)
        endpoint = (
            f"/api/database/rows/table/{self.id}/{validated_id}/"
            "?user_field_names=true"
        )
        try:
            response = self.client.make_api_request(
                endpoint, method="PATCH", data=encoded_values
            )
            return self._row_from_response(response)
        except Exception as error:
            raise RowUpdateError(
                f"Failed to update row {validated_id} in table {self.id}."
            ) from error

    def delete_rows(
        self,
        rows_data: Union[List[Union[Row, int]], Generator[Union[Row, int], None, None]],
        batch_size: Optional[int] = None,
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
        :raises RowDeleteError: If rows cannot be deleted.
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
            raise RowDeleteError(f"Failed to delete rows: {e}") from e
