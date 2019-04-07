import json
import os.path
from unittest import TestCase
from unittest.mock import patch

import dosa

endpoint = 'https://api.digitalocean.com/%s' % dosa.API_VERSION
api_sample_data = os.path.join(os.path.dirname(__file__), 'api_sample_data')


class TestDosaClientDomainRecordActions(TestCase):
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
    def test_get_domain_record(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('domain_record'))
        domain_name = 'example.com'
        dr = self.client.DomainRecords(domain=domain_name)
        dr.list()
        self.assertTrue(mock_get.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args
        self.assertEqual(
            url[0], '{}/domains/{}/records'.format(endpoint, domain_name))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    @patch('dosa.requests.post')
    def test_dosa_domain_record_create(self, mock_post):
        mock_post.return_value.status_code = 201
        mocked_return = json.loads(self._get_sample_data('domain_record'))
        mock_post.return_value.json.return_value = mocked_return
        domain_name = 'example.com'
        dr = self.client.DomainRecords(domain=domain_name)
        dr.create(type='A', name=domain_name, data='162.10.66.0')
        self.assertTrue(mock_post.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        url, data = mock_post.call_args
        self.assertEqual(
            url[0], '{}/domains/{}/records'.format(endpoint, domain_name))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        data_dict = json.loads(data['data'])
        self.assertEqual(
            data_dict['data'],
            mocked_return['domain_record']['data'])

    @patch('dosa.requests.put')
    def test_dosa_update_domain_record_by_id(self, mock_put):
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = json.loads(
            self._get_sample_data('domain_record'))
        domain_name = 'example.com'
        domain_record = 28448433
        dr = self.client.DomainRecords(domain=domain_name)
        record = dr.Record(record_id=domain_record)
        record.update(name='www')
        self.assertTrue(mock_put.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{"name": "www"}'
        url, data = mock_put.call_args
        self.assertEqual(url[0],
                         '{}/domains/{}/records/{}'.format(endpoint,
                                                           domain_name,
                                                           domain_record))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    def _get_sample_data(self, path=''):
        return open(os.path.join(api_sample_data,
                                 '{}.json'.format(path))).read()
