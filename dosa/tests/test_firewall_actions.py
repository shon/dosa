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

        firewall = self.client.firewalls.get_firewall_by_name('webserver')

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

        status, result = self.client.firewalls.create(**params)
        self.assertTrue(mock_post.called)

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
        print(data_json)
        self.assertEqual(data_json['name'], params['name'])

    @patch('dosa.requests.delete')
    def test_dosa_firewall_delete(self, mock_delete):
        mock_delete.return_value.status_code = 204
        # there's no response for delete firewall (No Content)
        mock_delete.return_value.text = None
        firewall_name = '99d5ef9c-2aa5-40ad-8507-2af7d65d099a'
        status, result = self.client.firewalls.delete(firewall_name)

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
                endpoint, firewall_name))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)

    def _get_sample_data(self, path):
        filename = '{}.json'.format(path)

        with open(os.path.join(api_sample_data, filename)) as handle:
            data = handle.read()

        return data
