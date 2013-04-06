#!/usr/bin/python

from config import Config
import sqlite3
import json

import time
import datetime

class SQL2JSON:
	def __init__(self):
		self.cfg = Config()
	def convert(self):
		dev = ''	# device type/name
		loc = ''	# location of the device
		typename=''
		devaddr = ''	#string, either modbus address if device on local rs485, or socket if device isreacheble via modbustcp
		chan_names=[]
		chan_types=[]
		indicator = ['ON', '?', 'OFF']	# texts for values 0 1 2
		mon_status = 0
		lan_status = 0
		usb_status = 2
		lanip = '1.2.3.4'

		mbstatus = {}	# data structure for JSON output

		# json output begins with general master device and system data
		mbstatus['modbusproxy_status'] = {}
		mbstatus['modbusproxy_status']['indicator'] = []
		mbstatus['modbusproxy_status']['indicator'].append({"name":"MON "+indicator[mon_status], "status":str(mon_status)})
		mbstatus['modbusproxy_status']['indicator'].append({"name":"LAN "+indicator[lan_status], "status":str(lan_status)})
		mbstatus['modbusproxy_status']['indicator'].append({"name":"USB "+indicator[usb_status], "status":str(usb_status)})
		mbstatus['modbusproxy_status']['info'] = []
		mbstatus['modbusproxy_status']['info'].append({"name":"WLAN IP address", "value":lanip})
		localtime = time.asctime( time.localtime(time.time()) )
		mbstatus['modbusproxy_status']['info'].append({"name":"TIME", "value":localtime})

		# device related data will follow
		mbstatus['device_status'] = []

		cfg = Config()

		conn1 = sqlite3.connect(cfg.get('sql_db_chan'), timeout=500)
		cursor1 = conn1.cursor()
		cursor1a = conn1.cursor()	# the second one

		# device related data will follow
		mbstatus['device_status'] = []

		#find out the mba numbers to represent the I/O extensions
		conn1.execute('BEGIN IMMEDIATE TRANSACTION')
		Cmd1 = "select aichannels.mba from aichannels left outer join dichannels on aichannels.mba=dichannels.mba \
			union select dichannels.mba from dichannels left outer join aichannels on aichannels.mba=dichannels.mba"
		cursor1.execute(Cmd1) # find modbus addresses for devices that have channels configured

		Cmd1 = "select name,type from chantypes order by num"
		cursor1a.execute(Cmd1) # get (globally used) channel types
		for rowa in cursor1a: # find devices with modbus addresses with at least one io channel configured
			if rowa[0] <> '': #
				chan_names.append(rowa[0])
				chan_types.append(rowa[1])

		for row in cursor1: # for devices with modbus addresses with at least one io channel configured
			if row[0] <> '': #
				mba = int(row[0]) # modbus address of the device

			Cmd1 = "select rtuaddr,tcpaddr,status,name,location from devices where num=" + str(mba)
			cursor1a.execute(Cmd1) # get device information and status
			devname = 'UNKNOWN' # default value if device not found from table devices
			location = 'UNDEFINED'
			devstatus = 3
			for rowb in cursor1a: #
				if rowb[1].split('.')[0] == '127': # device on local rs485
					devaddr = str(rowb[0]) # modbus address on local rs485
				else: # modbustcp
					devaddr = rowb[1]  # string
				devstatus = rowb[2]
				devname = rowb[3]
				location = rowb[4]

			# data structure for one device status for JSON
			devstatus = { "name":devname, "address":str(devaddr), "status":str(devstatus), "location":str(loc), "channel_data":[] }

			for line in range(len(chan_types)): # members 0..3, various channel types
				typenum = chan_types[line] # numeric!
				typename = chan_names[line]
				# data structure for one type of channel for JSON
				chstatus = {"typenum":typenum, "typename":typename, "data":[] }

				if typenum < 2: # DI, bit data included, one channels is one register bit
					Cmd1 = "select regadd,value,status,bit from dichannels where type+0=" + str(typenum) + " and mba+0=" + str(mba) + " group by regadd,bit+0"  # di channels
				else: # bit data irrelevant, one register per channel
					Cmd1 = "select regadd,value,status,outlo,outhi from aichannels where type+0=" + str(typenum) + " and mba+0=" + str(mba) + " group by regadd"  # ai channels

				try:
					cursor1a.execute(Cmd1) # find channel data for given given device (defined by mba) and channel type
				except:
					print 'problem with channel data select'

				for rowa in cursor1a: # generating cells for channels within current channel type
					# starting new channel
					addrstatus = {}
					addrstatus['address'] = int(rowa[0])
					addrstatus['value'] = int(rowa[1]) if rowa[1] <> '' else 0
					addrstatus['status'] = int(rowa[2]) if rowa[2] <> '' else 0

					if typenum > 1: # analogue (voltage or temp or...)
						addrstatus['vmin'] = int(rowa[3]) if rowa[3] <> '' else -50
						addrstatus['vmax'] = int(rowa[4]) if rowa[4] <> '' else 100
					else: # binary bitwise, types 0 and 1
						addrstatus['bit'] = int(rowa[3]) if rowa[3] <> '' else 0
					chstatus['data'].append(addrstatus)
				devstatus['channel_data'].append(chstatus)
			mbstatus['device_status'].append(devstatus)
		cursor1.close()
		cursor1a.close
		conn1.close()
		return json.dumps(mbstatus, indent=4)	# device channel data output

if __name__ == '__main__':
	x = SQL2JSON()
	print x.convert()

