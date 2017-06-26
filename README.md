# sensu-pager-handler
a dumb sensu handler and his buddy, the slack bot
 * able to route each alert / check type to various users on slack based on config
 * per-person timer. If first person in list doens't reply within x minutes, move on to next person.
 * celery-based slackbot, able to monitor multiple conversations aynchronously
 * reporting: user one never acknowledged alert, but user two did within 2:32. Total time from alert to ack: 7:32 etc
 * external config - read routing / config info from DB / yaml file etc


Running the server:
    RABBIT_URL=user:pass@IP//vlan SLACK_TOKEN=abcdefghijklmnopqrstuvwxyz celery -A sensu_slackbot.sensu_slackbot_server 
    worker -l info

Overview: 
Sensu handler passes sensu event (json string) to celery task alert_loop(). This task tries to find event-specific
    configuration, and if it finds any, it goes through the contact list for that alert and starts a slack_ping() task
    for the first user.
    
If the first contact doesn't ack within 5 mins, we launch a new slack_ping() task for second user, and so on. 