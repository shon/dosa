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
    def test_dosa_image_list(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('images'))
        status, result = self.client.images.list()
        self.assertEqual(1, len(result['images']))
        self.assertTrue(mock_get.called)

        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args
        self.assertEqual(url[0], '{}/images'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    @patch('dosa.requests.get')
    def test_dosa_image_n_of_requests(self, mock_get):
        """Test n of requests equal to n of pages"""

        # prepare a fake request
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('images'))

        images = self.client.images.all()

        self.assertEqual(len(images), 1)
        self.assertEqual(mock_get.call_count, 1)

    @patch('dosa.requests.get')
    def test_dosa_image_by_search(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(
            self._get_sample_data('images_search'))
        images_list = self.client.images.search('ubuntu')

        # image is a list of dictionaries
        self.assertIsInstance(images_list, list)
        self.assertEqual(1, len(images_list))

        # assert method called
        self.assertTrue(mock_get.called)
        expected_headers = {
            'Content-Type': 'application/json',
            'authorization': 'Bearer {}'.format(self.api_key)
        }
        expected_params = {}
        expected_data = '{}'
        url, data = mock_get.call_args

        self.assertEqual(url[0], '{}/images'.format(endpoint))
        self.assertDictEqual(data['headers'], expected_headers)
        self.assertDictEqual(data['params'], expected_params)
        self.assertEqual(data['data'], expected_data)

    def _get_sample_data(self, path=''):
        return open(os.path.join(api_sample_data,
                                 '{}.json'.format(path))).read()
