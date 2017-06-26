# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from celery import Celery

RABBIT_URL = os.getenv('RABBIT_URL')
BACKEND_URL = RABBIT_URL  # Share existing RabbitMQ? Use .. elasticsearch?!?!?! omg

app = Celery('tasks',
             broker='pyamqp://{}'.format(RABBIT_URL),
             backend='rpc://{}'.format(BACKEND_URL),
             include=[
                 'sensu_slackbot.sensu_slackbot_tasks'
             ]
             )

if __name__ == '__main__':
    app.start()
