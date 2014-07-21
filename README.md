DOsa
====

Python wrapper for Digital Ocean [API
V2](https://developers.digitalocean.com).

![image](http://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Paper_Masala_Dosa.jpg/193px-Paper_Masala_Dosa.jpg%0A%20:target:%20http://www.flickr.com/photos/git/3936135033/)

Installation
------------

~~~~ {.sourceCode .bash}
pip install dosa
~~~~

Usage
-----

~~~~ {.sourceCode .python}
import dosa

API_KEY = 'Your API Key'
dosa.DEBUG = True  # enables debug logs

client = dosa.Client(api_key=API_KEY)

# Droplets
client.droplets.list()
status, result = client.droplets.create(name='terminator', region='nyc2',\
    size='512mb', image='ubuntu-14-04-x32')
new_droplet_id = result['id']
client.droplets.delete(new_droplet_id)

# Images
client.images.list()
~~~~

Credits
-------

Created while working on [Scroll.in](http://scroll.in)'s project.
