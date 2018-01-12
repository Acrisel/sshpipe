#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
'''
Created on Oct 3, 2017

@author: arnon
'''

import logging
from sshpipe import SSHPipeHandler
import argparse

mlogger = logging.getLogger(__file__)


class SSHChainHandler(SSHPipeHandler):
    ''' Chain handler object is SSHPipeHandler callable.

    At start it would initiate 
    '''

    def __init__(self, cars, *args, **kwargs):
        super(SSHChainHandler, self).__init__(*args, **kwargs)
        self.cars = cars

    def message_queue_loop(self, ):
        ''' loops on message_queue running handler on messages received.
        If control message receive, run appropriate control.

        message_queue_loop is design to run on a parallel thread to loop
        forever.
        Pipe listener's loop_forever fetch messages from STDIN into message queue for
        message_queue_loop to handle.
        '''
        global mlogger
        visited_atstart = False
        while True:
            mlogger.debug("Getting from message_queue.")
            received = self.message_queue.get()

            if received is None:
                continue

            message, error = received
            errmsg = '' if not error else "; error: {}.".format(error)
            mlogger.debug("Message queue received: message: {}{}"
                          .format(repr(message), errmsg))

            if error:
                if self.tolerance == 0:
                    self._exitmsg = error
                    self._exitcode = 1
                    break
                self.tolerance -= 1

            if not visited_atstart:
                if self.caller_host and self.caller_port:
                    self._create_callback_channel()
                    self._send_callback('ATSTART {}'.format(self.handler_id))

                mlogger.debug("Message queue not visited atstart yet.")
                visited_atstart = True
                try:
                    self.atstart(message)
                except Exception as error:
                    mlogger.debug("Exception from atstart: {}."
                                  .format(error))
                    self._exitmsg = error
                    self._exitcode = 2
                    break

            if message in self.term_messages:
                break

            try:
                result = self.handle(message)
            except Exception as error:
                mlogger.debug("Exception from handler: {}."
                              .format(error))
                self._exitmsg = error
                self._exitcode = 3
                break

        self._send_callback('ATEXIT {}'.format(self.handler_id))
        self._close_callback_channel()
        try:
            self.atexit(message)
        except Exception as error:
            mlogger.debug("Exception from atexit: {}.".format(error))
            self._exitmsg = error
            self._exitcode = 4
        loop_message = "." if self._exitcode == 0 else " with error."
        msg = "Completed message queue loop{}".format(loop_message)
        mlogger.debug(msg)


def argcmd():
    parser = argparse.ArgumentParser('SSHChainHandler')
    parser.add_argument('cars', type=str, nargs="+", )
    return parser


if __name__ == '__main__':
    # TODO: add command line options
    cmd = argcmd()
    client = SSHChainHandler(cmd.car, cmd.cdr)
    client.service_loop()
