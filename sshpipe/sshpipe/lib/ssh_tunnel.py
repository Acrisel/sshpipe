# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
'''
Created on Oct 3, 2017

@author: arnon
'''
import os
from sshpipe import SSHPipe

'''
    ssh_tunnel.py instantiate an SSH pipe on remote host.
    At the far end of the pipe, it runs a Pipe Listener server that would
    receive messages and act upon.
'''


class SSHTunnel(object):
    ''' Creates and operates SSH tunnel to remote host.

    SSH Tunnel is based on SSHPipe starting in one end and SSHPipeHandler
    based executable running in the remote end.

    '''

    def __init__(self, remote, receiver):
        ''' Initiates SSHTunnle object.

        Args:
            remote: ssh key tag configured in .ssh/config such that is set
                in target host to start with the right environment.
            receiver: executable that establishes SSHPipeHandler object.
                String or list of command string parts.

        '''
        self.receiver = receiver
        self.remote = remote
        self.__sshagent = None
        self.__state = 'initial'

    def start(self, wait=0.2):
        self.__sshagent =\
            sshagent = SSHPipe(host=self.remote, command=self.receiver)
        sshagent.start(wait=wait)

        if not sshagent.is_alive():
            raise RuntimeError("SSHAgent is not alive.")

        self.__state = 'start'
        return self

    def send(self, message):
        if self.__state != 'start':
            raise RuntimeError("Attempted send() without starting the tunnel.")
        self.__sshagent.send(message)

    def is_alive(self):
        return self.__sshagent.is_alive()

    def response(self):
        if self.__state != 'close':
            raise RuntimeError("Attempted response() without closing the tunnel.")
        return self.__sshagent.response()

    def close(self):
        if self.__state == 'start':
            self.__sshagent.close()
            self.__state = 'close'
