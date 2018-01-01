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
        self.__sshaagent = None

    def start(self):
        sshagent = SSHPipe(self.host, self.receiver)
        self.__sshaagent = sshagent.start(wait=0.2)

        if not sshagent.is_alive():
            print("Agent not alive", sshagent.response())
            self.__sshaagent = None
            exit(1)

    def send(self, message):
        self.__sshaagent.send(message)

    def is_alive(self):
        return self.__sshagent.is_alive()

    def response(self):
        return self.__sshagent.response()

    def close(self):
        self.__sshagent.close()


def run():
    # Cannot use os.path.dirname(__file__) when OSX,
    # since it adds /private prefix
    agent_dir = os.path.dirname(__file__) 
    agentpy = os.path.join(agent_dir, "ssh_remote_handler_server.py")
    # remote host IP address, or better yet, use host by name.
    host = 'ubuntud01_eventor'

    sshagent = SSHPipe(host, agentpy)
    sshagent.start(wait=0.2)

    if not sshagent.is_alive():
        print("Agent not alive", sshagent.response())
        exit(1)

    sshagent.send("This is life.\n")
    sshagent.send("This is also life.\n")
    sshagent.send("This is yet another life.\n")
    sshagent.send("That is all, life.\n")
    sshagent.send("TERM")

    if not sshagent.is_alive():
        print(sshagent.response())
        exit()

    response = sshagent.close()
    # if response:
    #     exitcode, stdout, stderr = response
    print('Response: ', response)


if __name__ == '__main__':
    mp.set_start_method('spawn')
    run()
