#!/usr/bin/env python
# coding: utf-8

# In[191]:


# = = = = = = = = = = = = = 
# Created:       15:09:2020
# Last Updated:  18:09:2020
#
# Description:  Webscraper targeted at reading table format of fuel prices provided by AIP and preserve them in CSV format
# = = = = = = = = = = = = = 


# In[192]:


from selenium import webdriver
import re # Importing regex
import datetime
import os
import csv


# In[199]:


# Input/s:  String
# Output/s: [String]
#
# Description: Splits string into sentences and seperated numeric values
#
def split_string(fstring):
    # Return is string is empty
    if len(fstring) <= 0:
        return []
    
    # Check if current char is not a white space
    if fstring[:1] != ' ':
        # Current value found, get word remainder
        value = split_word(fstring)
        
        # Return array of found value and remainder
        return [value[0]] + split_string(value[1])
        
    else:
        # No current value, continue to next
        return split_string(fstring[1:])

# Input/s:  String
# Output/s: String, String
#
# Description: Splits string into sentence ending at numeric value
#
def split_word(fstring):
    # Check if we've got chars left
    if len(fstring) <= 0:
        return '', ''
    
    # Check if we haven't reached the end of the word
    if (fstring[:1] != ' ') | ((len(fstring) >= 2) & (fstring[1:2].isalpha())):
        value = split_word(fstring[1:])
        return fstring[:1] + value[0] , value[1]
    
    else:
        return '', fstring
    
    return '', ''

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
    


# In[200]:


# Web Driver location
path = r'.\Chromedriver'

# Fuel data CSV
fileName = "fuel_data.csv"

# Fuel data location
url = 'https://aip.com.au/pricing/new-south-walesact-retail-petrol-prices'

# Target Cities
targets = ['Canberra', 'Sydney', 'Batemans Bay', 'Cooma', 'Goulburn', 'Coffs Harbour', 'Wollongong', 'Yass']


# In[201]:


# Get current date
curr_day = datetime.date.today()

# Calculate day subtraction to retrieve Sunday
idx = (curr_day.weekday() + 1) % 7

# Get datetime.date of last sunday
curr_week = curr_day - datetime.timedelta(idx)

# Convert to datetime object
curr_time = datetime.datetime(curr_week.year,curr_week.month,curr_week.day)


# In[205]:


if (not check_week(fileName, curr_time)):
    # Driver opening
    driver = webdriver.Chrome(executable_path = path)

    #Specify wait 10 seconds
    driver.implicitly_wait(15)
    
    # Executing fuel place location
    driver.get(url)
    

    # Get values between 'tr' elements and split them as desired
    elements = [split_string(element.text) for element in driver.find_elements_by_css_selector('tr')]

    # Get desired fuel data and add timestamp and current date
    current_prices = []
    for element in elements:
        if element[0] in targets:
            current_prices = current_prices + [[curr_time.timestamp()] + [curr_time.strftime("%Y-%m-%d")] + element]
    
    # Write fuel prices to file
    with open(fileName, 'a', newline='') as fd:
        writer = csv.writer(fd)
        for element in current_prices:
            writer.writerow(element)
    
    driver.close()


# In[ ]:




