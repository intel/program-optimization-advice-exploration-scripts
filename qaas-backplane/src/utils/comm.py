#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# MIT License

# Copyright (c) 2023 Intel-Sandbox
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
# HISTORY
# Created October 2022
# Contributors: David/Hafid

import argparse
import socket
import threading
import socketserver
import pickle

# Library for QAAS communication

class ServiceMessageReceiver(socketserver.TCPServer):
    def __init__(self, address, service_msg_recv_handler=lambda msg: None):
        super().__init__(address, ServiceMessageHandler)
        self.service_msg_recv_handler = service_msg_recv_handler
        # Also start the runner thread
        t = threading.Thread(target=self.serve_forever)
        t.setDaemon(True)
        t.start()


    def handler_on_recv(self, msg):
        self.service_msg_recv_handler(msg)

class ServiceMessageHandler(socketserver.BaseRequestHandler):
    DEFAULT_RECV_BUFFSIZEW = 1024
    DEBUG = False
    def handle(self):
        data = bytearray()
        # Due to our message sending protocal, we will send 1 message per connection, so read all until end
        while True:
            chunk = self.request.recv(self.DEFAULT_RECV_BUFFSIZEW)
            if not chunk: break
            data.extend(chunk)
        if data:
            msg = pickle.loads(data)
            if self.DEBUG: print(f"Recv message of type {type(msg)} from: {msg.hostname}")
            self.server.handler_on_recv(msg)

class ServiceMessageSender:
    def __init__(self, comm_port):
        self.comm_port = comm_port
        self.connect()

    def send(self, data):
        if self.msg_sender:
            self.msg_sender.sendall(data.encode())
        self.close()
        self.connect()

    def connect(self):
        self.msg_sender = socket.create_connection(("localhost", self.comm_port)) if self.comm_port else None

    def close(self):
        if self.msg_sender:
            self.msg_sender.close()

# class SshCommunicator:
#     def __init__(self, port):
#         self.port = port
#         #self.host = socket.gethostname()
#         self.host = "localhost"
#         self.my_socket = socket.socket()

#     def send(self, data):
#         self.conn.send(str(data).encode())

#     def recv(self):
#         data = self.conn.recv(1024).decode()
#         if not data:
#             return None
#         return str(data)
#     def close(self):
#         self.conn.close()

# class SshAccepted(SshCommunicator):
#     def __init__(self, listen_port, conn):
#         super().__init__(listen_port)
#         self.conn = conn
#     def do_stuff(self):
#         print('here')
#         data = self.recv()
#         print(f"listen recv {data}")
#         print(f"listen send 20")
#         self.send(20)


# class SshListener(SshCommunicator):
#     def __init__(self, listen_port):
#         super().__init__(listen_port)
#     def listen(self):
#         self.my_socket.bind((self.host, self.port))
#         self.my_socket.listen(20)
#         while True:
#             conn, address = self.my_socket.accept()
#             print('Create new thread')
#             accepted = SshAccepted(self.port, conn)
#             threading.Thread(target=accepted.do_stuff, args=()).start()
#         print (f'Connected from {str(address)}')

# class SshConnector(SshCommunicator):
#     def __init__(self, listen_port):
#         super().__init__(listen_port)
#     def connect(self):
#         self.my_socket.connect((self.host, self.port))
#         self.conn = self.my_socket


# def main():
#     parser = argparse.ArgumentParser(description="Build application")
#     parser.add_argument("--mode", choices=["connect", "listen"], required=True )
#     parser.add_argument("--port", type=int, required=True)
#     args = parser.parse_args()

#     if (args.mode == "connect"):
#         connect = SshConnector(args.port)
#         connect.connect()
#         print(f"connect send 10")
#         connect.send(10)
#         data = connect.recv()
#         print(f"connect recv {data}")
#         connect.close()
#     else:
#         listen = SshListener(args.port)
#         listen.listen()

# if __name__ == "__main__":
#     main()
