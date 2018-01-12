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
Created on Oct 10, 2017

@author: arnon
'''

from .pipe_listener import pipe_listener_forever
import multiprocessing as mp
import threading as th
import logging
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
import os
from acrilib import LevelBasedFormatter, LoggerAddHostFilter
import signal
import sys
from sshpipe import SSHPipe

mlogger = logging.getLogger()


class SSHPipeHandler(object):
    """ Pipe remote client wish message handler"""

    logging_config = {
        'level_formats': {
            logging.DEBUG: ("[ %(asctime)-15s ][ %(host)s ]"
                            "[ %(processName)-11s ][ %(levelname)-7s ]"
                            "[ %(message)s ]"
                            "[ %(module)s.%(funcName)s(%(lineno)d) ]"),
            'default': ("[ %(asctime)-15s ][ %(host)s ]"
                        "[ %(processName)-11s ][ %(levelname)-7s ]"
                        "[ %(message)s ]"),
            },
        'level': logging.DEBUG,
        'logdir': '/tmp',
        'encoding': 'utf8',
        'mode': 'a',
        'maxBytes': 0,
        'backupCount': 0,
        'delay': False,
        }

    TERM_MESSAGES = ['TERM', 'STOP', 'FINISH', 'EXIT', 'QUIT']

    def __init__(self, handler_id=None, term_messages=None, unpack=True,
                 imports=None, tolerance=0, caller_host=None,
                 caller_port=None):
        """
        Args:
            tolerance: indicate how to behave if couldn't understand message
                or handling failed.
                -1: tolerate all exception in message reception or handling.
                 0: zero tolerance, abort on first error
                 n: allow n errors before aborting (abort on error number n+1)
        """
        global mlogger
        self.term_messages = term_messages
        if term_messages is None:
            self.term_messages = SSHPipeHandler.TERM_MESSAGES
        self.term_message = self.term_messages[0]
        self.unpack = unpack
        self.imports = imports
        self.tolerance = tolerance
        self.handler_id = handler_id
        if handler_id is None:
            "sshpipe_handler_{}".format(os.getpid())
        self._exitmsg = ""
        self._exitcode = 0
        self.caller_host = caller_host
        self.caller_port = caller_port
        self._pipe = None

        sshpipe_config_file = \
            os.environ.get("SSHPIPE_CONFIG_FILE",
                           os.path.expanduser('~/.sshpipe'))
        file_config = {}
        if os.path.isfile(sshpipe_config_file):
            # TODO: read configuration for logging
            #       (logdir, formats, level, etc.)
            pass
        config = SSHPipeHandler.logging_config
        config.update(file_config)

        logq = mp.Queue()
        logfile = "{}.log".format(self.handler_id)
        logdir = config['logdir']
        if logdir is not None:
            logfile = os.path.join(logdir, logfile)

        file_handler_kwargs = {
            'filename': logfile,
            'mode': config['mode'],
            'maxBytes': config['maxBytes'],
            'backupCount': config['backupCount'],
            'encoding': config['encoding'],
            'delay': config['delay'],
            }

        level = config['level']
        formatter = LevelBasedFormatter(config['level_formats'])
        handler = RotatingFileHandler(**file_handler_kwargs)
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.qlogger = QueueListener(logq, handler,
                                     respect_handler_level=False)
        self.qlogger.start()

        queue_handler = QueueHandler(logq)
        mlogger.addHandler(queue_handler)
        mlogger.setLevel(level)
        mlogger.addFilter(LoggerAddHostFilter())
        self.mlogger = mlogger

        signal.signal(signal.SIGHUP, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

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
                self.handle(message)
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

    def service_loop(self):
        global mlogger
        self.message_queue = mp.Queue()
        self.started_event = mp.Event()

        pipe_listener_forever_kwargs = {
            'message_queue': self.message_queue,
            'started_event': self.started_event,
            'term_messages': self.term_messages,
            'unpack': self.unpack,
            'imports': self.imports,
            'logger': mlogger,
            }

        message_queue_loop_th = th.Thread(target=self.message_queue_loop,
                                          daemon=True)
        message_queue_loop_th.start()

        pipe_listener_forever(**pipe_listener_forever_kwargs)

        message_queue_loop_th.join()

        mlogger.debug("Completed service loop; exitcode: {}; exitmsg:{}."
                            .format(self._exitcode, self._exitmsg))

        if self._exitcode > 0:
            dest = sys.stderr
            print(self._exitmsg, dest)
            # TODO: exit must be a parameter choice
            exit(self._exitcode)

    def _create_callback_channel(self):
        global mlogger
        command = "sshpipe_socket_handler.py --port {}".format(
            self.caller_port)
        self._pipe = SSHPipe(host=self.caller_host, command=command,
                             logger=mlogger)

    def _send_callback(self, msg):
        if self._pipe:
            self._pipe.send(msg)

    def _close_callback_channel(self):
        if self._pipe:
            response = self.pipe.close()
            return response

    def atstart(self, received):
        global mlogger
        mlogger.debug("atstart: nothing to do, message: {}."
                      .format(received))

    def handle(self, received):
        global mlogger
        mlogger.debug("handle: nothing to do, message: {}."
                      .format(received))

    def atexit(self, received):
        global mlogger
        mlogger.debug("atexit: with message {}".format(received))
        self.qlogger.stop()
        msg = received
        if received not in self.term_messages:
            msg = self.term_message
        print(msg)

    def exit_gracefully(self, signo, stack_frame, *args, **kwargs):
        self.atexit(self.term_message)
        print(self.term_message)
