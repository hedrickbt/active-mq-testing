import stomp
import sys
import time
import datetime
import uuid

# CLIENT_ID = 'receiver-' + str(uuid.uuid4())

def connect_and_subscribe(listener):
    #conn.connect('activemq-admin', 'w#7$k^PmIb0G^UoBZIS^OgBN4Sziaj', wait=True, headers={'client-id': CLIENT_ID})
    conn.connect('activemq-admin', 'w#7$k^PmIb0G^UoBZIS^OgBN4Sziaj', wait=True)
    conn.subscribe(destination='/queue/test', id=1, ack='auto')


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

        print("%s %s" % (datetime.datetime.now(),message))
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
        print("%s %s %s:%i" % (datetime.datetime.now(),'connecting', host_and_port[0], host_and_port[1]))

    def on_message(self, frame):
        self.print_frame(frame, 'received a message')
        for x in range(5):
            print(x)
            time.sleep(1)
        print('processed message')

    def on_disconnected(self):
        print()
        print("%s %s" % (datetime.datetime.now(),'disconnected'))
        connect_and_subscribe(self.conn)

    def on_disconnecting(self):
        print()
        print(datetime.datetime.now())
        print('disconnecting')

    def on_heartbeat(self):
        print()
        print("%s %s" % (datetime.datetime.now(),'received heartbeat'))

    def on_heartbeat_timeout(self):
        print()
        print("%s %s" % (datetime.datetime.now(),'heartbeat timeout'))

    def on_receipt(self, frame):
        self.print_frame(frame, 'receipt')

    def on_receiver_loop_completed(self, frame):
        self.print_frame(frame, 'receive loop completed')

    def on_send(self, frame):
        self.print_frame(frame, 'send')

print(datetime.datetime.now())
# print("client-id: {}", CLIENT_ID)
# I will send heartbeat every 15 seconds, server, please send me heartbeat every 10 seconds.
conn = stomp.Connection([('hedrickbt-activemq-stomp.poc.k8s.rainhail.com', 61613)], heartbeats=(15000,10000))
conn.set_listener('', MyListener(conn))
connect_and_subscribe(conn)
time.sleep(36000)
print(datetime.datetime.now())
conn.disconnect()