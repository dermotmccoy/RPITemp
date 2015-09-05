#!/usr/bin/env python

import sqlite3
import sys
import cgi
import cgitb
import time
import pytz
from datetime import datetime

# global variables
speriod=(15*60)-1
dbname='/var/www/tempdb/templogreg.db'


local_tz = pytz.timezone('Australia/Sydney') # use your local timezone name here
# NOTE: pytz.reference.LocalTimezone() would produce wrong result here

## You could use `tzlocal` module to get local timezone on Unix and Win32
# from tzlocal import get_localzone # $ pip install tzlocal

# # get local timezone    
# local_tz = get_localzone()

def utcstr_to_local(utcstr_dt):
    utc_dt = datetime.strptime(utcstr_dt,"%Y-%m-%d %H:%M:%S")
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary



# print the HTTP header
def printHTTPheader():
    print "Content-type: text/html\n\n"



# print the HTML head section
# arguments are the page title and the table for the chart
def printHTMLHead(title, table):
    print "<head>"
    print "    <title>"
    print title
    print "    </title>"
    
    print_graph_script(table)

    print "</head>"


# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_data(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    series = []
    sensors = curs.execute("SELECT DISTINCT ID from temps").fetchall()
    #sensors = curs.execute("SELECT DISTINCT ID from temps")
    #print sensors 
    #print " \n"
    for one in sensors:
      if interval == None:
        curs.execute("SELECT * FROM temps WHERE ID = '{0}'".format(one))
      elif interval == "All":
        curs.execute("SELECT * FROM temps WHERE ID = '{0}'".format(str(one[0])))
      else:
        curs.execute("SELECT * FROM temps WHERE timestamp>datetime('now','-{0} hours') AND ID = '{1}'".format( interval,str(one[0])))

   # print sensors
    #for one in sensors:
   #   if interval == None:
   #     curs.execute("SELECT * FROM temps")
   #   elif interval == "All":
   #     curs.execute("SELECT * FROM temps")
   #   else:
   #     curs.execute("SELECT * FROM temps WHERE timestamp>datetime('now','-{0} hours')".format( interval))

      rows=curs.fetchall()
      series.append(rows)
    conn.close()
    return series

# convert rows from database into a javascript table
def create_table(series):
    seriesLen=len(series) #get the number of series (Sensor count)
    #Todo: Add labels according to number of series. This needs to match the data!
    
    chart_table="[ ['Time' "  #put in the Time column label
    chart_lookup =[]
    for z in range (0,seriesLen):
      chart_table+=",'{0}'".format(str(series[z][0][0])) #add a column label for each sensor
      chart_lookup.append("['{0}','{1}']".format(z,str(series[z][0][0])))
      if z==seriesLen-1:#if it's the last column label, don't add the comma
        chart_table+="],"
      #else:
        #chart_table+="],"

    #print chart_lookup

    for x in range(0,len(series[0])): #For each row
      rowstr="['{0}'".format(format_table(utcstr_to_local(str(series[0][x][1]))))#get the timestamp for that row 

      for y in range (0,seriesLen): #for each series get value of row
        rowstr+=",{0}".format(str(series[y][x][2]))
 
      if x==len(series[0])-1:#if it's the last row, don't add the comma
        rowstr+="] ]\n"
      else:
        rowstr+="],\n"
      chart_table+=rowstr
        

#    for rows in series:
#      for row in rows[:-1]:
#        rowstr="['{1}',{2},{2}],\n".format(str(row[0]),format_table(utcstr_to_local(str(row[1]))),str(row[2]))
#        chart_table+=rowstr
#      row=rows[-1]
#      rowstr="['{1}',{2},{2}]\n".format(str(row[0]),format_table(utcstr_to_local(str(row[1]))),str(row[2]))
#      chart_table+=rowstr
#    chart_table+="]"


#    print chart_table
    return chart_table


# print the javascript to generate the chart
# pass the table generated from the database info
def print_graph_script(table):

    # google chart snippet
    chart_code="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable(%s);

        var options = { title: 'Temperature' };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>"""

    print chart_code % (table)




# print the div that contains the graph
def show_graph():
    print "<h2>Temperature Chart</h2>"
    print '<div id="chart_div" style="width: 1200px; height: 500px;"></div>'


def format_time(time):
    return time.strftime('%a %H:%M on %d/%m/%Y')

def format_table(time):
    return time.strftime('%a %H:%M')


# connect to the db and show some stats
# argument option is the number of hours
def show_stats(option):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if option is None:
        option = str(24)

    if option == "All":
      curs.execute("SELECT ID,timestamp,max(temp) FROM temps") 
      rowmax=curs.fetchone()

      curs.execute("SELECT ID,timestamp,min(temp) FROM temps")
      rowmin=curs.fetchone()

      curs.execute("SELECT avg(temp) FROM temps")
      rowavg=curs.fetchone()
    else:
      curs.execute("SELECT ID,timestamp,max(temp) FROM temps WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
      rowmax=curs.fetchone()

      curs.execute("SELECT ID,timestamp,min(temp) FROM temps WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
      rowmin=curs.fetchone()

      curs.execute("SELECT avg(temp) FROM temps WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
      rowavg=curs.fetchone()


    print "<hr>"


    print "<table>"
    print "<tr><td></td><td><strong>Temp</strong></td><td><strong>Time</strong></td></tr>"
    print "<tr><td>Min: </td><td>{0:.2f}C </td><td>{1}</td></tr>".format(rowmin[2],format_time(utcstr_to_local(rowmin[1])))
    print "<tr><td>Max: </td><td>{0:.2f}C </td><td>{1}</td></tr>".format(rowmax[2],format_time(utcstr_to_local(rowmax[1])))
    print "<tr><td>Average: </td><td>{0:.2f}C</td><td></td></tr>".format(rowavg[0])
    print "</table>"

    print "<hr>"

    print "<h2>In the last hour:</h2>"
    print "<table>"
    print "<tr><td><strong>Date/Time</strong></td><td><strong>Temperature</strong></td></tr>"

    #get the last hours data
    rows=curs.execute("SELECT * FROM temps WHERE timestamp>datetime('now','-1 hour') AND timestamp<=datetime('now') ORDER BY timestamp DESC")
    #rows=curs.execute("SELECT * FROM temps WHERE timestamp>datetime('now','-1 hour') AND timestamp<=datetime('now')")
    for row in rows:
        rowstr="<tr><td>{0}&emsp;</td><td>{1}&emsp;&emsp;</td><td>{2:.2f}C</td></tr>".format(row[0],(format_time(utcstr_to_local(str(row[1])))),row[2])
        print rowstr
    print "</table>"

    print "<hr>"

    conn.close()




def print_time_selector(option):

    print """<form action="/cgi-bin/webguiplus.py" method="POST">
        Show the temperature logs for  
        <select name="timeinterval">"""

    if option is not None:

        if option == "6":
            print "<option value=\"6\" selected=\"selected\">the last 6 hours</option>"
        else:
            print "<option value=\"6\">the last 6 hours</option>"

        if option == "12":
            print "<option value=\"12\" selected=\"selected\">the last 12 hours</option>"
        else:
            print "<option value=\"12\">the last 12 hours</option>"

        if option == "24":
            print "<option value=\"24\" selected=\"selected\">the last 24 hours</option>"
        else:
            print "<option value=\"24\">the last 24 hours</option>"

        if option == "72":
            print "<option value=\"72\" selected=\"selected\">the last 72 hours</option>"
        else:
            print "<option value=\"72\">the last 72 hours</option>"

        if option == "120":
            print "<option value=\"120\" selected=\"selected\">the last 120 hours</option>"
        else:
            print "<option value=\"120\">the last 120 hours</option>"

        if option == "All":
            print "<option value=\"All\" selected=\"selected\">All recorded data</option>"
        else:
            print "<option value=\"All\">All recorded data</option>"

    else:
        print """<option value="6">the last 6 hours</option>
            <option value="12">the last 12 hours</option>
            <option value="24" selected="selected">the last 24 hours</option>
            <option value="72" selected="selected">the last 72 hours</option>
            <option value="120" selected="selected">the last 120 hours</option>
            <option value="All" selected="selected">All recorded data</option>"""

    print """        </select>
        <input type="submit" value="Display">
    </form>"""


# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
    # check that the option string represents a number
    if option_str.isalnum():

        if option_str == "All":
          return option_str
        else:
          # check that the option is within a specific range
          if int(option_str) > 0 and int(option_str) <= 240:
            return option_str
          else:
            return None
    else: 
      return None


#return the option passed to the script
def get_option():
    form=cgi.FieldStorage()
    if "timeinterval" in form:
        option = form["timeinterval"].value
        return validate_input (option)
    else:
        return None




# main function
# This is where the program starts 
def main():

    cgitb.enable()

    # get options that may have been passed to this script
    option=get_option()

    if option is None:
        option = str(24)

    # get data from the database
    #records=get_data(option)
    series=get_data(option)

    # print the HTTP header
    printHTTPheader()

    if len(series) != 0:
        # convert the data into a table
        table=create_table(series)
    else:
        print "No data found"
        return

    # start printing the page
    print "<html>"
    # print the head section including the table
    # used by the javascript for the chart
    printHTMLHead("Raspberry Pi Temperature Logger", table)

    # print the page body
    print "<body>"
    print "<h1>Raspberry Pi Temperature Logger</h1>"
    print time.strftime('%I:%M`%p %Z on %b %d, %Y')+"<hr>"
    print_time_selector(option)
    show_graph()
    show_stats(option)
    print "</body>"
    print "</html>"

    sys.stdout.flush()

if __name__=="__main__":
    main()





