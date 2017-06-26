# -*- coding: utf-8 -*-
"""
list of stuff our slack bot need to do.
"""

from __future__ import absolute_import, unicode_literals

import logging
import os
import time
from collections import OrderedDict
from datetime import datetime

from celery import result as celery_result
from slackclient import SlackClient

from sensu_slackbot.config import get_config as _get_config
from sensu_slackbot.sensu_slackbot_server import app
# from celery import chain - chain the slack calls to successive contacts?

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class SensuEvent(object):
    """
    Simple object representing a sensu event with a few utility functions and a nice __repr__()
    """
    def __init__(self, event):
        assert isinstance(event, dict)
        self.event_raw = event
        try:
            self.check_name = event['check']['name']
            self.check_timestamp = event['timestamp']
            self.check_timestamp_human = datetime.fromtimestamp(self.check_timestamp).strftime('%c')
            self.client_name = event['client']['name']
            self.client_address = event['client']['address']
            self.client_name = event['client']['name']
            # anything else? I guess it's all in self.event_raw

        except Exception as e:
            raise e
        LOG.debug("Created new SensuEvent: {}".format(self))

    def __repr__(self):
        return "SensuEvent <{}({}) - {} UTC ({}s old)>".format(self.check_name,
                                                           self.client_name,
                                                           self.check_timestamp_human,
                                                           self.check_age_in_seconds())

    def check_age_in_seconds(self):
        now = int(time.time())
        return int(now - self.check_timestamp)


def slack_setup():
    """
    Returns a slack client object. I tink these are just requests.Session objects so prob don't need to cache them.
    :return: SlackClient
    """
    slack_token = os.getenv('SLACK_TOKEN')
    sc = SlackClient(slack_token)
    return sc


def get_event_config(event):
    """
    Given an event, returns the config for that event, or None if none found
    :param event: SensuEvent object
    :return: config dict or None
    """
    # TODO: return default config is none found. Need a default config though.
    return _get_config()['alertconfig'].get(event.check_name, None)


@app.task
def alert_loop(event):
    """
    given an event object (JSON obj, see EOF), convert it to a SensuEvent object, get that event's config, and start
    attempting to page the event's contacts
    :param event: json / dict of event, see example for typical example_check.json
    :return: Some kind of report? In JSON? Eg.: pinged first contact at 06:32, got not reply within 5 mins, pinged second
    contact at 06:37, got reply within 2:32, stop.
    """
    LOG.debug("Received Sensu alert: raw event: {}".format(event))
    sensu_event = SensuEvent(event)
    LOG.info("Received Sensu alert: {}".format(sensu_event))
    config = get_event_config(sensu_event)
    if config is None:
        LOG.debug("Event has no defined configuration.")
        return
    else:
        LOG.debug("Event configuration found, proceeding.")

    alert_start_time = time.time()
    alert_ackd_timestamp = None
    contact_attempts = []

    # convert contacts to slack user IDs
    contacts_dict = map_contacts_to_ids(config['contacts'])

    for c_name, c_id in contacts_dict.items():
        # call each contact in turn. make sure they are aware what their index is in the list - third guy better wake up
        # .delay
        res = slack_ping.delay(c_name, c_id, event)
        try:
            acked = res.get(delay=5*60)
        except celery_result.TimeoutError as e:
            # no response in 5 mins, move on to next BUT store the job and check back again later
            contact_attempts.append((c_name, res))
            continue

        if res.successful():
            # do something w/ the fact that contact ack'ed this alert, then exit
            return
        else:
            # move on to next in list. Let's hope there is a next.
            continue


def map_contacts_to_ids(user_list):
    """
    takes a list of slack usernames and maps them to slack IDs, eg alexs = u'U1SP90YBG'
    :param user_list: list of slack user names
    :return: dict {u'alexs': u'U1SP90YBG'}
    """
    # TODO: Cache these lookups?
    if isinstance(user_list, (str, unicode)):
        user_list = [user_list]

    sc = slack_setup()
    all_users = sc.api_call('users.list')
    user_map = OrderedDict()

    for contact in user_list:
        tmp = [user['id'] for user in all_users['members'] if user['name'] == contact]
        user_map[contact] = tmp[0]

    return user_map


@app.task
def slack_ping(contact_name, contact_uid, event):
    """
    sends initial chat, then loop sleeps for 5 mins waiting for reply
    :param contact_name: username of user to contact
    :param contact_uid: slack uid of user to contact
    :param event: SensuEvent object
    :return:
    """
    alert_acknowledged = False
    sc = slack_setup()

    # im.open opens a direct message with a user, but doesn't send anything.
    im_open = sc.api_call('im.open',
                          user=contact_uid,
                          return_im=True)

    # Now we need the direct message channel ID, which we can post and read from as normal.
    im_channel_id = im_open['channel']['id']

    # the alert_loop() will only wait for 5 mins for user to ack before moving on to next, but that doesn't mean
    # we can't wait a little longer, and check if they ever woke up at all. 30 mins? Does this block a celery queue?
    start = int(time.time())
    stop_time = start + (30 * 60)

    # TODO: RTM websockets won't work, can't post complex messages or attachments like buttons. So this is all useless.
    while True:
        # check for response from user, return if yes, otherwise sleep and check again, until time is up.
        time.sleep(5)
        if time.time() > stop_time:
            break

    if alert_acknowledged:
        return int(time.time()) - start
    else:
        return 0

if __name__ == '__main__':
    pass
    # with open('example_check.json') as json_data:
    #     d = json.load(json_data)
    # ev = SensuEvent(d)
    # print(ev)
