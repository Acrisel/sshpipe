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
        bindir = os.path.join(os.path.dirname(here), 'bin')
        handler = os.path.join(bindir, 'sshpipe_socket_handler.py')
        self.mlogger.debug("Initiating callback tunnel: {}.".format(handler))
        self.tunnel = SSHTunnel(host, [handler, '--id', type(self).__name__, '--port', str(port),], logger=self.mlogger)
        self.mlogger.debug("Starting callback tunnel.")
        self.tunnel.start()

    def atstart(self, received):
        file = "{}{}".format(__file__, ".remote.log")
        self.mlogger.debug("Opening file: {}.".format(file))
        self.file = open(file, 'w')

    def atexit(self, received):
        if self.file is not None:
            self.file.close()
        self.mlogger.debug("Closing callback tunnel.")
        self.tunnel.close()
        for name, msg in zip(['returncode', 'stdout', 'stderr'], self.tunnel.response()):
            self.mlogger.debug("response {}:\n{}".format(name, msg))
        super(MySSHPipeHandler, self).atexit(received)

    def handle(self, received):
        self.file.write(str(received))
        self.mlogger.debug("Sending to callback tunnel: {}.".format(received))
        self.tunnel.send(str(received))


if __name__ == '__main__':
    parser = ap.ArgumentParser("Example parameters for aget process.")
    parser.add_argument("--host", type=str, required=False, default=1)
    parser.add_argument("--port", type=int, required=False, default=1)
    parser.add_argument("--id", type=str, required=False, dest='handler_id')
    args = parser.parse_args()

    client = MySSHPipeHandler(host=args.host, port=args.port, handler_id=args.handler_id)
    client.service_loop()
