import stomp
import sys
import time
import datetime
import uuid
import yaml

# CLIENT_ID = 'sender-' + str(uuid.uuid4())

with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)

ACTIVEMQ_USER = settings['activemq']['user']
ACTIVEMQ_PASSWORD = settings['activemq']['password']
ACTIVEMQ_HOST = settings['activemq']['host']
ACTIVEMQ_PORT = settings['activemq']['port']
ACTIVEMQ_QUEUE = settings['activemq']['queue']
ACTIVEMQ_HEARTBEAT_SEND = settings['activemq']['heartbeat']['send']
ACTIVEMQ_HEARTBEAT_RECEIVE = settings['activemq']['heartbeat']['receive']

print(datetime.datetime.now())
conn = stomp.Connection([(ACTIVEMQ_HOST, ACTIVEMQ_PORT)], heartbeats=(ACTIVEMQ_HEARTBEAT_SEND,ACTIVEMQ_HEARTBEAT_RECEIVE))
#conn.connect(ACTIVEMQ_USER, ACTIVEMQ_PASSWORD, wait=True, headers={'client-id': CLIENT_ID})
conn.connect(ACTIVEMQ_USER, ACTIVEMQ_PASSWORD, wait=True)
for x in range(10):
    message = 'round 1> ' + str(datetime.datetime.now()) + ' ' + str(x) + ':' + ' '.join(sys.argv[1:])
    conn.send(body=message, destination=ACTIVEMQ_QUEUE)
conn.disconnect()