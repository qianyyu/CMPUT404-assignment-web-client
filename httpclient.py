#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust and 2020 Qian Yu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# Reference:
# PyMOTW-3,https://pymotw.com/3/urllib.parse/
# MDN, https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
        # self.response()
        return None
    # def __str__(self):
        # print(self.body)


class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            code = int(data.split('\r\n')[0].split(' ')[1])
            return code
        except Exception as e:
            print(data)
            print(e)

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        # print(buffer)
        return buffer.decode('utf-8')

    def parser(self,url):
        def display(parsed):
            print('scheme  :', parsed.scheme)
            print('netloc  :', parsed.netloc)
            print('path    :', parsed.path)
            print('query   :', parsed.query)
            print('fragment:', parsed.fragment)
            print('username:', parsed.username)
            print('password:', parsed.password)
            print('hostname:', parsed.hostname)
            print('port    :', parsed.port)
        try:
            parsed = urllib.parse.urlparse(url)
            if(parsed.hostname == None):
                raise Exception('Invalid URL')
            # display(parsed)
            path = '/' if parsed.path == ''   else parsed.path
            host = parsed.hostname
            port = 80  if parsed.port == None else parsed.port
            return path,host,port
        except Exception as e:
            print(e)

    def urlencoded(self,args):
        #content = ''
        #for key,value in args.items():
            #content += (key+'='+value+'&')
        #return content[:-1]
        return urllib.parse.urlencode(args)



    def GET(self, url, args=None):
        path,host,port = self.parser(url)
        self.connect(host,port)

        payload  = ['GET '+path+' HTTP/1.1\r\n',
                    'Host: '+host+'\r\n',
                    'Accept-Charset: UTF-8\r\n',
                    'Connection: close\r\n\r\n']
        payload = ''.join(payload)

        # print(payload)

        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        print(body)
        header = self.get_headers(data)
        self.close()
        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        path,host,port = self.parser(url)
        self.connect(host,port)
        content = '' if args == None else self.urlencoded(args)

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
        payload  = ['POST '+path+' HTTP/1.1\r\n',
                    'Host: '+host+'\r\n',
                    'Content-Type: application/x-www-form-urlencoded\r\n',
                    'Content-Length: '+str(len(content))+'\r\n'
                    'Accept-Charset: UTF-8\r\n',
                    'Connection: close\r\n\r\n',
                    content]
        

        payload = ''.join(payload)
        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        header = self.get_headers(data)
        print(body)
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
