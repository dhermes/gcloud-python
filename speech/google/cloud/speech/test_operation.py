# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest


class OperationTests(unittest.TestCase):

    OPERATION_NAME = '123456789'

    def _getTargetClass(self):
        from google.cloud.speech.operation import Operation
        return Operation

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_ctor_defaults(self):
        client = _Client()
        operation = self._makeOne(client, self.OPERATION_NAME)
        self.assertEqual(operation.name, '123456789')
        self.assertFalse(operation.complete)
        self.assertIsNone(operation.metadata)
        self.assertIsNone(operation.results)

    def test_from_api_repr(self):
        from unit_tests._fixtures import OPERATION_COMPLETE_RESPONSE
        from google.cloud.speech.operation import Transcript
        from google.cloud.speech.metadata import Metadata
        RESPONSE = OPERATION_COMPLETE_RESPONSE

        client = _Client()
        operation = self._getTargetClass().from_api_repr(client, RESPONSE)

        self.assertEqual('123456789', operation.name)
        self.assertTrue(operation.complete)

        self.assertIsInstance(operation.results[0], Transcript)
        self.assertEqual(operation.results[0].transcript,
                         'how old is the Brooklyn Bridge')
        self.assertEqual(operation.results[0].confidence, 0.98267895)
        self.assertTrue(operation.complete)
        self.assertIsInstance(operation.metadata, Metadata)
        self.assertEqual(operation.metadata.progress_percent, 100)

    def test_update_response(self):
        from unit_tests._fixtures import ASYNC_RECOGNIZE_RESPONSE
        from unit_tests._fixtures import OPERATION_COMPLETE_RESPONSE
        RESPONSE = ASYNC_RECOGNIZE_RESPONSE

        client = _Client()
        operation = self._getTargetClass().from_api_repr(client, RESPONSE)
        self.assertEqual(operation.name, '123456789')
        operation._update(OPERATION_COMPLETE_RESPONSE)
        self.assertTrue(operation.complete)

    def test_poll(self):
        from google.cloud.speech.operation import Metadata
        from unit_tests._fixtures import ASYNC_RECOGNIZE_RESPONSE
        from unit_tests._fixtures import OPERATION_COMPLETE_RESPONSE
        RESPONSE = ASYNC_RECOGNIZE_RESPONSE
        client = _Client()
        connection = _Connection(OPERATION_COMPLETE_RESPONSE)
        client.connection = connection

        operation = self._getTargetClass().from_api_repr(client, RESPONSE)
        self.assertFalse(operation.complete)
        operation.poll()
        self.assertTrue(operation.complete)
        self.assertIsInstance(operation.metadata, Metadata)
        self.assertEqual(operation.metadata.progress_percent, 100)
        requested = client.connection._requested
        self.assertEqual(requested[0]['method'], 'GET')
        self.assertEqual(requested[0]['path'],
                         'operations/%s' % (operation.name,))

    def test_poll_complete(self):
        from unit_tests._fixtures import OPERATION_COMPLETE_RESPONSE
        from unit_tests._fixtures import OPERATION_INCOMPLETE_RESPONSE
        RESPONSE = OPERATION_INCOMPLETE_RESPONSE

        client = _Client()
        connection = _Connection(OPERATION_COMPLETE_RESPONSE)
        client.connection = connection
        operation = self._getTargetClass().from_api_repr(client, RESPONSE)

        self.assertFalse(operation.complete)
        operation.poll()  # Update the operation with complete data.

        with self.assertRaises(ValueError):
            operation.poll()
        requested = client.connection._requested
        self.assertEqual(requested[0]['method'], 'GET')
        self.assertEqual(requested[0]['path'],
                         'operations/%s' % (operation.name,))


class _Connection(object):
    def __init__(self, response=None):
        self.response = response
        self._requested = []

    def api_request(self, method, path):
        self._requested.append({'method': method, 'path': path})
        return self.response


class _Client(object):
    connection = None
