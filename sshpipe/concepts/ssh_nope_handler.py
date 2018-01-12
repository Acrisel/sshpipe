#!/usr/bin/env python
'''
Created on Oct 3, 2017

@author: arnon
'''

import logging
from sshpipe import SSHChainHandler, SSHPipeHandler

mlogger = logging.getLogger(__file__)


class SSHNopeHandler(SSHPipeHandler):

    def __init__(self, *args, **kwargs):
        super(SSHNopeHandler, self).__init__(*args, **kwargs)

    def atstart(self, received):
        pass

    def atexit(self, received):
        super(SSHNopeHandler, self).atexit(received)

    def handle(self, received):
        print(str(received), end='')


if __name__ == '__main__':
    # TODO: add command line options

    client = SSHNopeHandler()
    client.service_loop()
