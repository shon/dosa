Python wrapper for Digital Ocean `API
V2 <https://developers.digitalocean.com>`__.

|Latest Version|

|Number of PyPI downloads|

Installation
------------

.. code:: bash

    pip install dosa

Usage
-----

.. code:: python

    import dosa

    API_KEY = 'Your API Key'
    dosa.set_debug()  # enables debug logs

    client = dosa.Client(api_key=API_KEY)

    # Droplets
    client.droplets.list()
    status, result = client.droplets.create(name='terminator', region='nyc2',\
        size='512mb', image='ubuntu-14-04-x32', ssh_keys=[12345])
    new_droplet_id = result['id']

    # Droplet
    new_droplet = client.Droplet(new_droplet_id)
    print(new_droplet.info())
    ## shortcuts
    new_droplet.status()
    new_droplet.ip_addresses()
    client.droplets.delete(new_droplet_id)

    # SSH Keys
    pub_key = open('~/.ssh/id_rsa.pub').read()
    client.keys.create(name='RSA key', public_key=pub_key)
    client.keys.list()

    # Images
    client.images.list()
    client.images.all()

    # Extras
    # $ ls keys/
    # rsa_pub1.id  rsa_pub2.key  rsa_pub3.key
    keys_dir = 'keys'
    client.sync_ssh_keys(keys_dir)

Credits
-------

Created while working on `Scroll.in <http://scroll.in>`__'s project.

Dosa?
-----

|"Paper Masala Dosa" by SteveR- -
http://www.flickr.com/photos/git/3936135033/. Licensed under Creative
Commons Attribution 2.0 via Wikimedia Commons|

.. |Latest Version| image:: https://badge.fury.io/py/dosa.svg
   :target: http://badge.fury.io/py/dosa
.. |Number of PyPI downloads| image:: https://pypip.in/d/dosa/badge.png
   :target: https://crate.io/packages/dosa/
.. |"Paper Masala Dosa" by SteveR- - http://www.flickr.com/photos/git/3936135033/. Licensed under Creative Commons Attribution 2.0 via Wikimedia Commons| image:: http://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Paper_Masala_Dosa.jpg/640px-Paper_Masala_Dosa.jpg
   :target: http://commons.wikimedia.org/wiki/File:Paper_Masala_Dosa.jpg#mediaviewer/File:Paper_Masala_Dosa.jpg
