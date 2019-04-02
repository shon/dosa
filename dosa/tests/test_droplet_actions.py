import json
import os.path
from unittest import TestCase
from unittest.mock import patch

import dosa

endpoint = 'https://api.digitalocean.com/%s' % dosa.API_VERSION
api_sample_data = os.path.join(os.path.dirname(__file__), 'api_sample_data')


class TestDosaClientDropletActions(TestCase):
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
    def test_dosa_droplet_list(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('droplets'))
        status, result = self.client.droplets.list()
        self.assertEqual(1, len(result['droplets']))
        self.assertTrue(mock_get.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args
        self.assertEqual(url[0], '{}/droplets'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    @patch('dosa.requests.post')
    def test_dosa_droplet_create(self, mock_post):
        mock_post.return_value.status_code = 202
        mock_post.return_value.json.return_value = json.loads(
            self._get_sample_data('droplet_create'))
        status, result = self.client.droplets.create(name='terminator',
                                                     region='nyc2',
                                                     size='512mb',
                                                     image='ubuntu-14-04-x32',
                                                     ssh_keys=[12345])
        self.assertTrue(mock_post.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = {
            'name': 'terminator',
            'region': 'nyc2',
            'size': '512mb',
            'image': 'ubuntu-14-04-x32',
            'ssh_keys': [12345]
        }
        url, data = mock_post.call_args
        self.assertEqual(url[0], '{}/droplets'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        received_data = json.loads(data['data'])
        # assert that expected data was returned in sample data
        for key, value in expected_data.items():
            self.assertEqual(received_data[key], value)

    @patch('dosa.requests.get')
    def test_dosa_droplet_by_id(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('droplet_by_id'))
        data_sample = json.loads(self._get_sample_data('droplet_by_id'))
        droplet_id = data_sample['droplet']['id']
        droplet_ips = [ip['ip_address']
                       for ip in data_sample['droplet']['networks']['v4']]
        droplet_status = data_sample['droplet']['status']
        droplet = self.client.Droplet(droplet_id)
        status, droplet_info = droplet.info()
        self.assertEqual(droplet_id, droplet_info['droplet']['id'])
        self.assertTrue(mock_get.called)
        self.assertEqual(droplet_status, droplet.status())
        self.assertListEqual(droplet_ips, droplet.ip_addresses())
        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args
        self.assertEqual(url[0], '{}/droplets/{}'.format(endpoint, droplet_id))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    @patch('dosa.requests.delete')
    def test_dosa_droplet_delete(self, mock_delete):
        mock_delete.return_value.status_code = 204
        # there's no response for delete droplet (No Content)
        mock_delete.return_value.text = None
        droplet_id = 12345
        status, result = self.client.droplets.delete(droplet_id)

        self.assertTrue(mock_delete.called)
        self.assertEqual(result, None)
        self.assertEqual(status, 204)
        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}

        url, data = mock_delete.call_args
        self.assertEqual(url[0], '{}/droplets/{}'.format(endpoint, droplet_id))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)

    def _get_sample_data(self, path=''):
        return open(os.path.join(api_sample_data,
                                 '{}.json'.format(path))).read()
