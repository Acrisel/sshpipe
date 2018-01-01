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
from sshpipe.sshconfig import load, loads, dump, dumps
from sshpipe.sshpipe import SSHPipe
from sshpipe.sshpipe_callable_handler import SSHPipeCallableHandler
from sshpipe.pipe_listener import pipe_listener, pipe_listener_forever, EXIT_MESSAGE, set_logger
from sshpipe.sshpipe_handler import SSHPipeHandler

__author__ = 'arnon'
__version__ = '0.5.0'

