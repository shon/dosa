import logging
import requests

API_VERSION = 'v2'
__version__ = '0.1'


class APIObject(object):

    def __init__(self, api_key, path, **kw):
        self.api_key = api_key
        self.path = path.format(kw)
        for (k, v) in kw.items():
            setattr(self, k, v)

    def send_req(self, req_type, path, data={}):
        req_calls = {'GET': requests.get, 'POST': requests.post}
        headers={'authorization': 'Bearer %s' % self.api_key, 'content_type': 'application/json'}
        endpoint = 'https://api.digitalocean.com/%s/%s' % (API_VERSION, path)
        req_call = req_calls[req_type]
        req = req_call(endpoint, params=data, headers=headers)
        ret = req.json()
        if req.status_code not in (200, 202):
            logging.debug('http status code: %s' % req.status_code)
            headers_s = ''.join(' -H ' + '%s:%s' % (k, v) for (k, v) in headers.items())
            curl_cmd = 'curl -X %s %s -d %s %s' % (req_type, endpoint, data, headers_s)
            logging.debug(curl_cmd)
            raise Exception(ret)
        return ret


class Resource(APIObject):

    def get(self):
        return send_req('GET', self.id)

class Collection(APIObject):

    def list(self):
        return self.send_req('GET', self.path)


class Droplets(Collection):

    def create(self, name, region, size, image, ssh_keys=None, backups=False, ipv6=False, private_networking=False):
        data = dict(name=name, region=region, size=size, image=image+'zz',  ssh_keys=ssh_keys, backups=backups, private_networking=private_networking)
        return self.send_req('POST', 'droplets', data)


class Client(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.droplets = Droplets(self.api_key, 'droplets')
        self.images = Collection(self.api_key, 'images')

    def Droplet(self, id):
        return Resource(self.api_key, 'droplets/{id}', id=id)
