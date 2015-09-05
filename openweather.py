#! /usr/bin/python
import os
import urllib
import json
 
def weather_PART():
    weather_Info_List = []
    precis_List = []
    counter = 0
    weather_String = ""
    printer_Weather_String = ""
    url = urllib.urlopen('http://api.openweathermap.org/data/2.5/weather?q=toongabbie&units=metric') #toongabbie's forcast
    data = url.read().decode("iso-8859-1")
    detail = json.loads(data)

    print data
    print detail




 
if __name__=='__main__':
    print "Running"
    weather_PART();

