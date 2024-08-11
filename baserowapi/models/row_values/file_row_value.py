from typing import Optional, List, Any
import logging
import os
import requests
from baserowapi.models.fields import FileField
from baserowapi.models.row_values.row_value import RowValue


class FileRowValue(RowValue):
    """
    Represents a RowValue designed for a FileField.

    :param field: The associated FileField object.
    :param client: The Baserow class API client to make API requests.
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :raises ValueError: If the provided field is not an instance of the FileField class.
    """

    def __init__(
        self, field: "FileField", client: Any, raw_value: Optional[List[Any]] = None
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, FileField):
            raise ValueError(
                f"The provided field is not an instance of the FileField class. Received: {type(field).__name__}"
            )

        if self._raw_value is None:
            self._raw_value = []

    def upload_file_to_server(
        self,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        replace: bool = False,
    ) -> List[Any]:
        """
        Upload a file or files to Baserow either from a local path or by downloading it from a provided URL.
        The method either appends or replaces the current value based on the 'replace' flag.

        Note: This function updates the in-memory representation of the row value.
        Use `row.update()` to save the updated value to the server.

        :param file_path: Path to the file or directory to be uploaded. Defaults to None.
        :param url: The URL of the file to download and upload. Defaults to None.
        :param replace: If True, replaces the current value with the uploaded file's data.
                        Otherwise, appends. Defaults to False.
        :return: A list of file object representations returned by Baserow.
        :raises ValueError: If neither file_path nor url is provided.
        :raises Exception: If there's an error during the upload process.
        """
        if not file_path and not url:
            raise ValueError("Either file_path or url must be provided.")

        endpoint_file = "/api/user-files/upload-file/"
        endpoint_url = "/api/user-files/upload-via-url/"
        uploaded_files = []

        # Upload local files
        if file_path:
            if os.path.isdir(file_path):
                files_to_upload = [
                    os.path.join(file_path, file) for file in os.listdir(file_path)
                ]
            else:
                files_to_upload = [file_path]

            for file in files_to_upload:
                try:
                    with open(file, "rb") as f:
                        response = self.client.make_api_request(
                            endpoint_file, method="POST", files={"file": f}
                        )
                        uploaded_files.append(response)
                except Exception as e:
                    error_message = f"Failed to upload file {file}. Error: {e}"
                    self.logger.error(error_message)
                    raise Exception(error_message)

        # Upload file from URL
        if url:
            try:
                data = {"url": url}
                response = self.client.make_api_request(
                    endpoint_url, method="POST", data=data
                )
                uploaded_files.append(response)
            except Exception as e:
                self.logger.error(f"Failed to upload file from URL {url}. Error: {e}")
                raise

        # Update in-memory value based on the 'replace' flag
        if replace:
            self.value = uploaded_files
        else:
            self.value.extend(uploaded_files)

        return uploaded_files

    def download_files(self, directory_path: str) -> List[str]:
        """
        Downloads all file objects in the FileRowValue to the specified directory.

        :param directory_path: The path to the directory where the files should be downloaded.
        :return: List of filenames that were successfully downloaded.
        :raises Exception: If there's an error during the download process.
        """
        logger = logging.getLogger(__name__)
        downloaded_files = []

        # Ensure the target directory exists
        os.makedirs(directory_path, exist_ok=True)

        for file_obj in self._raw_value:
            file_url = file_obj["url"]
            file_name = file_obj["original_name"]
            target_file_path = os.path.join(directory_path, file_name)

            # Check if the file already exists in the target directory
            if os.path.exists(target_file_path):
                logger.info(
                    f"File {file_name} already exists in {directory_path}. Skipping download."
                )
                continue

            try:
                # Download the file
                response = requests.get(file_url, stream=True)
                response.raise_for_status()

                # Save the downloaded file to the target directory
                with open(target_file_path, "wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)

                logger.debug(
                    f"File {file_name} downloaded successfully to {directory_path}."
                )
                downloaded_files.append(file_name)

            except requests.RequestException as e:
                logger.error(
                    f"Failed to download file {file_name} from {file_url}. Error: {e}"
                )
                raise Exception(f"Failed to download file {file_name}. Error: {e}")

        return downloaded_files
