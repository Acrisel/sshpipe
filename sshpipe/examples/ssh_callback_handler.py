#!/usr/bin/env python
'''
Created on Oct 3, 2017

@author: arnon
'''

import logging
import argparse as ap
import os
from sshpipe import SSHPipeHandler, SSHTunnel

mlogger = logging.getLogger(__file__)


class MySSHPipeHandler(SSHPipeHandler):

    def __init__(self, host, port, *args, **kwargs):
        super(MySSHPipeHandler, self).__init__(*args, **kwargs)
        self.file = None
        here = os.path.dirname(__file__)
        bin = os.path.join(os.path.dirname(here), 'bin')
        socket_handler = os.path.join(bin, 'sshpipe_socket_handler.py')
        tunnel = SSHTunnel(host, [socket_handler, '--port', port,])

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
    parser = ap.ArgumentParser("Example parameters for aget process.")
    parser.add_argument("--host", type=str, required=False, default=1)
    parser.add_argument("--port", type=int, required=False, default=1)

    args = parser.parse_args()

    client = MySSHPipeHandler(host=args.host, port=args.port, handler_id=os.path.basename(__file__))
    client.service_loop()
