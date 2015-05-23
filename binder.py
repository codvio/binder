#!/usr/bin/env python2
# -*- coding: utf-8 -*-


# [dependencies] #######################################################################################################

from twisted.internet import protocol, reactor
from twisted.python   import failure


# [config] #############################################################################################################

port_start  = 60000
server_port = None


# [InternalServer] #####################################################################################################

class InternalServer(protocol.Protocol):

    # [constructor] ####################################################################################################

    def __init__(self, factory):

        self.factory = factory

    # [connectionMade] #################################################################################################

    def connectionMade(self):

        if self.factory.connected_instance is None:
            self.factory.connected_instance = self
        else:  # Allow only single connection
            self.transport.loseConnection()
            self.transport.connectionLost(failure.Failure(Exception("Only one connection allowed!")))

    # [connectionLost] #################################################################################################

    def connectionLost(self, reason):

        if self.factory.connected_instance == self:
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

        self.protocol         = InternalServer(self)
        self.protocol.factory = self

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

        self.factory.port         += 1
        self.internal_server_port  = reactor.listenTCP(self.factory.port, InternalServerFactory(self))

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

if __name__ == "__main__":

    try:
        server_port = reactor.listenTCP(1560, ExternalServerFactory(port_start))
        reactor.run()
    except KeyboardInterrupt:
        pass
