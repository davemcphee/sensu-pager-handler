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

from config import get_config
from sensu_slackbot.sensu_slackbot_tasks import alert_loop as to_the_slack_mobile_slackman
logging.basicConfig(level=logging.WARN)


class SensuHandler(object):
    """
    Info we need to boot:
        a config source. Let's go with a yaml file for now.
    """
    def __init__(self):
        self.LOG = logging.getLogger(__name__)
        self.config = get_config()
        self.known_alerts = self.config['alertconfig'].keys()
        self.LOG.debug("Configured alerts: {}".format(self.known_alerts))

    def handle(self):
        """
        Get JSON data from stdin
        :return:
        """
        event_data = json.loads(sys.stdin.read())
        event_name = event_data['check']['name']
        event_client_name = event_data['client']['name']
        event_client_address = event_data['client']['address']
        self.LOG.debug("Received an event named {} from host {} [{}]".format(event_name, event_client_name, event_client_address))

        alert_config = self.config['alertconfig'][event_name]
        res = to_the_slack_mobile_slackman(event_data, alert_config)
        return 0

    def start_alerting_cycle(self, event):
        # loop through contacts configured for this event, ping them, wait 5 mins if no response, ping again
        # kinda pre-supposes slack as contact method.
        pass

    # I copied these from ruby. I don't know what they're supposed to do.
    def filter(self):
        pass

    def bail(self, msg):
        pass

    def _get_config(self):
        pass

if __name__ == '__main__':
    sh = SensuHandler()
    sh.handle()
