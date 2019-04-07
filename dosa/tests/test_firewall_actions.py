#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:51:50 2019

@author: Paolo Cozzi <cozzi@ibba.cnr.it>
"""

import json
import os.path
from unittest import TestCase
from unittest.mock import patch

import dosa

endpoint = 'https://api.digitalocean.com/%s' % dosa.API_VERSION
api_sample_data = os.path.join(os.path.dirname(__file__), 'api_sample_data')


class TestDosaClientFirewallActions(TestCase):
    @classmethod
    def setUp(self):
        self.api_key = 'my_fake_api_key'
        self.client = dosa.Client(self.api_key)

        # to see all differences in assertEqual
        self.maxDiff = None

    @classmethod
    def tearDown(self):
        pass

    def test_dosa_client_created(self):
        client = dosa.Client(self.api_key)
        self.assertIsInstance(client, dosa.Client)

    @patch('dosa.requests.get')
    def test_dosa_firewall_list(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('firewalls'))
        status, result = self.client.firewalls.list()
        self.assertEqual(2, len(result['firewalls']))
        self.assertTrue(mock_get.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args
        self.assertEqual(url[0], '{}/firewalls'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    @patch('dosa.requests.get')
    def test_dosa_firewall_search(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('firewalls'))

        firewall = self.client.firewalls.get_by_name('webserver')

        # a firewall is an object
        self.assertIsInstance(firewall, dosa.Firewall)

        # assert method called
        self.assertTrue(mock_get.called)
        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args

        self.assertEqual(url[0], '{}/firewalls'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    @patch('dosa.requests.post')
    def test_dosa_firewall_create(self, mock_post):
        mock_post.return_value.status_code = 202
        mock_post.return_value.json.return_value = json.loads(
            self._get_sample_data('firewall_create'))

        # set firewall data
        params = {
            'droplet_ids': [],
            'inbound_rules': [{'ports': '22',
                               'protocol': 'tcp',
                               'sources': {
                                   'addresses': ['0.0.0.0/0', '::/0']}},
                              {'ports': '80',
                               'protocol': 'tcp',
                               'sources': {
                                   'addresses': ['0.0.0.0/0', '::/0']}}],
            'name': 'firewall',
            'outbound_rules': [{'destinations': {
                'addresses': ['0.0.0.0/0', '::/0']},
                'ports': 'all',
                'protocol': 'tcp'}],
            'tags': []}

        firewall = self.client.firewalls.create(**params)
        self.assertTrue(mock_post.called)
        self.assertIsInstance(firewall, dosa.Firewall)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        url, data = mock_post.call_args
        self.assertEqual(url[0], '{}/firewalls'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        data_json = json.loads(data['data'])
        self.assertEqual(data_json['name'], params['name'])

    @patch('dosa.requests.delete')
    def test_dosa_firewall_delete(self, mock_delete):
        mock_delete.return_value.status_code = 204
        # there's no response for delete firewall (No Content)
        mock_delete.return_value.text = None
        firewall_id = '99d5ef9c-2aa5-40ad-8507-2af7d65d099a'
        status, result = self.client.firewalls.delete(firewall_id)

        self.assertTrue(mock_delete.called)
        self.assertEqual(result, None)
        self.assertEqual(status, 204)
        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}

        url, data = mock_delete.call_args
        self.assertEqual(url[0], '{}/firewalls/{}'.format(
            endpoint, firewall_id))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)

    @patch('dosa.requests.get')
    @patch('dosa.requests.post')
    def test_dosa_firewall_add_droplet(self, mock_post, mock_get):
        # get a droplet and firewall id
        droplet_id = 12345
        firewall_id = '99d5ef9c-2aa5-40ad-8507-2af7d65d099a'

        # prepare a response for a firewall object
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('firewall'))

        mock_post.return_value.status_code = 204
        # there's no response for adding droplet (No Content)
        mock_post.return_value.text = None

        # get a firewall object
        firewall = dosa.Firewall(
            self.api_key, 'firewalls/{id}', id=firewall_id)

        # add a droplet to firewall
        status, result = firewall.add_droplet(droplet_id)

        self.assertTrue(mock_get.called)
        self.assertTrue(mock_post.called)
        self.assertEqual(result, None)
        self.assertEqual(status, 204)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }

        expected_params = {}
        url, data = mock_post.call_args
        self.assertEqual(url[0], '{}/firewalls/{}/droplets'.format(
            endpoint, firewall_id))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)

    @patch('dosa.requests.get')
    @patch('dosa.requests.post')
    def test_dosa_firewall_add_droplet_already(self, mock_post, mock_get):
        """Test adding a droplet to firewall, which already have such
        droplet"""

        # get a droplet and firewall id
        droplet_id = 12345
        firewall_id = '99d5ef9c-2aa5-40ad-8507-2af7d65d099a'

        # prepare a response for a firewall object
        mock_get.return_value.status_code = 200

        # read data from file and update data with droplet_id
        firewall_data = json.loads(self._get_sample_data('firewall'))
        firewall_data['firewall']['droplet_ids'] = [droplet_id]

        # assign data to response
        mock_get.return_value.json.return_value = firewall_data

        mock_post.return_value.status_code = 204
        # there's no response for adding droplet (No Content)
        mock_post.return_value.text = None

        # get a firewall object
        firewall = dosa.Firewall(
            self.api_key, 'firewalls/{id}', id=firewall_id)

        # add a droplet to firewall
        result = firewall.add_droplet(droplet_id)

        self.assertTrue(mock_get.called)
        self.assertFalse(mock_post.called)
        self.assertEqual(result, None)

    @patch('dosa.requests.get')
    @patch('dosa.requests.delete')
    def test_dosa_firewall_delete_droplet(self, mock_delete, mock_get):
        # get a droplet and firewall id
        droplet_id = 12345
        firewall_id = '99d5ef9c-2aa5-40ad-8507-2af7d65d099a'

        # prepare a response for a firewall object
        mock_get.return_value.status_code = 200

        # read data from file and update data with droplet_id
        firewall_data = json.loads(self._get_sample_data('firewall'))
        firewall_data['firewall']['droplet_ids'] = [droplet_id]

        # assign data to response
        mock_get.return_value.json.return_value = firewall_data

        mock_delete.return_value.status_code = 204
        # there's no response for deleting droplet (No Content)
        mock_delete.return_value.text = None

        # get a firewall object
        firewall = dosa.Firewall(
            self.api_key, 'firewalls/{id}', id=firewall_id)

        # add a droplet to firewall
        status, result = firewall.remove_droplet(droplet_id)

        self.assertTrue(mock_get.called)
        self.assertTrue(mock_delete.called)
        self.assertEqual(result, None)
        self.assertEqual(status, 204)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }

        expected_params = {}
        url, data = mock_delete.call_args
        self.assertEqual(url[0], '{}/firewalls/{}/droplets'.format(
            endpoint, firewall_id))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)

    @patch('dosa.requests.get')
    @patch('dosa.requests.delete')
    def test_dosa_firewall_delete_droplet_error(self, mock_delete, mock_get):
        """Test adding a droplet to firewall, which already have such
        droplet"""

        # get a droplet and firewall id
        droplet_id = 12345
        firewall_id = '99d5ef9c-2aa5-40ad-8507-2af7d65d099a'

        # prepare a response for a firewall object
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('firewall'))

        mock_delete.return_value.status_code = 204
        # there's no response for adding droplet (No Content)
        mock_delete.return_value.text = None

        # get a firewall object
        firewall = dosa.Firewall(
            self.api_key, 'firewalls/{id}', id=firewall_id)

        # add a droplet to firewall
        result = firewall.remove_droplet(droplet_id)

        self.assertTrue(mock_get.called)
        self.assertFalse(mock_delete.called)
        self.assertEqual(result, None)

    def _get_sample_data(self, path):
        filename = '{}.json'.format(path)

        with open(os.path.join(api_sample_data, filename)) as handle:
            data = handle.read()

        return data
