'''
Created on Oct 3, 2017

@author: arnon
'''
import os
from functools import reduce
from sshpipe import SSHChain
import platform


def os_path_correct(path):
    system = platform.system()
    if system == 'Darwin':
        parts = path.split(os.path.sep)
        if parts[0] == '/private':
            path = os.path.join(*parts[1:])
    return path


def run():
    # Cannot use os.path.dirname(__file__) when OSX,
    # since it adds /private prefix
    this_dir = os.path.dirname(__file__)
    proj_dir = os.path.dirname(this_dir)
    agentpy = os.path.join(this_dir, "ssh_remote_handler.py")
    nopepy = os.path.join(proj_dir, "concepts", "ssh_nope_handler.py")
    # remote host IP address, or better yet, use host by name.

    head = SSHChain([('ubuntud01_sequent', nopepy),
                     ('arnon-mbp-sequent', agentpy)])
    head.start()
    head.send("This is life.\n")
    head.send("This is also life.\n")
    head.send("This is yet another life.\n")
    head.send("That is all, life.\n")
    head.send("TERM")
    head.close()
    print('Response:', head.response())


if __name__ == '__main__':
    # mp.set_start_method('spawn')
    run()
