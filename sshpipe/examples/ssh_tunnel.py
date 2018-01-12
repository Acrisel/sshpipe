'''
Created on Oct 3, 2017

@author: arnon
'''
import os
from sshpipe import SSHTunnel


def run():
    # Cannot use os.path.dirname(__file__) when OSX,
    # since it adds /private prefix
    agent_dir = os.path.dirname(__file__) 
    agentpy = os.path.join(agent_dir, "ssh_remote_handler.py")
    print('agentpy:', agentpy)
    # remote host IP address, or better yet, use host by name.
    host = 'ubuntud01_sequent'

    tunnel = SSHTunnel(host, [agentpy, "--count 1"])
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
