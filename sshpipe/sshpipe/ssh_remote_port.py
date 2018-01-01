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

import logging
from sshutil.sshpipe import SSHPipe
from sshutil.pipe_listener import pipe_listener_forever, EXIT_MESSAGE
import multiprocessing as mp

module_logger = logging.getLogger(__name__)


def remote_socket_agent(port, exit_message=EXIT_MESSAGE, pickle_loads=False, imports=None):
    ''' Forward SSH messages to port
    '''
    global module_logger
    controlq = mp.Queue()
    kwargs = {'queue':controlq, 'port':port, 'exit_message':exit_message, 'pickle_loads': pickle_loads, 'imports':imports, 'logger': module_logger,}
    listener = mp.Process(target=pipe_listener_forever, kwargs=kwargs, daemon=True)
    listener.start()
    
    active = True
    while active:
        msg = controlq.get()
        active = msg == EXIT_MESSAGE
        
        
class SSHRemotePort(SSHPipe):
    ''' Facilitates sending information to remote host:port via ssh channel
    '''
    def __init__(self, host, port, pack=False, exit_message=None, imports=None, logger=None, *args, **kwargs):
        self.host = host
        self.port = port
        self.pack = pack
        cmd_parts= ["ssh_remote_port.py --port {}".format(port)]
        if imports:
            cmd_parts.append("--imports {}".format(imports))
        if pack:
            cmd_parts.append("--pickle-loads")
        if exit_message:
            cmd_parts.append("--exit-message {}".format(exit_message))
            
        command = ' '.join(cmd_parts)
        super(SSHRemotePort, self).__init__(self.host, command, *args, logger=logger, **kwargs) #=module_logger)
        
    def start(self):
        super(SSHRemotePort, self).start(wait=0.2)
        

def cmdargs():
    import argparse
    import os
    
    filename = os.path.basename(__file__)
    progname = filename.rpartition('.')[0]
    
    parser = argparse.ArgumentParser(description="%s runs SSH Port Agent" % progname)
    parser.add_argument('--port', type=int, 
                        help="""Port to forward messages to.""")
    parser.add_argument('--exit-message', type=str, dest='exit_message', default=EXIT_MESSAGE,
                        help="""string to use as exit message, default: {}.""".format(EXIT_MESSAGE))
    parser.add_argument('--pickle-loads', action='store_true', default=False, dest='pickle_loads',
                        help='if set, will pikcle.loads() message before sending to port.')
    parser.add_argument('--imports', type=str, required=False, dest='imports', nargs='*',
                        help="""import module before pickle loads.""")
    args = parser.parse_args()  
    
    return args
    
if __name__ == '__main__':
    mp.freeze_support()
    mp.set_start_method('spawn')
    
    args = cmdargs()
    remote_socket_agent(args)
    
    