import stomp
import sys
import time
import datetime
import uuid
import yaml

SUBSCRIBER_ID = str(uuid.uuid4())
#CLIENT_ID = 'receiver-' + str(uuid.uuid4())

CONN_COUNT = 0

with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)

ACTIVEMQ_USER = settings['activemq']['user']
ACTIVEMQ_PASSWORD = settings['activemq']['password']
ACTIVEMQ_HOST = settings['activemq']['host']
ACTIVEMQ_PORT = settings['activemq']['port']
ACTIVEMQ_QUEUE = settings['activemq']['queue']
ACTIVEMQ_HEARTBEAT_SEND = settings['activemq']['heartbeat']['send']
ACTIVEMQ_HEARTBEAT_RECEIVE = settings['activemq']['heartbeat']['receive']


class MyListener(stomp.ConnectionListener):
    def __init__(self, conn):
        self.conn = conn

    def print_frame(self, frame, message):
        print()

        if message == "send" \
            and hasattr(frame, 'cmd') \
            and frame.cmd == None \
            and hasattr(frame, 'body') \
            and frame.body == None \
            and hasattr(frame, 'headers') \
            and len(frame.headers) == 0:
            message = message + " heartbeat"

        print("[%i] %s %s" % (CONN_COUNT,datetime.datetime.now(),message))
        if hasattr(frame, 'body'):
            print('\tbody: "%s"' % frame.body)
        else:
            print('\tno body')
        if hasattr(frame, 'cmd'):
            print('\tcmd: "%s"' % frame.cmd)
        else:
            print('\tno cmd')
        if hasattr(frame, 'headers'):
            print('\theaders: "%s"' % str(frame.headers))
        else:
            print('\tno headers')

    def on_error(self, frame):
        self.print_frame(frame, 'received an error')

    def on_before_message(self, frame):
        self.print_frame(frame, 'before message')

    def on_connected(self, frame):
        self.print_frame(frame, 'connected')

    def on_connecting(self, host_and_port):
        print()
        print("[%i] %s %s %s:%i" % (CONN_COUNT,datetime.datetime.now(),'connecting',
                                    host_and_port[0], host_and_port[1]))

    def on_message(self, frame):
        self.print_frame(frame, 'received a message')
        for x in range(5):
            print(x)
            time.sleep(1)
        print('processed message')

    def on_disconnected(self):
        # There is a bug, if you try to reconnect using the existing connection
        # the new connection will not send heartbeats.  It will receive heartbeats.
        # https://github.com/jasonrbriggs/stomp.py/issues/351
        # This is why the main code now loops indefinitely to see if the connection
        # has been lost and then creates a brand new connection.
        print()
        print("[%i] %s %s" % (CONN_COUNT,datetime.datetime.now(),'disconnected'))

    def on_disconnecting(self):
        print()
        print("[%i] %s %s" % (CONN_COUNT,datetime.datetime.now(),'disconnecting'))

    def on_heartbeat(self):
        print()
        print("[%i] %s %s" % (CONN_COUNT,datetime.datetime.now(),'received heartbeat'))

    def on_heartbeat_timeout(self):
        print()
        print("[%i] %s %s" % (CONN_COUNT,datetime.datetime.now(),'heartbeat timeout'))

    def on_receipt(self, frame):
        self.print_frame(frame, 'receipt')

    def on_receiver_loop_completed(self, frame):
        self.print_frame(frame, 'receive loop completed')

    def on_send(self, frame):
        self.print_frame(frame, 'send')

print(datetime.datetime.now())
# print("client-id: {}", CLIENT_ID)

conn = None
while True:
    print('[%i] %s Checking if need to create stomp connection' % (CONN_COUNT,datetime.datetime.now()))
    if conn is None or not conn.is_connected():
        CONN_COUNT = CONN_COUNT + 1
        print('[%i] %s Starting a new stomp connection' % (CONN_COUNT,datetime.datetime.now()))
        # I will send heartbeat every 15 seconds, server, please send me heartbeat every 10 seconds.
        conn = stomp.Connection([(ACTIVEMQ_HOST, ACTIVEMQ_PORT)], heartbeats=(ACTIVEMQ_HEARTBEAT_SEND,ACTIVEMQ_HEARTBEAT_RECEIVE))
        conn.set_listener('', MyListener(conn))

        #conn.connect(ACTIVEMQ_USER, ACTIVEMQ_PASSWORD, wait=True, headers={'client-id': CLIENT_ID})
        conn.connect(ACTIVEMQ_USER, ACTIVEMQ_PASSWORD, wait=True)
        conn.subscribe(destination=ACTIVEMQ_QUEUE, id=SUBSCRIBER_ID, ack='auto')
    time.sleep(30)

