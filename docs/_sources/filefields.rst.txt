Working with File Fields
========================

File creation and row assignment are separate operations. Uploading through the
client returns an unattached :class:`baserowapi.BaserowFile`; it does not mutate
any row. Assign the returned record explicitly.

.. code-block:: python

    uploaded = db.upload_file('fixie.jpg')
    row.update({'Files': [uploaded]})

    imported = db.upload_file_via_url('https://example.com/bison.jpg')
    row.update({'Files': [uploaded, imported]})

The file-field update is the complete desired list. Pass ``[]`` or ``None`` to
clear the field. Baserow also accepts stored filenames, lists of stored
filenames, returned file objects, and comma-separated stored filenames.

File Reads and Metadata
-----------------------

A file field reads as a list of ``BaserowFile`` records. ``name`` is Baserow's
stored filename and is the stable value used for assignment. Depending on the
endpoint, ``visible_name`` describes the name shown on an attached row and
``original_name`` describes the source name returned by upload. URL, size, MIME
type, and the complete payload in ``raw`` are retained when supplied.

.. code-block:: python

    for item in row['Files']:
        print(item.name, item.visible_name, item.url)

The semantic client does not download file URLs or traverse local directories.
Use an ordinary HTTP/file utility when an application needs that separate
behavior.
