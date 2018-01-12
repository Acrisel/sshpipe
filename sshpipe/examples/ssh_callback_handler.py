#!/usr/bin/env python
'''
Created on Oct 3, 2017

@author: arnon
'''

import logging
from sshpipe import SSHPipeHandler

mlogger = logging.getLogger(__file__)


class MySSHPipeHandler(SSHPipeHandler):

    def __init__(self, *args, **kwargs):
        super(MySSHPipeHandler, self).__init__(*args, **kwargs)
        self.file = None

    def atstart(self, received):
        file = "{}{}".format(__file__, ".remote.log")
        self.mlogger.debug("Opening file: {}.".format(file))
        self.file = open(file, 'w')

    def atexit(self, received):
        if self.file is not None:
            self.file.close()
        super(MySSHPipeHandler, self).atexit(received)

    def handle(self, received):
        self.file.write(str(received))


if __name__ == '__main__':
    # TODO: add command line options

    client = MySSHPipeHandler()
    client.service_loop()