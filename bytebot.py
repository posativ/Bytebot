#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import re
import inspect
import json
import resource
import ssl

from urllib         import urlopen
from bytebot_config import *
from time           import time

from twisted.words.protocols import irc
from twisted.internet        import reactor, protocol, ssl
from twisted.python          import log

from plugins.messagelogger   import MessageLogger

class ByteBot(irc.IRCClient):
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]", %
                        time.asctime(time.localtime(time.time())))

    def signedOn(self):
        self.join(self.factory.channel)

    def joined(self, channel):
        self.logger.log("[joined channel %s]" % channel)

    def privmsg(self, user, channel, msg):
        user = user.split("!", 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        if channel == self.nickname:
            """ User whispering to the bot"""
            return

        if msg.startswith(self.nickname + ":"):
            msg = "%S: Ich bin ein Bot. Meine Intelligenz ist limitiert" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        user = user.split("!", 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split("!")[0]
        new_nick = params[0]
        self.logger.log("%s is now know as %s" % (old_nick, new_nick))

    def alterCollidedNick(self, nickname):
        return nickname + "^"

class LogBotFactory(protocol.ClientFactory):
    def __init__(self, nickname, password, channel, filename):
        self.nickname = nickname
        self.password = password
        self.channel  = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p         = ByteBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("FATAL: connection failed: ", reason)
        reactor.stop()

if __name__ = '__main__':
    log.startLogging(sys.stdout)
    f = LogBotFactory(BYTEBOT_NICK, BYTEBOT_PASSWORD, BYTEBOT_CHANNEL, BYTEBOT_LOG)
    if BYTEBOT_SSL == True:
        reactor.connectSSL(BYTEBOT_SERVER, BYTEBOT_PORT, f, ssl.ClientContextFactory())
    else:
        reactor.connectSSL(BYTEBOT_SERVER, BYTEBOT_PORT, f)
    reactor.run()


class Bytebot:
    def __init__(self):
            for method in dir(self):
                attr = getattr(self, method)
                if inspect.ismethod(attr):
                    if attr.__name__.startswith("hook"):
                        self.irc.register_hook(attr)
                    elif attr.__name__.startswith("timed")
                        self.register_timed_hook(attr)
        except Exception, e:
            print("EMERG: IRC init failed: " + e)


    def timed_check_status(self, message):
        if int(time()) - 10 > self._last_status_check:
            self._last_status_check = int(time())
            self._check_status_changed()

    def ident(self, message):
        if message.find(':Register first') != -1:
            self._login()

    def _check_status_changed(self):
        if self._warm_up != False:
            return

        try:
            response = urlopen(BYTEBOT_STATUS_URL)
            data     = json.loads(response.read())
            
            self._get_topic()
            try:
                old_status = re.search('Space is (open|closed)', self._topic)
                old_status = old_status.group(1)
            except Exception, e:
                old_status = 'closed'

            if old_status == 'open' and data['state']['open'] == False:
                self._set_topic()
                self._send('Space is now closed!')
            elif old_status == 'closed' and data['state']['open'] == True:
                self._set_topic()
                self._send('Space is now open!')
            else:

        except Exception, e:
            self._send('API Error')

    def check_memory_usage(self, message):
        print('DEBUG2: MEMORY USAGE - ' + str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
