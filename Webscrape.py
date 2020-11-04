#!/usr/bin/env python
# coding: utf-8

# In[245]:


# = = = = = = = = = = = = = 
# Created:       15:09:2020
# Last Updated:  21:09:2020
#
# Description:  Webscraper targeted at reading table format of fuel prices provided by AIP and preserve them in CSV format
#               Focused on using Requests library
# = = = = = = = = = = = = = 


# In[246]:


import datetime
import os
import csv

# Focusing on only using Requests
import requests


# In[ ]:





# In[247]:


# Fuel data CSV
fileName = "fuel_data.csv"

# Target Cities
targets = ['canberra', 'sydney', 'batemans bay', 'cooma', 'goulburn', 'coffs harbour', 'wollongong', 'yass']

# Link to the JSON that contains week values
url = requests.get('https://aip.com.au/aip-api-request?api-path=public/api&call=nswUlpTable&fuelType=undefined')


# In[248]:


# Get current date
curr_day = datetime.date.today()

# Calculate day subtraction to retrieve Sunday
idx = (curr_day.weekday() +1) % 7

# Get datetime.date of last sunday
curr_week = curr_day - datetime.timedelta(idx)

# Convert to datetime object
curr_time = datetime.datetime(curr_week.year,curr_week.month,curr_week.day)


# In[249]:


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


# In[ ]:





# In[250]:


class Weekly_Price:
    #This object requires values to be made
    #"Timestamp (Unix)","Date (YYYY-MM-DD)","Location", "Weekly Average", "Weekly Change", "Variation", "Weekly Low", "Weekly High", "flagged (y/n)"
    def __init__(self, time, date, loc, avg, chng, var, low, high, flag):
        self.time = float(time)
        self.date = date
        self.loc = loc
        self.avg = float(avg)
   
        self.low = float(low)
        self.high = float(high)
        
        self.flag = flag
        
        # Below values have the potential to be "-"
        # Check if chng has a value else it's empty
        self.chng = float(chng) if isfloat(chng) else 0.0
        # Check if var has a value else it's empty
        self.var = float(var) if isfloat(var) else 0.0
       
    # Convert object to a useable array to be written to file
    def toArray(self):
        return [str(self.time),
               self.date,
               self.loc,
               str(self.avg),
               str(self.chng),
               str(self.var),
               str(self.low),
               str(self.high),
               self.flag]
    
    # Update values in object with new values if necessary
    def update_obj(self, avg, chng, var, low, high):
        self.avg = avg
        self.chng = chng
        self.var = var
        self.low = low
        self.high = high
        
    # Compare and see if the objects are of the same date
    def compare_locTime(self, obj):
        if (self.time == obj.time) & (self.loc == obj.loc):
            return True
        return False
    
    def compare_loc(self, obj):
        if (self.loc == obj.loc):
            return True
        return False
        
    # Compares values of object and returns array of which ones differ
    # True = same, False = different
    def compare_values(self, obj):
        return [
            True if self.avg == obj.avg else False,
            True if self.chng == obj.chng else False,
            True if self.var == obj.var else False,
            True if self.low == obj.low else False,
            True if self.high == obj.high else False,
        ]
        
    
    # Update flag if necessary
    def update_flag(self, flag):
        self.flag = flag
        


# In[251]:


def retrieve_data(fFileName):
    stored_data = []

    if os.path.exists(fFileName):
        with open(fFileName) as fd:
            # Read CSV
            reader = csv.reader(fd, delimiter=',')
            # Skip header line
            next(reader)
            for element in reader:

                # I'm sorry, it's ugly
                # This goes through 
                stored_data.append(Weekly_Price(element[0],
                                               element[1],
                                               element[2],
                                               element[3],
                                               element[4],
                                               element[5],
                                               element[6],
                                               element[7],
                                               (element[8] if len(element) == 9 else 'n')))
    return stored_data


# In[252]:


def latest_timestamp(fdata):
    timestamp = 0.0
    
    for val in fdata:
        if val.time > timestamp:
            timestamp = val.time
    return timestamp


# In[253]:


def get_latest(fdata):
    timestamp = latest_timestamp(fdata)
    
    latest = []
    
    for val in fdata:
        if val.time == timestamp:
            latest.append(val)
            
    return latest


# In[254]:


stored_data = retrieve_data(fileName)

# Objects are pass by reference
latest_objects = get_latest(stored_data)


# In[ ]:





# In[255]:


def convert_weekly(fdata, fcurr_time):
    # Object Data created from input
    obj_data = []
    
    for item in fdata:
        if fdata[item]['location'].lower() in targets:
            # time, date, loc, avg, chng, var, low, high, flag
            obj_data.append(Weekly_Price(
                fcurr_time.timestamp(),
                fcurr_time.strftime("%Y-%m-%d"),
                fdata[item]['location'],
                fdata[item]['weeklyAverage'],
                fdata[item]['weeklyChange'],
                fdata[item]['diff'],
                fdata[item]['weeklyLow'],
                fdata[item]['weeklyHigh'],
                'n'
            ))
            
    return obj_data


# In[256]:


# JSON of data retrieved from 
data = convert_weekly(url.json(), curr_time)


# In[257]:


# Flag whether we've updated values
updated = False

# Compare current week to most recent data
for val1 in data:
    for val2 in latest_objects:
        if val2.compare_locTime(val1):
            # If values from the same week aren't the same, update them with the more
            # Recent ones.
            if not all(val2.compare_values(val1)):
                val2.update_obj(val1.avg, val1.chng, val1.var, val1.low, val1.high)
                updated = True
        elif val1.compare_loc(val2):
            # If values from two different weeks are identical, flag the value
            if all(val2.compare_values(val1)):
                val2.update_flag('y')


# In[258]:


if latest_objects[0].time != data[0].time:
    print("here")
elif updated:
    with open(fileName, 'w', newline='') as fd:
        writer = csv.writer(fd)
        # Write Headers
        writer.writerow(["Timestamp (Unix)","Date (YYYY-MM-DD)","Location", "Weekly Average", "Weekly Change", "Variation", "Weekly Low", "Weekly High", "flagged (y/n/d)"])
        
        for value in stored_data:
            writer.writerow(value.toArray())


# In[259]:


# Gets skipped if we already have this weeks valeus
if (not check_week(fileName, curr_time)):
    ## The request made to get the raw infromation used for populating the table
    ## Found in the Networks tab of inspect element
    

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


# In[ ]:





# In[ ]:





# In[ ]:




