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

from .. import pipe_listener_forever
import multiprocessing as mp
import threading as th
import logging 
import os 
from acrilib import LevelBasedFormatter, LoggerAddHostFilter
from .. import SSHPipeHandler
import signal
import sys

#from acrilib import LogSim

module_logger = logging.getLogger()

class SSHSubprocessClient(SSHPipeHandler):
    """ Pipe remote client wish message handler"""
        
    def __init__(self, cmd=[], calling_host=None, callback_port=None, *args, **kwargs):
        pass
        
def cmdargs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1', required=False,
                        help='')
    parser.add_argument('--port', type=int, required=True,
                        help='')
    args = parser.parse_args()
    return vars(args)

if __name__ == '__main__':
    args = cmdargs()
    
    # TODO: add command line options
    
    client = SSHSubprocessClient(**args)
    client.service_loop()
