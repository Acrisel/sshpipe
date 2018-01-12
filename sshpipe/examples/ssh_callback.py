'''
Created on Jan 12, 2018

@author: arnon
'''

import socket
from contextlib import closing
import os
from sshpipe import SSHTunnel

'''
This example utilizes SSHPipe to establish worker on remote host.
The agent then establishes another SSHPipe back into originator.
Through the back-pipe, agent sends back information to originator process.
To collect response via call-back, originator start a socket listener.
Socket information is sent via SSHPipe to agent which will use that as
part of the callback.
'''


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
        return port


def run():
    # Cannot use os.path.dirname(__file__) when OSX,
    # since it adds /private prefix
    agent_dir = os.path.dirname(__file__)
    agentpy = os.path.join(agent_dir, "ssh_callback_handler.py")
    # remote host IP address, or better yet, use host by name.
    host = 'ubuntud01_sequent'

    callback_host = 'arnon-mbp-sequent'
    callback_port = find_free_port()

    tunnel = SSHTunnel(host, [agentpy, '--host', callback_host, '--port', callback_port])
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
