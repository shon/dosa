DOsa
====

Python wrapper for Digital Ocean API V2


.. image:: http://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Paper_Masala_Dosa.jpg/193px-Paper_Masala_Dosa.jpg
    :target: http://www.flickr.com/photos/git/3936135033/


.. code-block:: bash

    pip install dosa


.. code-block:: python

    import dosa

    API_KEY = 'Your API Key'

    client = dosa.Client(api_key=API_KEY)
    client.droplets.list()
    client.images.list()
    client.droplets.create(name='terminator', region='nyc2', size='512mb', \
        image='ubuntu-14-04-x32')

Credits
-------
Created while working on `Scroll.in <http://scroll.in>`_'s project.
