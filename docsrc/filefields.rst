Working with File Fields in Baserow API
=======================================

The Baserow API provides tools to interact with file fields, making it easy to upload, download, and inspect file data within your rows. This guide will walk you through the core operations associated with file fields.

Setting Up
----------

Before working with file fields, you should have a table instance and a target row:

.. code-block:: python

    # Given this example row:
    single_row = table.get_row(1)

Downloading Files
-----------------

Files associated with a row can be downloaded to a specified local directory:

.. code-block:: python

    # Download files from a row value to '/tmp' directory
    download_result = single_row.values['myFileField'].download_files('/tmp')

Uploading Files
---------------

You can upload files to Baserow either from a local source or directly from a URL. After uploading, use the `.update()` method to save the changed row to the server:

.. code-block:: python

    # Upload a local file to the server
    single_row.values['myFileField'].upload_file_to_server('fixie.jpg')
    single_row.update()

    # Upload a file from a URL
    single_row.values['myFileField'].upload_file_to_server(url='https://www.jimwitte.net/bison.jpg')
    single_row.update()

Inspecting File Data
--------------------

A file field value in a row contains a list of file objects, each providing details about the stored files:

.. code-block:: python

    # Print the file objects associated with 'myFileField'
    print(single_row['myFileField'])

