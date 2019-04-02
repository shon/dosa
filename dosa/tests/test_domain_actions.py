import json
import os.path
from unittest import TestCase
from unittest.mock import patch

import dosa

endpoint = 'https://api.digitalocean.com/%s' % dosa.API_VERSION
api_sample_data = os.path.join(os.path.dirname(__file__), 'api_sample_data')


class TestDosaClientDomainActions(TestCase):
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

    @patch('dosa.requests.get')
    def test_dosa_domain_list(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('domains'))
        status, result = self.client.domains.list()
        self.assertEqual(1, len(result['domains']))
        self.assertTrue(mock_get.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args
        self.assertEqual(url[0], '{}/domains'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    @patch('dosa.requests.post')
    def test_dosa_domain_create(self, mock_post):
        mock_post.return_value.status_code = 202
        mocked_return = {
            'domain': {
                'name': 'example.com',
                'ttl': 1800,
                'zone_file': 'null'
            }
        }
        mock_post.return_value.json.return_value = mocked_return
        status, result = self.client.domains.create(
            name='example.com', ip_address='1.2.3.4')
        self.assertTrue(mock_post.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        url, data = mock_post.call_args
        self.assertEqual(url[0], '{}/domains'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        data_json = json.loads(data['data'])
        self.assertEqual(data_json['name'], mocked_return['domain']['name'])

    @patch('dosa.requests.delete')
    def test_dosa_domain_delete(self, mock_delete):
        mock_delete.return_value.status_code = 204
        # there's no response for delete domain (No Content)
        mock_delete.return_value.text = None
        domain_name = 'example.com'
        status, result = self.client.domains.delete(domain_name)

        self.assertTrue(mock_delete.called)
        self.assertEqual(result, None)
        self.assertEqual(status, 204)
        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}

        url, data = mock_delete.call_args
        self.assertEqual(url[0], '{}/domains/{}'.format(endpoint, domain_name))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)

    def _get_sample_data(self, path=''):
        return open(os.path.join(api_sample_data,
                                 '{}.json'.format(path))).read()
