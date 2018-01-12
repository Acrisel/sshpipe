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

from ..pipe_listener import pipe_listener_forever
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
        
def run(args, *, input=None, stdout=None, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None):
    ''' Simulate python's subprocess run over sshpipe
    '''
    
    