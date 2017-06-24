# sensu-pager-handler
sensu proxy-handler with a few features
 * able to route alerts based on user defined conditions
 * external config - read routing / config info from DB / yaml file etc


Running the server:
    RABBIT_URL=user:pass@IP//vlan celery -A sensu_slackbot.sensu_slackbot_server worker -l info
