from collections import namedtuple
import glob
import json
import logging
import os
from os.path import basename
import requests

API_VERSION = 'v2'
__version__ = '0.6.2'
DEBUG = False

Return = namedtuple('Return', ('status_code', 'result'))


def set_debug():
    global DEBUG
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    DEBUG = True


def show_debug_hints(req_type, endpoint, data, headers, resp):
    if DEBUG:
        logging.debug('http status code: %s' % resp.status_code)
        logging.debug('response body: %s' % resp.text)
        headers_s = ''.join(' -H ' + '"%s: %s"' % (k, v) for (k, v) in headers.items())
        curl_cmd = 'curl -X %s %s -d "%s" %s' % (req_type, endpoint, json.dumps(data), headers_s)
        logging.debug(curl_cmd)


class APIObject(object):

    def __init__(self, api_key, name, path=None, **kw):
        self.api_key = api_key
        self.name = name
        path = path or name
        self.path = path.format(**kw)
        for (k, v) in kw.items():
            setattr(self, k, v)

    def send_req(self, req_type, path, data={}, params={}):
        req_calls = {'GET': requests.get, 'POST': requests.post, 'DELETE': requests.delete}
        headers = {'authorization': 'Bearer %s' % self.api_key, 'Content-Type': 'application/json'}
        endpoint = 'https://api.digitalocean.com/%s/%s' % (API_VERSION, path)
        req_call = req_calls[req_type]
        resp = req_call(endpoint, params=params, data=json.dumps(data), headers=headers)
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
        if failed or DEBUG:
            show_debug_hints(req_type, endpoint, data, headers, resp)
        if failed:
            raise Exception(resp.text)
        return Return(status_code, ret)


class Resource(APIObject):

    def info(self):
        return self.send_req('GET', self.path)


class Collection(APIObject):

    def list(self, **params):
        """
        @params: per_page=10, page=4
            per_page: number of objects to include in result
            page: page number
        """
        return self.send_req('GET', self.path, params=params)

    def all(self):
        images = []
        resp = self.list()
        images.extend(resp.result[self.name])
        total = resp.result['meta']['total']
        more_no_reqs = total / len(images)
        for i in range(more_no_reqs):
            resp = self.list(page=(i+2))
            images.extend(resp.result[self.name])
        return images

    def create(self, **data):
        return self.send_req('POST', self.path, data)

    def delete(self, id):
        path = self.path + '/' + str(id)
        return self.send_req('DELETE', path)


class Droplet(Resource):

    def ip_addresses(self):
        networks_v4 = self.info().result['droplet']['networks']['v4']
        return [net['ip_address'] for net in networks_v4]

    def status(self):
        return self.info().result['droplet']['status']


class Droplets(Collection):

    def create(self, name, region, size, image, ssh_keys=None, backups=False, ipv6=False, private_networking=False):
        data = dict(name=name, region=region, size=size, image=image,  ssh_keys=ssh_keys, backups=backups, private_networking=private_networking)
        return self.send_req('POST', self.path, data)


class Client(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.droplets = Droplets(self.api_key, 'droplets')
        self.images = Collection(self.api_key, 'images')
        self.keys = Collection(self.api_key, 'ssh_keys', 'account/keys')

    def Droplet(self, id):
        return Droplet(self.api_key, 'droplets/{id}', id=id)

    def sync_ssh_keys(self, keysdir):
        """
        sync local ssh keys directory containing all key files
        - uploads all keys in keysdir to digitalocean
        - removes any extra keys found at digitalocean
        """
        local_keys = dict((basename(path), open(path).read()) for path in glob.glob(os.path.join(keysdir, '*')))
        registered_keys = dict((key['name'], key) for key in self.keys.list().result['ssh_keys'])
        local_key_names = set(local_keys.keys())
        registered_key_names = set(registered_keys.keys())
        new_key_names = local_key_names.difference(registered_key_names)
        keynames_to_discard = registered_key_names.difference(local_keys)
        for name in new_key_names:
            self.keys.create(name=name, public_key=local_keys[name])
        for name in keynames_to_discard:
            self.keys.delete(registered_keys[name]['id'])
        final_keys = self.keys.list().result['ssh_keys']
        return {'new': new_key_names, 'deleted': keynames_to_discard, 'all_ids': [key['id'] for key in final_keys]}
