# Simple script to start a local http server
# and automatically open the home page in the 
# user's default browser.
# -- Contrail52


import sys
import threading
import webbrowser
import time

from http.server import HTTPServer, SimpleHTTPRequestHandler

class CustomHandler(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None):
        if code == 404:
            with open("404.html") as html_file:
                self.error_message_format = html_file.read()
            SimpleHTTPRequestHandler.send_error(self, code, message)
            
def start_server():
    httpd = HTTPServer(('localhost', 8080), CustomHandler)
    httpd.serve_forever()

server_thread = threading.Thread(target=start_server, args=())
server_thread.start()

url = 'http://localhost:8080/index.html'
webbrowser.open_new(url)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
