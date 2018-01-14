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
Created on Aug 27, 2017

@author: arnon
'''

import pickle
import struct
import multiprocessing as mp
import subprocess as sp
import time
import logging
import os
from logging.handlers import QueueListener, QueueHandler
import signal
import enum
from acrilib import LoggerAddHostFilter


mlogger = logging.getLogger(__file__)


class SSHPipeQueueHandler(logging.Handler):
    def __init__(self, logger):
        super(SSHPipeQueueHandler, self).__init__()
        self.logger = logger

    def emit(self, record):
        self.logger.handle(record)


def stdbin_decode(value, encoding='utf8'):
    try:
        value = value.decode(encoding)
    except Exception:
        pass
    if value.endswith('\n'):
        value = value[:-1]
    return value


def remote_agent(where, command, pipe_read, pipe_write, communicateq, config,
                 encoding, name=None, callback=None, logq=None, ):
    ''' Runs SSH command overriding its stdin and stdout with pipes.

    Args:
        where: user@host or host string.
        command: string or list of command parts to run under ssh. 
        pipe_read, pipe_write: read and write ends of multiprocessing Pipe().
        communicateq: multiprocessing queue to puss back response.
        callback: to invoke when agent is terminated.

    remote_agent is intended to run as a mulitprocessing process.  It uses
    subprocess run to run ssh command on remote host. remote_agent overrides
    subprocess stdin of subprocess with pipe_read.

    remote_agent collects stdout and stderr and pass them back via
    communicate queue.
    '''
    global mlogger

    if logq is not None:
        # if name is not None:
        mlogger = logging.getLogger()
        mlogger.addHandler(QueueHandler(logq))
        mlogger.addFilter(LoggerAddHostFilter())
    pipe_write.close()

    # convert pipe end to opened file descriptor, so it can be passed to
    # subprocess.
    pipe_readf = os.fdopen(os.dup(pipe_read.fileno()), 'rb')

    cmd = ["ssh"]
    if config:
        cmd.append("-F {}".format(config))

    if isinstance(command, str):
        command = [command]
    cmd += [where] + command

    mlogger.debug('Starting subprocess run({})'.format(cmd))
    sshrun = sp.run(cmd, shell=False, stdin=pipe_readf, stdout=sp.PIPE,
                    stderr=sp.PIPE, check=False,)

    returncode, stdout, stderr = (sshrun.returncode,
                                  sshrun.stdout.decode(encoding),
                                  sshrun.stderr.decode(encoding))
    response = (returncode, stdout, stderr)

    error = '' if not stderr else '\n' + stderr
    mlogger.debug(('Response placed in SSH queue: returncode: {}, '
                   'stdout: {}, stderr: {}').format(repr(returncode),
                                                    stdout, error))
    communicateq.put(response)
    if callback is not None:
        callback(returncode, stdout, stderr)
    pipe_readf.close()
    exit(returncode)


class SSHPipeState(enum.Enum):
    initiated = 0
    started = 1
    closed = 2


class SSHPipe(object):
    ''' Facilitates creation of agent process on remote host using ssh and
    feeding that process with data to process.
    '''
    def __init__(self, host, command, name=None, user=None,
                 term_message='TERM', config=None, encoding='utf8',
                 callback=None, logger=None):
        ''' SSHPipe object runs command on remote host with the intention to
        pass workloads throughout the lifetime of the run.

        Assumptions:
            ssh key configuration among cluster hosts.
                set .profile with: source /var/venv/eventor/bin/activate
                create environment ssh keys:
                    ssh-keygen -t rsa -C "envname" -f "id_rsa_envname"
                add to authorized_keys proper key:

command=". ~/.profile_envname; if [ -n \"$SSH_ORIGINAL_COMMAND\" ];
then eval \"$SSH_ORIGINAL_COMMAND\"; else exec \"$SHELL\"; fi" ssh-rsa ...

        Args:
            host: remote host.
            command: to run on remote host. String or list of command string parts.
            user: user to use to access remote host.
            config: SSH configuration to use. ~/.ssh/config .
            callback: if available, would be invoked once the agent in remote
            host is terminated.
                e.g., callback maybe a method that place result in a queue or
                send to a port. callback function should have the following
                calling arguments:returncode, stdout, stderr
            encoding: to use in decoding stdout and stderr.
            logger: logger object (logging).
        '''
        global mlogger
        if logger is not None:
            mlogger = logger

        self.term_message = term_message

        self.pipe_read, self.pipe_write = mp.Pipe()
        self.__qlogger = None
        self.__logq = mp.Queue()

        self.__communicateq = mp.Queue()
        self.where = \
            "{}{}".format('' if user is None else "@{}".format(user), host)
        self.command = command
        self.callback = callback

        self.pipe_writef = None
        self.result = None
        self.config = config
        self.encoding = encoding
        self.name = name
        self.__state = SSHPipeState.initiated

    def start(self, wait=1):
        ''' Starts process wherein SSH command will be executed.

        Args:
            wait: seconds to sleep between check process status.
        '''
        global mlogger

        if self.__state == SSHPipeState.started:
            return

        self.__qlogger = QueueListener(self.__logq,
                                       SSHPipeQueueHandler(mlogger))
        self.__qlogger.start()

        remote_agent_kwargs = {
            'where': self.where,
            'command': self.command,
            'pipe_read': self.pipe_read,
            'pipe_write': self.pipe_write,
            'communicateq': self.__communicateq,
            'config': self.config,
            'encoding': self.encoding,
            'name': self.name,
            'logq': self.__logq,
            'callback': self.callback,
            # 'logger':mlogger,
            }

        try:
            self.__agent = mp.Process(target=remote_agent,
                                      kwargs=remote_agent_kwargs, daemon=True)
            self.__agent.start()
        except Exception:
            raise
        self.pid = self.__agent.pid

        mlogger.debug("Agent activated: {}.".format(self.__agent.pid))

        if wait is not None:
            while True:
                time.sleep(wait)
                mlogger.debug("Waiting for start: alive: {}, exitcode: {}"
                              .format(self.__agent.is_alive(),
                                      self.__agent.exitcode))
                if self.__agent.is_alive() or \
                   self.__agent.exitcode is not None:
                    break

        if self.is_alive():
            mlogger.debug("Agent is running: {}.".format(self.__agent.pid))
            self.__state = SSHPipeState.started
        else:
            mlogger.debug("Agent is dead: {}.".format(self.response()))
            self.close()

        self.pipe_read.close()
        self.pipe_writef = os.fdopen(os.dup(self.pipe_write.fileno()), 'wb')

        signal.signal(signal.SIGHUP, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def is_alive(self):
        ''' Returns True if remote_agent process is alive.
        '''
        return self.__agent.is_alive() and self.__communicateq.empty()

    def prepare(self, msg, pack=True):
        ''' Returns byte message prefixed by its length packed into bytes.

        Args:
            msg: object to prepate.
            pack: if set, pickle dumps msg.
        '''
        workload = msg
        if pack:
            workload = pickle.dumps(msg)
        msgsize = len(workload)
        mlogger.debug('Preparing message of size: %s.' % (msgsize,))
        msgsize_packed = struct.pack(">L", msgsize)
        return msgsize_packed + workload

    def send(self, msg, pack=True):
        ''' Writes msg into remote_agent pipe (process' stdin)

        Args:
            msg: message object
            pack: if set, pickle dumps msg.
        '''
        request = self.prepare(msg, pack=pack)
        mlogger.debug(
             'Writing message of actual size {} to pipe.'
             .format(len(request)))

        self.pipe_writef.write(request)

    def response(self, timeout=None):
        ''' Wait for response from remote_agent.

        Args:
            timeout: if set, limits wait time.

        Returns:
            (returncode, stdout, stderr) resulted by remote_agent
        '''
        global mlogger

        mlogger.debug('Getting response from SSH control queue.')
        if self.result is None:
            try:
                result = self.__communicateq.get(timeout=timeout)
            except Exception:
                result = None

            if result:
                encoding = self.encoding
                returncode, stdout, stderr = (
                    result[0], stdbin_decode(result[1], encoding=encoding),
                    stdbin_decode(result[2], encoding=encoding))
                if not stdout:
                    stdout = self.term_message
                self.result = returncode, stdout, stderr
        mlogger.debug('Received from SSH control queue: {}'
                      .format(repr(self.result)))
        return self.result

    def close(self, msg=None):
        ''' Sends termination message to remote_agent.

        Args:
            msg: termination message, defaults to 'TERM'

        Returns:
            same as response()
        '''
        global mlogger

        if self.__state == SSHPipeState.closed:
            return self.response()

        if msg is None:
            msg = self.term_message

        if self.is_alive():
            mlogger.debug('Sending {} to pipe.'.format(msg))
            self.send(msg)
        else:
            mlogger.debug('Process is not alive, skipping {}.'.format(msg))
            pass
        if self.pipe_writef:
            self.pipe_writef.close()
        response = self.response()
        mlogger.debug('Joining with subprocess.')
        self.__agent.join()
        mlogger.debug('Subprocess joined.')
        if self.__qlogger is not None:
            self.__qlogger.stop()
        self.__state = SSHPipeState.closed
        return response

    def exit_gracefully(self, signo, stack_frame, *args, **kwargs):
        self.close()

    def __del__(self):
        self.close()

    def join(self, timeout=None):
        ''' Waits for remote_agent to finish.

        Args:
            timeout: limits time wait as in Process.join()
        '''
        self.__agent.join(timeout)
