# Copyright 2017, Google LLC All rights reserved.
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

from __future__ import absolute_import

import mock
import pytest

from google.cloud.pubsub_v1.subscriber import futures
from google.cloud.pubsub_v1.subscriber._protocol import streaming_pull_manager


class TestStreamingPullFuture(object):
    def make_future(self):
        manager = mock.create_autospec(
            streaming_pull_manager.StreamingPullManager, instance=True
        )
        future = futures.StreamingPullFuture(manager)
        return future

    def test_default_state(self):
        future = self.make_future()

        assert future.running()
        assert not future.done()
        future._manager.add_close_callback.assert_called_once_with(
            future._on_close_callback
        )

    def test__on_close_callback_success(self):
        future = self.make_future()

        future._on_close_callback(mock.sentinel.manager, None)

        assert future.result() is True
        assert not future.running()

    def test__on_close_callback_failure(self):
        future = self.make_future()

        future._on_close_callback(mock.sentinel.manager, ValueError("meep"))

        with pytest.raises(ValueError):
            future.result()

        assert not future.running()

    def test_cancel(self):
        future = self.make_future()

        future.cancel()

        future._manager.close.assert_called_once()
        assert future.cancelled()
