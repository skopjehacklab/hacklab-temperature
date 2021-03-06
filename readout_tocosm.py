#!/usr/bin/env python2.7
"""
    Reads out the temp sensors from serial and posts them to https://cosm.com/feeds/64655/
"""

import serial
import json
import requests
import time
import ConfigParser
import os
import sys

#get the feed_id and api_key from .gitignored file
pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
config_file = os.path.join(pwd,"readout_tocosm.cfg")

config = ConfigParser.ConfigParser()
config.read(config_file)
cosm = dict(config.items("cosm"))

sensors = {
   "28B535930013"  : "hardware_room",
   "288AF85730019" : "lounge_area",
   "285BEF57300C7" : "random_room",
   "282576B0300C7" : "outside"
}

#set up the serial and ask for data
ser = serial.Serial("/dev/ttyUSB0", timeout=10)

ser.flushInput()
time.sleep(10)
ser.write("g")

#current time will be the same for all uploads
curr_time = time.strftime("%Y-%m-%dT%H:%M:%SZ%z", time.gmtime())
print curr_time

#read the data
while True:
    line = ser.readline()
    if not line or line == '\r\n':
        break
    sensor_addr,curr_temp,readout_millis,curr_millis = line.split(",")

    # get sensor-room mapping
    datapoint_id = sensors.get(sensor_addr)
    if datapoint_id is None:
        print "Unknown sensor found %s" % sensor_addr
        continue

    if int(curr_millis)-int(readout_millis)>300000:
        print "Haven't read new reading from %s for over 5 minutes." % datapoint_id
        continue

    url="http://api.cosm.com/v2/feeds/%s/datastreams/%s/datapoints" % (cosm['feed_id'],datapoint_id)
    headers = {'X-ApiKey':cosm['api_key']}
    payload={'datapoints': [{'at': curr_time, 'value': curr_temp}]}

    print sensor_addr,json.dumps(payload)

    r = requests.post(url, data=json.dumps(payload), headers=headers)
