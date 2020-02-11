import json
from random import choice
from string import ascii_letters, digits
from locust import task

from base import LmsTasks

# use the following insigts query to update AVERAGE_CONTENT_LENGTH:
#
# SELECT sum(`request.headers.contentLength`)/count(`request.headers.contentLength`) FROM Transaction Where appName='prod-edge-edxapp-lms' AND name='WebTransaction/Function/track.views:user_track' SINCE 1 week ago
#
AVERAGE_CONTENT_LENGTH = 1606

# user_track API endpoint.  Use this location for POSTing tracking event data.
EVENT_API_PATH = '/event'


class TrackingTasks(LmsTasks):
    """
    Tasks representing tracking events reported by ajax requests.
    """

    def _random_simple_string(self, length):
        # for simplicity, chars in this pool should be only 1 byte long in
        # utf-8, and also won't expand into escapes when converting to json.
        char_pool = ascii_letters + digits
        random_chars = (choice(char_pool) for _ in range(length))
        return ''.join(random_chars)

    @task(9)
    def report_event(self):
        """
        POST a user tracking event.  This simulates event reports such as
        clicking the next button or jumping to a different secion.
        """
        # This variable represents the approximate overhead of the data (in the
        # form of urlencoded POST parameters), i.e. the number of bytes in the
        # request body less the random string. This is roughly based on the
        # number of characters in the boilerplate data below.
        approximate_data_overhead = 270
        random_string_length = AVERAGE_CONTENT_LENGTH - approximate_data_overhead
        random_string = self._random_simple_string(random_string_length)

        # The contents of the parameters are not significant, we just want to
        # structure the data in a way that won't cause the LMS to error.
        data = {
            'event_type': 'fake_event_for_load_testing',
            'event': '{{ "description": "this random tracking data is generated by https://github.com/edx/edx-load-tests", "random_event_data": "{}" }}'.format(random_string),
            'page': '/courses/{}'.format(self.course_id),
        }

        response = self.client.post(EVENT_API_PATH, data=data, headers=self.post_headers)

    @task(1)
    def stop(self):
        """
        Switch to another TaskSet.
        """
        self.interrupt()
