from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

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
