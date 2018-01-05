'''
Created on Oct 3, 2017

@author: arnon
'''
import os
import multiprocessing as mp
from sshpipe import SSHPipe

'''
    ssh_remote_handler_client.py instantiate an SSH pipe on remote host.
    At the far end of the pipe, it runs a Pipe Listener server that would
    receive messages and act upon.
'''


class SSHTunnle(object):
    def __init__(self, host, receiver):
        self.receiver = receiver
        self.host = host
        self.__sshagent = None
        self.__state = 'initial'

    def start(self, wait=0.2):
        self.__sshagent = sshagent = SSHPipe(self.host, self.receiver)
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


def run():
    # Cannot use os.path.dirname(__file__) when OSX,
    # since it adds /private prefix
    agent_dir = os.path.dirname(__file__) 
    agentpy = os.path.join(agent_dir, "ssh_remote_handler.py")
    # remote host IP address, or better yet, use host by name.
    host = 'ubuntud01_sequent'

    tunnel = SSHTunnle(host, agentpy)
    tunnel.start()
    tunnel.send("This is life.\n")
    tunnel.send("This is also life.\n")
    tunnel.send("This is yet another life.\n")
    tunnel.send("That is all, life.\n")
    tunnel.send("TERM")
    tunnel.close()
    print('Response:', tunnel.response())


if __name__ == '__main__':
    # mp.set_start_method('spawn')
    run()
