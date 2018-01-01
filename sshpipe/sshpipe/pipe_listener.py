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
import sys
import struct
import pickle
import logging
import importlib
import os
from acrilib import TimedSizedRotatingHandler
# from acrilog.mplogger import MpLogger

module_logger = logging.getLogger(__name__)

EXIT_MESSAGE = 'TERM'


def set_logger(name=None, logdir='/tmp'):
    if name is not None:
        logger_file = name
    else:
        logger_file = "{}.{}.log"\
            .format(os.path.basename(__file__).rpartition('.')[0], os.getpid())
    logger_file = os.path.join(logdir, logger_file)
    logger_handler = TimedSizedRotatingHandler(logger_file,)
    logger = logging.getLogger()
    logger.addHandler(logger_handler)
    return logger


def imports_from_cmd(imports_str):
    imports = dict()

    for import_str in imports_str:
        import_file, _, import_modules_str = import_str.partition(':')
        import_modules = import_modules_str.split(':')
        file_modules = imports.get(import_file, list())
        file_modules.extend(import_modules)
        imports[import_file] = file_modules
    imports = [(import_file, set(modules))
               for import_file, modules in imports.items() if modules]
    return imports


def _imports(imports, queue, exit_message):
    imports = imports_from_cmd(imports)
    module_logger.debug("Importing {}.".format(imports))
    for import_file, import_modules in imports:
        if not import_file:
            for module in import_modules:
                module_logger.debug("Importing %s." % (module))
                try:
                    from importlib import import_module
                    import_module(module)
                except Exception as e:
                    module_logger.critical("Failed to import: %s." % (module))
                    module_logger.exception(e)
                    # signal to parent via stdout
                    print('TERM')
                    print(e, file=sys.stderr)
                    queue.put((exit_message, e))
                    return False
        else:
            for module in import_modules:
                module_logger.debug("Importing %s from %s."
                                    .format(module, import_file))
                try:
                    spec = importlib.util.spec_from_file_location(module, import_file)
                    spec_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(spec_module)
                    # sys.modules[args.import_module] = module # not needed for now
                except Exception as e:
                    module_logger.critical("Failed to import: %s %s;"
                                           .format(import_module, import_file))
                    module_logger.exception(e)
                    # signal to parant via stdout
                    print('TERM')
                    print(e, file=sys.stderr)
                    queue.put((exit_message, e))
                    return False
    return True


def pipe_recv_message(queue, exit_message=EXIT_MESSAGE):
    try:
        msgsize_raw = sys.stdin.buffer.read(4)
    except Exception as e:
        module_logger.critical('Failed to read STDIN.')
        module_logger.exception(e)
        queue.put((exit_message, e))
        return

    try:
        msgsize = struct.unpack(">L", msgsize_raw)
    except Exception as e:
        module_logger.critical('Failed pickle loads message size from STDIN; received: %s' % hex(msgsize_raw))
        module_logger.exception(e)
        queue.put((exit_message, e))
        return

    try:
        msg_pack = sys.stdin.buffer.read(msgsize[0])
    except Exception as e:
        module_logger.critical('Failed to read STDIN.')
        module_logger.exception(e)
        queue.put((exit_message, e))
        return


def pipe_listener(queue, term_messages=[EXIT_MESSAGE], unpack=False):
    ''' Pipe listener wait for one message.  Once receive (DONE or TERM) it ends.

    Args:
        imports: string in the form of [file]:module[:module ...]
            if file, all modules will be imported from file.
    '''
    global module_logger

    # in this case, whiting for possible termination message from server
    exit_message = term_messages[0]

    module_logger.debug('Trying to read STDIN message size.')
    try:
        msgsize_raw = sys.stdin.buffer.read(4)
    except Exception as e:
        module_logger.critical('Failed to read STDIN.')
        module_logger.exception(e)
        queue.put((exit_message, e))
        return False

    module_logger.debug('Trying to unpack message size: {}.'
                        .format(repr(msgsize_raw)))
    try:
        msgsize = struct.unpack(">L", msgsize_raw)
    except Exception as e:
        module_logger.critical(
            'Failed pickle loads message size from STDIN; received: {}.'
            .format(hex(msgsize_raw)))
        module_logger.exception(e)
        queue.put((exit_message, e))
        return False

    msgsize = msgsize[0]
    module_logger.debug('Trying to read STDIN message of size {}.'
                        .format(msgsize))
    try:
        msg_pack = sys.stdin.buffer.read(msgsize)
    except Exception as e:
        module_logger.critical('Failed to read STDIN.')
        module_logger.exception(e)
        queue.put((exit_message, e))
        return False

    if unpack:
        try:
            msg = pickle.loads(msg_pack)
        except Exception as e:
            module_logger.critical('Failed pickle loads message from STDIN.')
            module_logger.exception(e)
            queue.put((exit_message, e))
            return False
    else:
        msg = msg_pack

    module_logger.debug(
        'Received message from remote parent: {}; passing to main process.'
        .format(msg))

    queue.put((msg, ''))

    return msg not in term_messages  # == exit_message


def pipe_listener_forever(message_queue, started_event,
                          term_messages=[EXIT_MESSAGE], unpack=True,
                          imports=None, logger=None):
    ''' Same us pipe_listener, but loop until request to abort
    '''
    global module_logger

    if logger is not None:
        # module_logger = MpLogger.get_logger(logger_info)
        module_logger = logger

    if imports is not None:
        imported = _imports(imports, message_queue, term_messages[0])
        if not imported:
            return
    started_event.set()

    active = True
    while active:
        active = pipe_listener(message_queue, term_messages=term_messages,
                               unpack=unpack)
