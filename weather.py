#! /usr/bin/python
import os
import feedparser
import urllib
 
def weather_PART():
        weather_Info_List = []
        precis_List = []
        counter = 0
        weather_String = ""
        printer_Weather_String = ""
        #data = urllib.urlopen("ftp://ftp2.bom.gov.au/anon/gen/fwo/IDA00002.dat") #sydney's forcast
        #data = urllib.urlopen("ftp://ftp2.bom.gov.au/anon/gen/fwo/IDN10064.txt") #sydney's forcast
        data = urllib.urlopen("ftp://ftp2.bom.gov.au/anon/gen/fwo/IDN60059.txt") #sydney's forcast
        for list in data:
            if "PARRA"  in list:
                precis_List.append(list)
	    if "SYDNEY OL"in list:
		precis_List.append(list)

	for list in precis_List:
		print "Location: "+ list[0:14] +";"
		print "Hour    : "+ list[15:19] +";"
		print "Wind    : "+ list[20:27] +";"
		print "Temp    : "+ list[28:30] +";"
		print "Press   : "+ list[31:37] +";"
		print "Rain    : "+ list[38:43] +";"

	# 15,4,8,2,7,6

	#for weather in precis_List:
	#    Location, Hour, Wind, Temp, Press, Rain = weather.strip().split("\t")
	#    print "Loc: "+Location
       
        for info in precis_List:
	    print info +":" 
                #if counter ==0:
                #       counter = counter +1
                #weather_String  = "today: Time" + str( info )
                #       counter = counter +2
                #weather_String  = "today: Temp" + str( info )
                #else:
                #        weather_String = weather_String  + "tomorrow " + info
       
        return precis_List
        #return weather_String
 
 
if __name__=='__main__':
    	print "Running"
        printy = weather_PART();
        print printy
