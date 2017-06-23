#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
python sensu handler - now with decision making ability!

TODO list:
    accept an alert - what does it look like? What data we got? JSON text? DONE
    read config from somewhere. what kind of info do we need? What decisions do we need to make? DONE
        What type of alert is this? DONE
        What is the response chain for this alert? (response chain: first farshid, 5 mins later, josh, 5 mins later,
            infra on call) DONE-  get this from config.yml file
        How do we alert the person? Slack? DONE - yeah slack. We need to interact with person.
        Wait 5 mins for the correct reply. IF we got it, quit. If not, alert next person in response chain
            This will need a bot ... maybe?
"""

import json
import logging
import sys

from config import get_config

logging.basicConfig(level=logging.DEBUG)


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


        pass

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

        # Do we know about this event?
        if event_name in self.known_alerts:
            # route it!
            self.LOG.debug("It's a {} system. I know this!".format(event_name))
            self.start_alerting_cycle(event_data)
        else:
            self.LOG.debug("I don't know this alert, routing to default contact Matthew D.")
        return 0

    def start_alerting_cycle(self, event):
        # loop through contacts configured for this event, ping them, wait 5 mins if no response, ping again
        # kinda pre-supposes slack as contact method.
        pass

    def filter(self):
        pass

    def bail(self, msg):
        pass

    def _get_config(self):
        pass

if __name__ == '__main__':
    sh = SensuHandler()
    sh.handle()
