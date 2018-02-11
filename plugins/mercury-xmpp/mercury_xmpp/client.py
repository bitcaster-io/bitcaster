import sleekxmpp
from mercury.logging import getLogger
logger = getLogger('mercury.plugins.xmpp')


class Client(sleekxmpp.ClientXMPP):
    def __init__(self, username, password, instance_name=None):
        jid = "%s/%s" % (username, instance_name) if instance_name else username
        super().__init__(jid, password)
        # self.instance_name = instance_name
        self.add_event_handler('session_start', self.start, threaded=False, disposable=True)
        # self.add_event_handler('message', self.receive, threaded=True, disposable=False)

        # if self.connect([server, port]):
        #     logger.info("Opened XMPP Connection")
        #     self.process(block=False)
        # else:
        #     raise Exception("Unable to connect to Google Jabber server")

    def __del__(self):
        self.close()

    def close(self):
        logger.info( "Closing XMPP Connection")
        self.disconnect(wait=False)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    # def send_msg(self, recipient, body):
    #     message = self.Message()
    #     message['to'] = recipient
    #     message['type'] = 'chat'
    #     message['body'] = body
    #
    #     logger.info( "Sending message: %s" % message)
    #     message.send()

    # def receive(self, message):
    #     if message['type'] in ('chat', 'normal'):
    #         logger.info( "XMPP Message: %s" % message)
    #         from_account = "%s@%s" % (message['from'].user, message['from'].domain)
    #         logger.info( "%s received message from %s" % (self.instance_name, from_account))
    #
    #         if self.instance_name in message['body'].lower():
    #             logger.info( "Caught test message: %s" % message)
    #             message.reply("%s was listening!" % self.instance_name).send()
    #         else:
    #             logger.info( "Uncaught command from %s: %s" % (from_account, message['body']))
