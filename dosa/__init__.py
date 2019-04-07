import glob
import json
import logging
import math
import os

from os.path import basename
from collections import namedtuple

import requests

API_VERSION = 'v2'
__version__ = '0.10'
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
        headers_s = ''.join(
            ' -H ' +
            '"%s: %s"' %
            (k,
             v) for (
                k,
                v) in list(
                headers.items()))
        curl_cmd = 'curl -X %s %s -d "%s" %s' % (
            req_type, endpoint, json.dumps(data), headers_s)
        logging.debug(curl_cmd)


class APIObject(object):

    def __init__(self, api_key, name, path=None, **kw):
        self.api_key = api_key
        self.name = name
        path = path or name
        self.path = path.format(**kw)
        for (k, v) in list(kw.items()):
            setattr(self, k, v)

    def send_req(self, req_type, path, data={}, params={}):
        req_calls = {
            'GET': requests.get,
            'POST': requests.post,
            'DELETE': requests.delete,
            'PUT': requests.put}
        headers = {
            'authorization': 'Bearer %s' % self.api_key,
            'Content-Type': 'application/json'}
        endpoint = 'https://api.digitalocean.com/%s/%s' % (API_VERSION, path)
        req_call = req_calls[req_type]
        resp = req_call(
            endpoint,
            params=params,
            data=json.dumps(data),
            headers=headers)
        status_code = resp.status_code

        # default status for request and returned values
        failed = False
        ret = None

        # requests is failes if statos is not in this list
        if status_code not in (200, 201, 202, 204):
            failed = True

        # If there's no response (No content), as for a DELETE method,
        # I can't get a json object
        if resp.text and resp.text != '':
            ret = resp.json()

        if failed or DEBUG:
            show_debug_hints(req_type, endpoint, data, headers, resp)

        if failed:
            raise Exception(resp.text)

        return Return(status_code, ret)


class Resource(APIObject):

    def info(self):
        return self.send_req('GET', self.path)

    def update(self, **data):
        return self.send_req('PUT', self.path, data)


class Collection(APIObject):

    def list(self, **params):
        """
        @params: per_page=10, page=4
            per_page: number of objects to include in result
            page: page number
        """

        # it returns a Return nametuple object
        return self.send_req('GET', self.path, params=params)

    def all(self):
        images = []
        resp = self.list()
        images.extend(resp.result[self.name])
        total = resp.result['meta']['total']

        # if total == len(images), math.ceil will be == 1
        more_no_reqs = math.ceil(total / len(images))

        # This seems easier to understand to me
        for i in range(1, more_no_reqs):
            # now I starts from 1. Getting next page
            resp = self.list(page=(i + 1))
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

    def create(self, name, region, size, image, ssh_keys=None,
               backups=False, ipv6=False, private_networking=False):
        data = dict(
            name=name,
            region=region,
            size=size,
            image=image,
            ssh_keys=ssh_keys,
            backups=backups,
            private_networking=private_networking)
        return self.send_req('POST', self.path, data)


class Images(Collection):

    def search(self, word, region=None, show_op=False):
        """
        @region: <string> eg sgp1, nyc1
        @show_op: prints output
        """
        region = region and region.lower()

        def filter_image(image):
            distribution = image['distribution'].lower()
            slug = image['slug'] and image['slug'].lower() or ''
            if (word in distribution) or (word in slug):
                if not region:
                    return True
                else:
                    return region in image['regions']
            return False

        images = list(filter(filter_image, self.all()))

        if show_op:
            for image in images:
                print(image['slug'], image['id'], image['distribution'])

        return images


class DomainRecords(Collection):

    def Record(self, record_id):
        return Resource(self.api_key, self.path +
                        '/{record_id}', record_id=record_id)


class Firewall(Resource):
    def add_droplet(self, droplet_id):
        """Add droplet to firewall"""

        # first get info from firewall to determine droplets assiged to it
        droplet_ids = self.info().result['firewall']['droplet_ids']

        if droplet_id in droplet_ids:
            logging.warning(
                "Droplet {d} has already firewall {f}".format(
                    d=droplet_id, f=self.id))
            return

        else:
            # determine path
            path = "firewalls/{id}/droplets".format(id=self.id)

            # determine data
            data = {"droplet_ids": [droplet_id]}

            return self.send_req('POST', path, data)

    def remove_droplet(self, droplet_id):
        """Remove droplet from firewall"""

        # first get info from firewall to determine droplets assiged to it
        droplet_ids = self.info().result['firewall']['droplet_ids']

        if droplet_id not in droplet_ids:
            logging.warning(
                "Droplet {d} hasn't firewall {f}".format(
                    d=droplet_id, f=self.id))
            return

        else:
            # determine path
            path = "firewalls/{id}/droplets".format(id=self.id)

            # determine data
            data = {"droplet_ids": [droplet_id]}

            return self.send_req('DELETE', path, data)


class Firewalls(Collection):
    # override APIObject.create and return a Firewall object
    def create(self, **data):
        # call base method and create a firewall
        status, result = super().create(**data)

        # get firewall_id
        firewall_id = result['firewall']['id']

        # now get a Firewall instance
        return Firewall(self.api_key, 'firewalls/{id}', id=firewall_id)

    def get_by_name(self, name):
        """Return a Firewall object from a name"""

        # search for a firewall rule by name:
        # https://stackoverflow.com/a/29051598/4385116
        data = list(filter(lambda d: d['name'] in [name], self.all()))

        # get firewall id
        firewall_id = data[0]['id']

        # now get a Firewall instance
        return Firewall(self.api_key, 'firewalls/{id}', id=firewall_id)


class Client(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.droplets = Droplets(self.api_key, 'droplets')
        self.images = Images(self.api_key, 'images')
        self.keys = Collection(self.api_key, 'ssh_keys', 'account/keys')
        self.domains = Collection(self.api_key, 'domains')
        self.firewalls = Firewalls(self.api_key, 'firewalls')

    def Domain(self, domain):
        return Resource(self.api_key, 'domains/{domain}', domain=domain)

    def DomainRecords(self, domain, record_id=None):
        return DomainRecords(
            self.api_key, 'domains/{domain}/records', domain=domain)

    def Droplet(self, id):
        return Droplet(self.api_key, 'droplets/{id}', id=id)

    def sync_ssh_keys(self, keysdir):
        """
        sync local ssh keys directory containing all key files
        - uploads all keys in keysdir to digitalocean
        - removes any extra keys found at digitalocean
        """
        local_keys = dict((basename(path), open(path).read())
                          for path in glob.glob(os.path.join(keysdir, '*')))
        registered_keys = dict((key['name'], key)
                               for key in self.keys.list().result['ssh_keys'])
        local_key_names = set(local_keys.keys())
        registered_key_names = set(registered_keys.keys())
        new_key_names = local_key_names.difference(registered_key_names)
        keynames_to_discard = registered_key_names.difference(local_keys)
        for name in new_key_names:
            self.keys.create(name=name, public_key=local_keys[name])
        for name in keynames_to_discard:
            self.keys.delete(registered_keys[name]['id'])
        final_keys = self.keys.list().result['ssh_keys']
        return {'new': new_key_names, 'deleted': keynames_to_discard,
                'all_ids': [key['id'] for key in final_keys]}
