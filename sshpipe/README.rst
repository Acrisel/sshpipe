=======
sshpipe
=======

---------------------------------------------------
SSH tools to manage and channel data to remote host
---------------------------------------------------

.. contents:: Table of Contents
   :depth: 2

Overview
========

    .. _Eventor: https://github.com/Acrisel/eventor
    .. _Sequent: https://github.com/Acrisel/sequent
    
    *sshpipe* was build as part of Eventor_ and Sequent_ to allow distributed processing using *SSH*. Usually, network based system are using ports to communicate between server and clients. However, in development environment, there may be many developers in need to individual port assignments. The management of such operation can become overwhelming.
    
    With SSH tunneling, each developer can manage its own environment. Using virtualenvs and SSH keys, developer can manage himself connections between servers and clients they are working on. 
    
    If you have comments or insights, please don't hesitate to contact us at support@acrisel.com

sshconfig
=========
	
    sshconfig is used to read SSH configuration file and give access to information stored there. It can be used also to save SSH configuration.
    
Loads and dumps
---------------
    
    *loads()*, *load()* methods are used to read SSH configuration from string stream or file respectively into *SSHConfig* object. 
    *dumps()*, *dump()* methods are used to write *SSHConfig* object to string stream or file respectively.
    
SSHConfig Class
---------------

    SSHConfig class holds SSH configuration as read by *load()* or *loads()*. It can then be stored back into SSH configuration file with sshconfig's *dump()* and *dumps().  *SSHConfig* provides *get()* method to retrieve SSH settings.

    Future functionality:
    
    1. validation of configuration.
    #. manipulation of configuration (e.g., add key, change flags, etc.)
    
SSHPipe
=======

    SSHPipe class is used to initiate an SSH channel to a process running in remote host. SSHPipe is initiated with the command for the agent process. It would then start the agent (commonly an object of *SSHPipeClient* or of a class inheriting from it.) 
    
    Once agent is started, SSHPipe provides methods to send the agent work assignments. When agent is done or fails, it would communicate back to SSHPipe object. The method *response()* can be used to retrieve that response.
    
Example
-------

    This example shows a SSHPipe creation from one host to another with. The service in the remote host will accept string message sent via the pipe and would store them into a file.
    
    *sshremotehandlerusage.py*, below, initiates  

    .. code:: python
        :number-lines:
    
        import os
        import multiprocessing as mp
        from sshpipe import SSHPipe

        def run():
            agent_dir = '/var/acrisel/sand/acris/sshpipe/sshpipe/sshpipe_examples' 
            agentpy = os.path.join(agent_dir, "sshremotehandler.py")
            host = 'ubuntud01_eventor' # SSH config host name of remote server.
    
            sshagent = SSHPipe(host, agentpy)
            sshagent.start()
    
            if not sshagent.is_alive():
                print("Agent not alive", sshagent.response())
                exit(1)
    
            sshagent.send("This is life.\n")
            sshagent.send("This is also life.\n")
            sshagent.send("This is yet another life.\n")
            sshagent.send("That is all, life.\n")
            sshagent.send("TERM")
    
            if not sshagent.is_alive():
                print(sshagent.response())
                exit()
    
            response = sshagent.close()
            if response:
                exitcode, stdout, stderr = response
            print('Response: ', response)
    
        if __name__ == '__main__':
            mp.set_start_method('spawn')
            run()
            
    The remote agent *sshremotehandler.py* is would run through SHHPipe and would loop awaiting input on its *stdin* stream. 
    
    .. code:: python
        :number-lines:
        
        import logging
        from sshpipe import SSHPipeHandler

        module_logger = logging.getLogger(__file__)

        class MySSHPipeHandler(SSHPipeHandler):
    
            def __init__(self, *args, **kwargs):
                super(MySSHPipeHandler, self).__init__(*args, **kwargs)
                self.file = None
                
            def atstart(self, received):
                file = "{}{}".format(__file__, ".remote.log")
                self.module_logger.debug("Opening file: {}.".format(file))
                self.file = open(file, 'w')
        
            def atexit(self, received):
                if self.file is not None:
                    self.file.close()
                super(MySSHPipeHandler, self).atexit(received)
    
            def handle(self, received):
                self.file.write(str(received))     
                
        if __name__ == '__main__':
            client = MySSHPipeHandler()
            client.service_loop()
        
    The handler overrides the four methods of *SSHPipeHandler*. *__init__()* defines an instance member *file*, *atstart()* opens file to which records would be written, *atexit()* closes the file, and *handle()* writes received record to file.
    
Example Explanation
-------------------

Lets say we run *sshremotehandlerusage.py* program on some server, ubuntud20
    
Classes and Methods
-------------------

    .. code:: python
    
        SSHPipe(host, command, name=None, user=None, term_message='TERM', config=None, encoding='utf8', callback=None, logger=None)
        
            SSHPipe establishes connection to remote *host* and runs *command*.  *host* can be ip address, hostname, or SSH host name.
            *name* associates and id to the pipe.  If *user* is provided, it will use for the SSH connectivity.  term_message, is 
    
SSHPipeClient
=============



	
example
-------

    .. code-block:: python
	
        import logging
	
        # create logger
        logger = logging.getLogger('simple_example')
        logger.setLevel(logging.DEBUG)
	
        # create console handler and set level to debug
        ch = logging.TimedRotatingFileHandler()
        ch.setLevel(logging.DEBUG)
	
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
        # add formatter to ch
        ch.setFormatter(formatter)
	
        # add ch to logger
        logger.addHandler(ch)
	
        # 'application' code
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')	

MpLogger and LevelBasedFormatter
================================

    Multiprocessor logger using QueueListener and QueueHandler
    It uses TimedSizedRotatingHandler as its logging handler

    It also uses acris provided LevelBasedFormatter which facilitate message formats
    based on record level.  LevelBasedFormatter inherent from logging.Formatter and
    can be used as such in customized logging handlers. 
	
example
-------

Within main process
~~~~~~~~~~~~~~~~~~~

    .. code-block:: python
	
        import time
        import random
        import logging
        from acris import MpLogger
        import os
        import multiprocessing as mp

        def subproc(limit=1, logger_info=None):
            logger=MpLogger.get_logger(logger_info, name="acrilog.subproc", )
    		for i in range(limit):
                sleep_time=3/random.randint(1,10)
                time.sleep(sleep_time)
                logger.info("proc [%s]: %s/%s - sleep %4.4ssec" % (os.getpid(), i, limit, sleep_time))

        level_formats={logging.DEBUG:"[ %(asctime)s ][ %(levelname)s ][ %(message)s ][ %(module)s.%(funcName)s(%(lineno)d) ]",
                        'default':   "[ %(asctime)s ][ %(levelname)s ][ %(message)s ]",
                        }
    
        mplogger=MpLogger(logging_level=logging.DEBUG, level_formats=level_formats, datefmt='%Y-%m-%d,%H:%M:%S.%f')
        logger=mplogger.start(name='main_process')

        logger.debug("starting sub processes")
        procs=list()
        for limit in [1, 1]:
            proc=mp.Process(target=subproc, args=(limit, mplogger.logger_info(),))
            procs.append(proc)
            proc.start()
    
        for proc in procs:
            if proc:
                proc.join()
    
        logger.debug("sub processes completed")

        mplogger.stop()	
        
    
Example output
--------------

    .. code-block:: python

        [ 2016-12-19,11:39:44.953189 ][ DEBUG ][ starting sub processes ][ mplogger.<module>(45) ]
        [ 2016-12-19,11:39:45.258794 ][ INFO ][ proc [932]: 0/1 - sleep  0.3sec ]
        [ 2016-12-19,11:39:45.707914 ][ INFO ][ proc [931]: 0/1 - sleep 0.75sec ]
        [ 2016-12-19,11:39:45.710487 ][ DEBUG ][ sub processes completed ][ mplogger.<module>(56) ]
        
Clarification of parameters
===========================

name
----

**name** identifies the base name for logger. Note the this parameter is available in both MpLogger init method and in its start method.

MpLogger init's **name** argument is used for consolidated logger when **consolidate** is set.  It is also used for private logger of the main process, if one not provided when calling *start()* method. 

proecess_key
------------

**process_key** defines one or more logger record field that would be part of the file name of the log.  In case it is used, logger will have a file per records' process key.  This will be in addition for a consolidated log, if **consolidate** is set. 

By default, MpLogger uses **name** as the process key.  If something else is provided, e.g., **processName**, it will be concatenated to **name** as postfix.  

file_prefix and file_suffix
---------------------------

Allows to distinguish among sets of logs of different runs by setting one (or both) of **file_prefix** and **file_suffix**.  Usually, the use of PID and granular datetime as prefix or suffix would create unique set of logs.

file_mode
---------

**file_mode** let program define how logs will be opened.  In default, logs are open in append mode.  Hense, history is collected and file a rolled overnight and by size. 

consolidate
----------- 

**consolidate**, when set, will create consolidated log from all processing logs.
If **consolidated** is set and *start()* is called without **name**, consolidation will be done into the main process.

kwargs
------

**kwargs** are named arguments that will passed to FileHandler.  This include:
    | file_mode='a', for RotatingFileHandler
    | maxBytes=0, for RotatingFileHandler
    | backupCount=0, for RotatingFileHandler and TimedRotatingFileHandler
    | encoding='ascii', for RotatingFileHandler and TimedRotatingFileHandler
    | delay=False, for TimedRotatingFileHandler
    | when='h', for TimedRotatingFileHandler
    | interval=1, TimedRotatingFileHandler
    | utc=False, TimedRotatingFileHandler
    | atTime=None, for TimedRotatingFileHandler
    
     
Change History
==============
    
        
Next Steps
==========

    1. Acknowledgment from handler that SSH pipe was established.
    #. SSHMultiPipe to allow management of multiple pipe from a single point.
    
    