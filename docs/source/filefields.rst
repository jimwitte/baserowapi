Working with file fields
==========================

.. code-block:: python

    # given this example row
    single_row = table.get_row(1)

    # download files from row value
    download_result = single_row.values['myFileField'].download_files('/tmp')

    # upload a local file to the server. Need to use .update() row method to save changed row to server
    single_row.values['myFileField'].upload_file_to_server('fixie.jpg')
    single_row.update()

    # upload a file from a URL. Need to use .update() row method to save changed row to server
    single_row.values['myFileField'].upload_file_to_server(url='https://www.jimwitte.net/bison.jpg')
    single_row.update()

    # the value of a file row value is a list of file objects
    print(single_row['myFileField'])