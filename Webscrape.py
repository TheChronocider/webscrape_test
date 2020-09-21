#!/usr/bin/env python
# coding: utf-8

# In[191]:


# = = = = = = = = = = = = = 
# Created:       15:09:2020
# Last Updated:  21:09:2020
#
# Description:  Webscraper targeted at reading table format of fuel prices provided by AIP and preserve them in CSV format
#               Focused on using Requests library
# = = = = = = = = = = = = = 


# In[15]:


import datetime
import os
import csv

# Focusing on only using Requests
import requests


# In[16]:


# Input/s:  String, datetime
# Output/s: Boolean
#
# Description: Checks if file exists and then checks if current week has been recorded. Returns true is current week recorded, else false
#
def check_week(fFileName, fCurr_time):
    if os.path.exists(fFileName):
        with open(fFileName) as fd:
            # Read CSV
            reader = csv.reader(fd, delimiter=',')
            # Skip header line
            next(reader)
            for element in reader:
                # Compare and exit if we have completed this timestamp before
                if float(element[0]) == fCurr_time.timestamp():
                    # Return that we found that we have done this week
                    return True
    # Create CSV if not exists
    else:
        with open(fFileName, 'w', newline='') as fd:
            writer = csv.writer(fd)
            # Write Headers
            writer.writerow(["Timestamp (Unix)","Date (YYYY-MM-DD)","Location", "Weekly Average", "Weekly Change", "Variation", "Weekly Low", "Weekly High"])
    
    # Return false as timestamp doesn't already exists
    return False
    


# In[17]:


# Fuel data CSV
fileName = "fuel_data.csv"

# Target Cities
targets = ['canberra', 'sydney', 'batemans bay', 'cooma', 'goulburn', 'coffs harbour', 'wollongong', 'yass']


# In[18]:


# Get current date
curr_day = datetime.date.today()

# Calculate day subtraction to retrieve Sunday
idx = (curr_day.weekday() + 1) % 7

# Get datetime.date of last sunday
curr_week = curr_day - datetime.timedelta(idx)

# Convert to datetime object
curr_time = datetime.datetime(curr_week.year,curr_week.month,curr_week.day)


# In[21]:


# Gets skipped if we already have this weeks valeus
if (not check_week(fileName, curr_time)):
    ## The request made to get the raw infromation used for populating the table
    ## Found in the Networks tab of inspect element
    url = requests.get('https://aip.com.au/aip-api-request?api-path=public/api&call=nswUlpTable&fuelType=undefined')

    ## The URL is a JSON file, thus we will be just reading it as a JSON
    data = url.json()
        
    with open(fileName, 'a', newline='') as fd:
        writer = csv.writer(fd)
        ## Iterate through JSON objects
        for item in data:
            if data[item]['location'].lower() in targets:
                # Following syntax
                element = [
                    curr_time.timestamp(),
                    curr_time.strftime("%Y-%m-%d"),
                    data[item]['location'],
                    data[item]['weeklyAverage'],
                    data[item]['weeklyChange'],
                    data[item]['diff'],
                    data[item]['weeklyLow'],
                    data[item]['weeklyHigh']
                ]
                
                writer.writerow(element)

