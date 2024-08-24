import pytest
import os

def test_upload_file_to_server(all_fields_table, single_row_data):
    # Step 1: Create a single row with an empty FileField
    single_row_data["FileField"]["input"] = []
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_rows([input_data])[0]

    # Step 2: Upload the file to the "FileField" column
    file_path = os.path.join(os.path.dirname(__file__), 'bike.png')
    created_row.values['FileField'].upload_file_to_server(file_path)
    
    # Step 3: update row to server
    created_row.update()

    # Step 4: Fetch the row by ID to verify the file upload
    updated_row = all_fields_table.get_row(created_row.id)

    # Step 5: Verify that the "FileField" column is a non-empty list
    file_field_value = updated_row["FileField"]
    assert isinstance(file_field_value, list), f"Expected a list, but got {type(file_field_value)}"
    assert len(file_field_value) > 0, "FileField is empty, file upload might have failed."

    # Step 6: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])

def test_download_files_from_server(all_fields_table, single_row_data):
    # Step 1: Create a single row with an empty FileField
    single_row_data["FileField"]["input"] = []
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_rows([input_data])[0]

    # Step 2: Upload multiple files to the "FileField" column
    files_to_upload = ['bike.png', 'bike.jpg', 'bike_wheel.jpg']
    file_paths = [os.path.join(os.path.dirname(__file__), file) for file in files_to_upload]
    for file_path in file_paths:
        created_row.values['FileField'].upload_file_to_server(file_path)
    
    # Step 3: Update the row to save the uploaded files
    created_row.update()

    # Step 4: Fetch the row by ID to verify the file uploads
    updated_row = all_fields_table.get_row(created_row.id)

    # Step 5: Download all files to the "downloads" directory
    download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
    downloaded_files = updated_row.values['FileField'].download_files(download_dir)

    # Step 6: Verify that the files have been downloaded
    for file in downloaded_files:
        downloaded_file_path = os.path.join(download_dir, file)
        assert os.path.exists(downloaded_file_path), f"File {file} was not downloaded."

    # Step 7: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])

    # Step 8: Clean up by deleting the downloaded files
    for file in downloaded_files:
        downloaded_file_path = os.path.join(download_dir, file)
        if os.path.exists(downloaded_file_path):
            os.remove(downloaded_file_path)
    
    # Remove the downloads directory if empty
    if os.path.exists(download_dir) and not os.listdir(download_dir):
        os.rmdir(download_dir)