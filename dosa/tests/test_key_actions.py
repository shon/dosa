import json
import os.path
from unittest import TestCase
from unittest.mock import patch

import dosa

endpoint = 'https://api.digitalocean.com/%s' % dosa.API_VERSION
api_sample_data = os.path.join(os.path.dirname(__file__), 'api_sample_data')


class TestDosaClientKeyActions(TestCase):
    @classmethod
    def setUp(self):
        self.api_key = 'my_fake_api_key'
        self.client = dosa.Client(self.api_key)

    @classmethod
    def tearDown(self):
        pass

    def test_dosa_client_created(self):
        client = dosa.Client(self.api_key)
        self.assertIsInstance(client, dosa.Client)

    @patch('dosa.requests.post')
    def test_dosa_key_create(self, mock_post):
        ssh_key_name = 'MyFakeSSHKey'
        ssh_key_value = 'myfakesshkey'
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = json.loads(
            self._get_sample_data('keys_create'))
        status, result = self.client.keys.create(
            name=ssh_key_name, public_key=ssh_key_value)
        self.assertEqual(1, len(result))
        self.assertTrue(mock_post.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = {
            'name': ssh_key_name,
            'public_key': ssh_key_value
        }
        url, data = mock_post.call_args
        self.assertEqual(url[0], '{}/account/keys'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertDictEqual(json.loads(data['data']), expected_data)

    @patch('dosa.requests.get')
    def test_dosa_key_list(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('keys'))
        status, result = self.client.keys.list()
        self.assertTrue(mock_get.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args
        self.assertEqual(url[0], '{}/account/keys'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    def _get_sample_data(self, path=''):
        return open(os.path.join(api_sample_data,
                                 '{}.json'.format(path))).read()
