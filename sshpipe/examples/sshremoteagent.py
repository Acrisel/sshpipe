#!/usr/bin/env python
'''
Created on Oct 3, 2017

@author: arnon
'''

import pickle
import sys
import struct
from sshpipe import SSHPipeCallableHandler


class MySSHPipeClient(SSHPipeCallableHandler):

    def action(self, received):
        if not isinstance(received, str):
            received()
            return None
        elif received == self.term_action:
            # maybe worker prints to stdout
            return 0
        else:
            print("My bad worker: " + repr(received), file=sys.stderr)
            print(self.term_action)
            return 2


if __name__ == '__main__':
    import argparse

    # TODO: add command line options
    client = MySSHPipeClient()
    client.service_loop()
