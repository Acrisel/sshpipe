'''
Created on Jan 12, 2018

@author: arnon
'''

import socket
import struct
import pickle
from threading import Thread
from contextlib import closing
import os
from sshpipe import SSHTunnel

'''
This example utilizes SSHPipe to establish worker on remote host.
The agent then establishes another SSHPipe back into originator.
Through the back-pipe, agent sends back information to originator process.
To collect response via call-back, originator start a socket listener.
Socket information is sent via SSHPipe to agent which will use that as
part of the callback.
'''


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
        return port


def socket_listiner(port):
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host
    # print('HOST:', socket.gethostname())
    serversocket.bind(('127.0.0.1', port))
    # become a server socket
    serversocket.listen(5)

    # we only expect one client to 
    clients = 1
    while clients:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        ct = Thread(target=client_thread, args=(clientsocket, ), daemon=True)
        ct.start()
        clients -= 1


def read_message_length(socket):
    fmt = ">L"
    llen = struct.calcsize(fmt)
    raw = socket.recv(llen)
    slen = (0,)
    if raw:
        slen = struct.unpack(fmt, raw)
    return slen[0]


def read_message(socket, length):
    bytes_recd = 0
    raw = b''
    while bytes_recd < length:
        chunk = socket.recv(min(length - bytes_recd, length))
        if chunk == '':
            raise RuntimeError("socket connection broken")
        bytes_recd = bytes_recd + len(chunk)
        raw += chunk
    return raw


def client_thread(socket,):
    while 1:
        slen = read_message_length(socket)
        if slen == 0:
            # port is closed
            break
        raw = read_message(socket, slen)
        result = pickle.loads(raw)
        print('ARRIVED:', result)
        if result == 'TERM':
            break


def run():
    # Cannot use os.path.dirname(__file__) when OSX,
    # since it adds /private prefix
    agent_dir = os.path.dirname(__file__)
    agentpy = os.path.join(agent_dir, "ssh_callback_handler.py")
    # remote host IP address, or better yet, use host by name.
    host = 'ubuntud01_sequent'

    callback_host = 'mbp_sequent'
    callback_port = find_free_port()

    # start port listener
    listener = Thread(target=socket_listiner, args=(callback_port, ))
    listener.start()

    tunnel = SSHTunnel(host, [agentpy, '--host', callback_host, '--port', str(callback_port)])
    tunnel.start(wait=1)
    if tunnel.is_alive():

        print('Sending messages to remote agent.')
        tunnel.send("This is life.\n")
        tunnel.send("This is also life.\n")
        tunnel.send("This is yet another life.\n")
        tunnel.send("That is all, life.\n")
        tunnel.send("TERM")
        tunnel.close()
    print('Response:')
    for msg in tunnel.response():
        print(msg)


if __name__ == '__main__':
    # mp.set_start_method('spawn')
    run()
