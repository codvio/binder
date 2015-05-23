#!/usr/bin/env python
# -*- coding: utf-8 -*-


# [dependencies] #######################################################################################################

import sys

from twisted.internet import protocol, reactor


# [globals] ############################################################################################################

server_port = None


# [InternalServer] #####################################################################################################

class InternalServer(protocol.Protocol):

    # [constructor] ####################################################################################################

    def __init__(self, factory):

        self.factory = factory

    # [connectionLost] #################################################################################################

    def connectionLost(self, reason):

        self.factory.connected_instance = None

    # [dataReceived] ###################################################################################################

    def dataReceived(self, data):

        self.factory.external_server_instance.write_data(data)

    # [write_data] #####################################################################################################

    def write_data(self, data):

        self.transport.write(data)


# [InternalServerFactory] ##############################################################################################

class InternalServerFactory(protocol.Factory):

    # [constructor] ####################################################################################################

    def __init__(self, external_server_instance):

        self.external_server_instance = external_server_instance
        self.connected_instance       = None

    # [buildProtocol] ##################################################################################################

    def buildProtocol(self, addr):

        if self.connected_instance is None:
            self.protocol           = InternalServer(self)
            self.connected_instance = self.protocol

            self.external_server_instance.internal_protocol = self.protocol

            return self.protocol


# [ExternalServerFactory] ##############################################################################################

class ExternalServer(protocol.Protocol):

    # [constructor] ####################################################################################################

    def __init__(self, factory):

        self.factory              = factory
        self.internal_protocol    = None
        self.internal_server_port = None

    # [connectionMade] #################################################################################################

    def connectionMade(self):

        self.internal_server_port  = reactor.listenTCP(self.factory.port, InternalServerFactory(self))
        self.factory.port         += 1

    # [connectionLost] #################################################################################################

    def connectionLost(self, reason):

        if self.internal_protocol:
            self.internal_protocol.transport.loseConnection()
            self.internal_server_port.stopListening()

    # [dataReceived] ###################################################################################################

    def dataReceived(self, data):

        if self.internal_protocol:
            self.internal_protocol.write_data(data)

    # [write_data] #####################################################################################################

    def write_data(self, data):

        self.transport.write(data)


# [ExternalServerFactory] ##############################################################################################

class ExternalServerFactory(protocol.Factory):

    # [constructor] ####################################################################################################

    def __init__(self, port_start):

        self.port = port_start

    # [buildProtocol] ##################################################################################################

    def buildProtocol(self, addr):

        return ExternalServer(self)


# [main block] #########################################################################################################

def print_usage():
    print "\n"
    print 'Usage:'
    print '    binder.py <external server port> <internal server ports start>\n'
    print 'Example:'
    print '    binder.py 1560 60000'


# [main block] #########################################################################################################

if __name__ == "__main__":

    if not len(sys.argv) == 3:
        print_usage()
    else:
        try:
            listen_port = int(sys.argv[1])
            port_start  = int(sys.argv[2])

            if listen_port < 0 or listen_port > 65535 or port_start < 0 or port_start > 65535:
                print 'port numbers must be 0-65535'
            else:
                server_port = reactor.listenTCP(listen_port, ExternalServerFactory(port_start))
                reactor.run()
        except ValueError:
            print_usage()
        except KeyboardInterrupt:
            reactor.stop()
