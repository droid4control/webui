#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import os

import time
from sql2json import SQL2JSON
from config import Config

cfg = Config()	# read config to change CWD

PORT_NUMBER = cfg.get('webserver_port')

# global variables
last_timestamp = 0
last_json = ""

#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):

	#Handler for the GET requests
	def do_GET(self):
		global last_timestamp
		global last_json

		if self.path=="/":
			self.path="/webui.html"

		try:
			if self.path == "/pacui.json":
				self.send_response(200)
				self.send_header('Content-type', 'application/json')
				self.end_headers()
				ts = time.time()
				if ts > (last_timestamp + 0.9):
						last_timestamp = ts
						x = SQL2JSON()
						last_json = x.convert()
				self.wfile.write(last_json)
				return

			#Check the file extension required and
			#set the right mime type
			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True
			if self.path.endswith(".json"):
				mimetype='application/json'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + self.path)
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return


		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started http server on port ' , PORT_NUMBER

	#Wait forever for incoming http requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()

