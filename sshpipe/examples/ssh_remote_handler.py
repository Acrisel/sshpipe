#!/usr/bin/env python
'''
Created on Oct 3, 2017

@author: arnon
'''
import os
import logging
from sshpipe import SSHPipeHandler
import argparse as ap

mlogger = logging.getLogger(__file__)


class MySSHPipeHandler(SSHPipeHandler):

    def __init__(self, count, *args, **kwargs):
        super(MySSHPipeHandler, self).__init__(*args, **kwargs)
        print('Super initiated', type(super(MySSHPipeHandler, self)).__name__, list(super(MySSHPipeHandler, self).__dict__.keys()))
        self.count = count
        self.file = None

    def atstart(self, received):
        file = "{}{}".format(__file__, ".remote.log")
        if not hasattr(super(MySSHPipeHandler, self), 'mlogger'):
            raise RuntimeError("Super missing mlogger method.")
        if not hasattr(self, 'mlogger'):
            raise RuntimeError("Self missing mlogger method.")
        self.mlogger.debug("Opening file: {}.".format(file))
        self.file = open(file, 'w')

    def atexit(self, received):
        if self.file is not None:
            self.file.close()
        super(MySSHPipeHandler, self).atexit(received)

    def handle(self, received):
        for _ in self.count:
            self.file.write(str(received))


if __name__ == '__main__':
    # TODO: add command line options
    parser = ap.ArgumentParser("Example parameters for aget process.")
    parser.add_argument("--count", type=int, required=False, default=1)

    args = parser.parse_args()

    client = MySSHPipeHandler(count=args.count, handler_id=os.path.basename(__file__))
    client.service_loop()
