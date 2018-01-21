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
from sshpipe.lib.sshconfig import load, loads, dump, dumps
from sshpipe.lib.sshpipe import SSHPipe
from sshpipe.lib.sshpipe_callable_handler import SSHPipeCallableHandler
from sshpipe.lib.pipe_listener import pipe_listener, pipe_listener_forever, EXIT_MESSAGE, set_logger
from sshpipe.lib.sshpipe_handler import SSHPipeHandler
from sshpipe.lib.ssh_tunnel import SSHTunnel
# from sshpipe.lib.ssh_chain import SSHChain
# from sshpipe.lib.ssh_chain_handler import SSHChainHandler

__author__ = 'arnon'
__version__ = '0.5.2'

