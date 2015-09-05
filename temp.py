#!/usr/bin/env python

import sqlite3
import os
import time
import glob

# get temerature
# returns None on error, or the temperature as a float
def get_temp(devicefile):

    try:
        fileobj = open(devicefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        return None

    # get the status from the end of line 1
    status = lines[0][-4:-1]

    # is the status is ok, get the temperature from line 2
    print lines
    if status=="YES":
        tempstr= lines[1][-6:-1]
        tempvalue=float(tempstr)/1000
        return tempvalue
    else:
        print "There was an error."
        return None

# main function
# This is where the program starts
def main():

    # enable kernel modules
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')

    # search for a device file that starts with 28
    devicelist = glob.glob('/sys/bus/w1/devices/28*')
    if devicelist=='':
        return None
    else:
        # append /w1slave to the device file
        for item in devicelist:
          item = item + '/w1_slave'
          temperature = get_temp(item)
          if temperature == None:
            temperature = get_temp(item)
          print item
          print temperature

    print devicelist


if __name__=="__main__":
    main()


