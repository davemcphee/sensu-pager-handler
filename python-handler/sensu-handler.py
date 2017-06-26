#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
python sensu handler - now with decision making ability!

You know what, now that I've built the sensu slackbot, we can make this app as dumb as a box of rocks.
Just take every check event and forward it to slackbot, let it decide what to do.
"""

import json
import logging
import sys

from sensu_slackbot.sensu_slackbot_tasks import alert_loop as to_the_slack_mobile_slackman
logging.basicConfig(level=logging.WARN)


class SensuHandler(object):
    """
    Reads from stdin, passes it to slackbot. Just a dumb pipe.
    """
    def __init__(self):
        self.LOG = logging.getLogger(__name__)

    def handle(self):
        """
        Read & forward JSON data from stdin
        :return: 0
        """
        raw_data = sys.stdin.read()
        try:
            event_data = json.loads(raw_data)
            event_name = event_data['check']['name']
            event_client_name = event_data['client']['name']
            event_client_address = event_data['client']['address']
            self.LOG.debug("Received an event named {} from host {} [{}]".format(event_name, event_client_name,
                                                                                 event_client_address))
        except Exception as e:
            self.LOG.critical("Failed to parse JSON object: {}".format(raw_data))
            raise

        to_the_slack_mobile_slackman.delay(event_data)
        return 0

    # I copied these methods from the ruby handler. I don't know what they're supposed to do.
    def filter(self):
        pass

    def bail(self, msg):
        pass

if __name__ == '__main__':
    sh = SensuHandler()
    sh.handle()
