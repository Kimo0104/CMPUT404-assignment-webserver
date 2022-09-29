#  coding: utf-8 
import socketserver
import os.path
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).decode("utf-8").strip().split()
        request_type, route = self.data[0], self.data[1]
        if "../" in route: self.handle_invalid_route() 
        self.handle_invalid_request() if request_type != 'GET' else self.provide_response(route)

    def file_exists(self, route):
        return os.path.exists(route)

    #Displays the contents of the specified file
    def display_file(self, file, type = "html"):
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/{}\r\n\r\n".format(type)
        response += file
        self.request.sendall(bytearray(response,'utf-8'))

    #Called when a user makes a request thats not a GET
    def handle_invalid_request(self):
        response = "HTTP/1.1 405 Method Not Allowed \r\n\r\n"
        self.request.sendall(bytearray(response,'utf-8'))
    
    #Called makes a request with an invalid route
    def handle_invalid_route(self):
        response = "HTTP/1.1 404 Not Found \r\n\r\n"
        self.request.sendall(bytearray(response,'utf-8'))
    
    #Called when a user does not have a '/' in the end of their route
    def handle_redirect(self, route):
        response_route = route[5:]+'/'
        route += ("/" + "index.html")
        # Need to make sure that the file exists before we reroute
        if not self.file_exists(route):
            self.handle_invalid_route()
            return
        response = "HTTP/1.1 301 Moved Permanently \r\n Location:{}\r\n Content-Type: text/html\r\n\r\n".format(response_route)
        f = open(route, "r").read() 
        response += f
        self.request.sendall(bytearray(response,'utf-8'))

    #Calls when a user requests a directory
    def handle_directory_request(self, route):
        route += "index.html"
        if self.file_exists(route):
            f = open(route, "r").read() 
            self.display_file(f)
        else:
            self.handle_invalid_route()
    
    # Gets type of file
    def get_type(self,route):
        return route.split('.')[-1]
    
    #Calls when a user requests a file / mime-type
    def handle_file_request(self,route):
        type = self.get_type(route)
        if self.file_exists(route):
            f = open(route, "r").read() 
            self.display_file(f,type)
        else:
            self.handle_invalid_route()
    
    # Calls appropriate methods based on route
    def provide_response(self, route):
        route = './www' + route
        if len(route.split('.')) == 2:
            if route[-1] != '/': 
                self.handle_redirect(route)
            else: 
                self.handle_directory_request(route)
        elif len(route.split('.')) == 3: 
            self.handle_file_request(route)
        else:
            self.handle_invalid_route()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
