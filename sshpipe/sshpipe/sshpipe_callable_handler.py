'''
Created on Oct 19, 2017

@author: arnon
'''
import sys
import struct
import pickle

class SSHPipeCallableHandler(object):
    def __init__(self, term_message='TERM',):
        self.term_message = term_message
        
    def service_loop(self):
        while True:
            try:
                msgsize_raw = sys.stdin.buffer.read(4)
                msgsize = struct.unpack(">L", msgsize_raw)
                workload = sys.stdin.buffer.read(msgsize[0])
                worker = pickle.loads(workload)
            except Exception as e:
                print(e, file=sys.stderr)
                print(self.term_action)
                exit(1)
        
            retcode = self.action(worker)
            if worker is not None:
                exit(retcode)
                
                
    def action(self, received):
        if not isinstance(received, str):
            received()
            return None
        elif received == self.term_message:
            # maybe worker prints to stdout
            return 0
        else:
            print("Bad object received: " + repr(received), file=sys.stderr)
            print(self.term_action)
            return 2

