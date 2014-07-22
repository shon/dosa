import json
import logging
import requests

API_VERSION = 'v2'
__version__ = '0.3'
DEBUG = False


def show_debug_hints(req_type, endpoint, data, headers, resp):
    logging.debug('http status code: %s' % resp.status_code)
    logging.debug('response body: %s' % resp.text)
    headers_s = ''.join(' -H ' + '%s:%s' % (k, v) for (k, v) in headers.items())
    curl_cmd = 'curl -X %s %s -d %s %s' % (req_type, endpoint, data, headers_s)
    logging.debug(curl_cmd)


class APIObject(object):

    def __init__(self, api_key, path, **kw):
        self.api_key = api_key
        self.path = path.format(kw)
        for (k, v) in kw.items():
            setattr(self, k, v)

    def send_req(self, req_type, path, data={}):
        req_calls = {'GET': requests.get, 'POST': requests.post, 'DELETE': requests.delete}
        headers = {'authorization': 'Bearer %s' % self.api_key, 'Content-Type': 'application/json'}
        endpoint = 'https://api.digitalocean.com/%s/%s' % (API_VERSION, path)
        req_call = req_calls[req_type]
        resp = req_call(endpoint, data=json.dumps(data), headers=headers)
        status_code = resp.status_code
        failed = False
        if req_type == 'DELETE':
            ret = None
            if status_code not in (200, 204):
                failed = True
        else:
            ret = resp.json()
            if status_code not in (200, 201, 202):
                failed = True
        if failed:
            show_debug_hints(req_type, endpoint, data, headers, resp)
            raise Exception(resp.text)
        return status_code, ret


class Resource(APIObject):

    def get(self):
        return self.send_req('GET', self.id)


class Collection(APIObject):

    def list(self):
        return self.send_req('GET', self.path)

    def create(self, **data):
        return self.send_req('POST', self.path, data)

    def delete(self, id):
        path = self.path + '/' + str(id)
        return self.send_req('DELETE', path)


class Droplets(Collection):

    def create(self, name, region, size, image, ssh_keys=None, backups=False, ipv6=False, private_networking=False):
        data = dict(name=name, region=region, size=size, image=image,  ssh_keys=ssh_keys, backups=backups, private_networking=private_networking)
        return self.send_req('POST', self.path, data)


class Client(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.droplets = Droplets(self.api_key, 'droplets')
        self.images = Collection(self.api_key, 'images')
        self.keys = Collection(self.api_key, 'account/keys')

    def Droplet(self, id):
        return Resource(self.api_key, 'droplets/{id}', id=id)
