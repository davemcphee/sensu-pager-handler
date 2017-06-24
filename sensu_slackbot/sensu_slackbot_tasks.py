"""
list of stuff our slack bot need to do.
"""

from __future__ import absolute_import, unicode_literals

import time
import os

from .sensu_slackbot_server import app
from celery import result as celery_result
from slackclient import SlackClient



# from celery import chain - chain the slack calls to successive contacts?
# from datetime import datetime


def slack_setup():
    slack_token = os.getenv('SLACK_TOKEN')
    sc = SlackClient(slack_token)
    return sc


@app.task
def init():
    sc = slack_setup()
    sc.api_call(
        "chat.postMessage",
        channel="@alexs",
        text="Sensu AlertBot v0.0.1-dev1 is online and awaiting incoming alerts from sensu"
    )


@app.task
def alert_loop(event, config):
    """
    given an event object (JSON obj, see EOF) and various config info we've deigned to send along (in particular: contacts list)
    start the process of slacking each contact in order, and giving them some time to respond. On failure, move on to next
    contact.
    :param event: json / dict of event, see EOF for typical example
    :param config: dict from config, everything associated with this event type (name?)
    :return: Some kind of report? In JSON? Eg.: pinged first contact at 06:32, got not reply within 5 mins, pinged second contact
    at 06:37, got reply within 2:32, stop.
    """
    alert_start_time = time.time()
    alert_ackd_timestamp = None
    contact_attempts = []

    for contact in config['contacts']:
        # call each contact in turn. make sure they are aware what their index is in the list - third guy better wake up
        res = slack_ping.delay(contact, event, config, config['contacts'].index(contact))
        try:
            acked = res.get(delay=5*60)
        except celery_result.TimeoutError as e:
            # no response in 5 mins, move on to next BUT store the job in case they reply later?
            contact_attempts.append((contact, res))
            continue

        if res.successful():
            alert_ackd_timestamp = time.time()
            break
        else:
            # uhhhh how did we get here
            raise Exception("ummm.")


@app.task
def slack_ping(contact, event, config, list_position):
    # sends initial chat, then loop sleeps for 5 mins waiting for reply
    alert_acknowledged = False
    sc = slack_setup()
    sc.api_call(
        "chat.postMessage",
        channel="@alexs",
        text="Sensu AlertBot v0.0.1-dev1 is online and awaiting incoming alerts from sensu"
    )
    # the alert_loop() will only wait for 5 mins for user to ack before moving on to next, but that doesn't mean
    # we can't wait a little longer, and check if they ever woke up at all. 30 mins?
    start = int(time.time())
    stop_time = start + (30 * 60)
    while True:
        new_lines = sc.rtm_read()
        for line in new_lines:
            if ':thisisfine:' in line:
                alert_acknowledged = True
                break
        time.sleep(5)
        if time.time() > stop_time:
            break

    if alert_acknowledged:
        return int(time.time()) - start
    else:
        return 0

"""
sensu event:

{
  "command": "capture_hc",
  "subscribers": [
    "capture_hc"
  ],
  "interval": 300,
  "occurrences": 1,
  "refresh": 14400,
  "handlers": [
    "default",
    "slack",
    "mailer"
  ],
  "name": "capture_hc",
  "issued": 1498255290,
  "executed": 1498255290,
  "duration": 0.687,
  "output": "CRITICAL - CAPTURE_hc reports 11 channels offline | CHECK_ELAPSED_TIME=0.573s CHECK_TRIES_USED=1 OK=405 ZOMBIE=0 NON_FP=11\n  Channel sessions currently offline:\n    2,2009,6202 Animal_Planet\n    2,2010,7002 VH1\n    2,2010,7012 MTV\n    2,2021,5719 Sky_Arts\n    2,2026,4704 Sky_News\n    2,2029,5560 Nickelodeon\n    2,2061,8931 BBC_News_HD\n    2,2067,50205 Boomerang\n    2,2109,52250 Syfy_Channel\n    2,2111,53280 BT_Sport_2\n    3,3225,21020 NET 5\n",
  "status": 2,
  "type": "standard",
  "history": [
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2",
    "2"
  ],
  "total_state_change": 0
}
"""