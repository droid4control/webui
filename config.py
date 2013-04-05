#!/usr/bin/python

import os

class Config:
	def __init__(self):
		self.cfg = {}
		self.cfg['sql_db_chan'] = 'modbus_channels'
		self.cfg['sql_db_setup'] = 'asetup'
		self.cfg['webserver_port'] = 8080
		try:
			import android
			os.chdir('/sdcard/sl4a/scripts/d4c')
		except:
			os.chdir('.')

	def get(self, key):
		return self.cfg[key] if self.cfg.has_key(key) else ""

if __name__ == '__main__':
	c = Config();
	print c.get('sql_db_chan')
	print c.get('foo')

