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
import os
import multiprocessing as mp
import sshutil_examples.sshtypes as sshtypes
from sshpipe import SSHPipe

import logging

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def run(host):
    agent_dir = os.path.dirname(__file__) 
    agentpy = os.path.join(agent_dir, "sshremoteagent.py")

    sshagent = SSHPipe(host, agentpy, logger=logger)
    sshagent.start()

    if not sshagent.is_alive():
        raise Exception(sshagent.response())

    worker = sshtypes.RemoteWorker()
    sshagent.send(worker)

    if not sshagent.is_alive():
        raise Exception(sshagent.response())

    sshagent.send(worker)

    response = sshagent.close()
    print('response: ', response)


def cmdargs():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default='arnon-mbp',
                        help="host to connect to")
    args = parser.parse_args()

    return vars(args)


if __name__ == '__main__':
    mp.set_start_method('spawn')
    args = cmdargs()
    run(**args)
