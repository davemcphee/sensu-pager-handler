# sensu-pager-handler
a dumb sensu handler and his buddy, the slack bot
 * able to route each alert / check type to various users on slack based on config
 * per-person timer. If first person in list doens't reply within x minutes, move on to next person.
 * celery-based slackbot, able to monitor multiple conversations aynchronously
 * reporting: user a never acknowledged alert, but user two did within 2:32. Total time from alert to ack: 7:32 etc
 * external config - read routing / config info from DB / yaml file etc


Running the server:
    RABBIT_URL=user:pass@IP//vlan SLACK_TOKEN=abcdefghijklmnopqrstuvwxyz celery -A sensu_slackbot.sensu_slackbot_server worker -l info
