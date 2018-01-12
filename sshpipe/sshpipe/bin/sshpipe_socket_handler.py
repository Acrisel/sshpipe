'''
Created on Oct 18, 2017

@author: arnon
'''

from sshpipe import SSHPipeHandler
import logging
from logging.handlers import SocketHandler
import pickle
import struct

module_logger = logging.getLogger(__file__)


class SSHPipeSocketHandler(SSHPipeHandler, SocketHandler):
    ''' SSHPipeSocketHandler modeled over logging.handlers.SocketHandler
    '''

    def __init__(self, port, host='17.0.0.1', *args, **kwargs):
        SSHPipeHandler.__init__(self, *args, **kwargs)
        SocketHandler.__init__(self, host, port)

        if port is None:
            self.address = host
        else:
            self.address = (host, port)

    def makePickle(self, record):
        """
        Pickles the record in binary format with a length prefix, and
        returns it ready for transmission across the socket.
        """
        if isinstance(record, str):
            s = pickle.dumps(record)
        else:  # object
            d = dict(record.__dict__)
            s = pickle.dumps(d, 1)
        slen = struct.pack(">L", len(s))
        return slen + s

    def atstart(self, receieved):
        # file = "{}{}".format(__file__, ".remote.log")
        # self.module_logger.debug("Opening file: {}.".format(file))
        # self.file = open(file, 'w')

        # call create socket to prevent it being called at first handle.
        self.createSocket()

    def atexit(self, received):
        # if self.file is not None:
        #     self.file.close()
        SSHPipeHandler.atexit(self, received)
        SocketHandler.close(self)

    def handle(self, received):
        """
        Send a pickled string to the socket.

        This function allows for partial sends which can happen when the
        network is busy.
        """
        # self.file.write(str(received))
        SocketHandler.emit(self, received)


def cmdargs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        required=False,
                        help='')
    parser.add_argument('--port', type=int, required=False,
                        help='')
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    args = cmdargs()

    # TODO: add command line options

    client = SSHPipeSocketHandler(**args)
    client.service_loop()
