'''
Created on Oct 3, 2017

@author: arnon
'''
import os
from functools import reduce
from sshpipe import SSHPipe, SSHPipeHandler

'''
    ssh_remote_handler_client.py instantiate an SSH pipe on remote host.
    At the far end of the pipe, it runs a Pipe Listener server that would
    receive messages and act upon.
'''
STDOUT = 1
STDERR = 2


class SSHChain(object):
    ''' Creates and operates SSH tunnel to remote host and processing results as they come.

    SSH Chain is build upon SSHTunnel. DB Tunnel, starts an agent
    to process responses from remote handler as the session is in progress.

    This different from its sibling SSHTunnel that would process responses only when
    the tunnel is closed.

    SSHBDTunnel have its remote handler open a backwards SSHTunnel that sends responses
    through a backward SSHTunnel.

    Process Structure:
        At start(), SSHChain object initiated SSHBDHandler in remote_host using SSHTunnel.
        On remote, SSHChain initiates SSHTunnel back to callback host with callback handler.

        At close(), SSHChain would first terminate its callback handler.
        Then, it will terminate itself.

    '''

    CHAIN_HANDLER = os.path.join(os.path.dirname(__file__), 'ssh_chain_handler.py')

    def __init__(self, chain):
        ''' Initiates SSHBChain object.

        Args:
            chain: a list of tuples of (host, handler [, <pass STD expression>])
                host: ssh key tag configured in .ssh/config at remote host.
                handler: executable that would be initiated on callback_host
                    to process messages from remote handler on callback (local) host.
                <pass STD expression>, optional, is a bit composition of STDOUT and PASS_STDERR.
                    If not present, assumes STDOUT.
                    for example:
                        STDOUT ^ STDERR: will combine sdtout and stderr to next inline.
                        None: will pass none of the standard outputs. This is expected to be
                            the last tuple in the chain.

        '''
        self.chain = chain

    def start(self, wait=0.2):
        # flatten chain tuples into one list
        args = reduce(lambda x, y: x + list(map(str, y)), self.chain, [])

        self.__sshagent = sshagent = SSHPipe(self.remote_host, args)
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

