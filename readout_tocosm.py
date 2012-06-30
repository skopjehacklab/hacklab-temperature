#!/usr/bin/env python2.7
"""
    Reads out the temp sensors from serial and posts them to https://cosm.com/feeds/64655/
    
    cron:
    */15 * * * * PYTHONUSERBASE=/home/kikadevices/temperature/env /home/kikadevices/temperature/temp_to_cosm.py >> /home/kikadevices/temperature/temp_to_cosm.log 2>&1

"""

import serial
import json
import requests
import time
import exceptions

sensors = {"28B535930013":"hardware_room","288AF85730019":"lounge_area","285BEF57300C7":"random_room"}
feed_id="64655"
cosm_api_key="COSM_API_KEY"

#set up the serial and ask for data
ser = serial.Serial("/dev/ttyUSB0")
ser.flushInput()
ser.write("g") 

#current time will be the same for all uploads
curr_time = time.strftime("%Y-%m-%dT%H:%M:%SZ%z", time.gmtime())

#read the data
while True:
    try:                     
        sensor_addr,curr_temp,readout_millis,curr_millis = ser.readline().split(",")
        
        # get sensor-room mapping
        datapoint_id=sensors[sensor_addr]

        if int(curr_millis)-int(readout_millis)>300000:
            raise exceptions.Warning("Haven't read new reading from %s for over 5 minutes.")
       
        url="http://api.cosm.com/v2/feeds/%s/datastreams/%s/datapoints" % (feed_id,datapoint_id)
        headers = {'X-ApiKey':cosm_api_key}
        payload={'datapoints': [{'at': curr_time, 'value': curr_temp}]}
               
        r = requests.post(url, data=json.dumps(payload), headers=headers)

        print sensor_addr, json.dumps(payload)
    except KeyError:
        print "Unknown sensor found %s" % sensor_addr
        continue

    except exceptions.Warning, e:
        print e
        continue

    except ValueError:
        #print "Done reading."
        break
