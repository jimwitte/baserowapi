Baserow client
===============

These examples show various options when creating a client object.

.. code-block:: python

    from baserowapi import Baserow, Filter

    # baserow client, default is 'https://api.baserow.io'
    baserow = Baserow(token='mytoken')

    # specify server url
    baserow = Baserow(url='https://baserow.example.com',token='mytoken')

    # with logging, INFO, ERROR, DEBUG
    baserow = Baserow(url='https://baserow.example.com',token='mytoken', logging_level='DEBUG')

    # logs to file
    baserow = Baserow(url='https://baserow.example.com',token='mytoken', logging_level='DEBUG', log_file='log.txt')
