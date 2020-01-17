#THIS IS A CRAWLER FOR GETTING WEATHER FORECASTS FOR CITIES AROUND THE WORLD USING DARKSKY API AND STORING THEM TO WEATHER.DB
#ALSO, THIS PROGRAM USES THE ALGORITHMS FOR CITYRANK (ranking the cities from best to worst destinations to fly)
#COPYRIGHT IOANNIS GEORGAS, 27-03-2018.
import csv
import sqlite3
#import requests, json
import json
import requests
import pprint
import ssl
import http
import time
import datetime
import calendar
import re
import numpy as np

conn = sqlite3.connect('Skytroo.db')
cur = conn.cursor()

############## THE BELOW SCRIPT FETCHES THE NEXT TWO WEEKENDS EVERY WEDNESDAY & SUNDAY.########################
#IT SHOULD BE RUN ONLY SUNDAY AND WEDNESDAY. DO NOT RUN THIS DURING A WEEKEND DAY (i.e you run it saturday it will grab (sunday, saturday,sunday, saturday)
#check what day it is today
now =time.strftime('%Y-%m-%d')
#print(now)
#the current date is: 2018-03-30 date is a string
y = now.split('-')
#print(y) # ['2018', '04', '13']
# split into year y[0], month y[1] and day y[2]

#use the today to find the weekends in the next two months y[0] & y[1]+1
def Nextweekends(x,y):
    #today is an object we need to define it for comparison
    today = datetime.date.today()
    month=[]
    date= ()
    month_d = []
    #list of all calendar days as numbers in list
    z = calendar.monthcalendar(x,y)
    #print(z, '#########')
    # print example: [[0, 0, 0, 0, 0, 0, 1], [2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15], [16, 17, 18, 19, 20, 21, 22], [23, 24, 25, 26, 27, 28, 29], [30, 0, 0, 0, 0, 0, 0]]
    #we need to exclude all zeros in the list because they are not days of the month
    for i in z:
        #i[5] and i[6] are the weekend days on each of those lists
        if i[5]!=0:
            day = i[5]
            date=(y,day)
            month.append(date)
        if i[6]!=0:
            day = i[6]
            date=(y,day)
            month.append(date)
    #for i in month:
    #    d1 = datetime.date(x,y,i)
    #    delta1 = d1-today
    #    if delta1.days>0:
    #        month_d.append(delta1.days)
    #print(month_d, 'deltas')
    print(month, 'all future weekend days in', calendar.month_name[y], x)
    return (month)

month_1 = Nextweekends(int(y[0]), int(y[1]))
if int(y[1])+1 == 13: #if we are in January next year
    month_2 = Nextweekends(int(y[0])+1, 1)   # month 13 does not exist !! problem
else:
    month_2 = Nextweekends(int(y[0]), int(y[1])+1)

bothweekend = month_1+month_2 # all results
print(bothweekend, 'all weekends in these two month by (month,day)')

month1 = []
month2 = []
weekend=[] # final top 4 results (next two weekends)
for i in bothweekend:
    if str(i[0]).zfill(2) == y[1].zfill(2) and str(i[1]).zfill(2)>y[2].zfill(2):
         xx = (y[0]+'-'+str(int(y[1])).zfill(2)+'-'+str(i[1]).zfill(2)+'T12:00:00')
         month1.append(xx)
    elif str(i[0]).zfill(2) > y[1].zfill(2):
         yy = (y[0]+'-'+str(int(i[0])).zfill(2)+'-'+str(i[1]).zfill(2)+'T12:00:00')
         month2.append(yy)
allweekends = month1+month2
for i in allweekends[0:4]:
    weekend.append(i)
#pprint.pprint(weekend)
#example of a print: weekend = ('2018-03-31T12:00:00', '2018-04-01T12:00:00', '2018-04-07T12:00:00', '2018-04-08T12:00:00')
     #zfill adds zeros i.e. 2018-4-4 becomes 2018-04-04
#END OF SCRIPT

cur.execute('DROP TABLE IF EXISTS Weekends')
cur.execute('''
CREATE TABLE IF NOT EXISTS Weekends (weekend_id INT, Saturday TEXT, Sunday TEXT)''')
cur.execute('''
INSERT INTO Weekends VALUES (?,?,?);''', (1, weekend[0], weekend[1]))
cur.execute('''
INSERT INTO Weekends VALUES (?,?,?);''', (2, weekend[2], weekend[3]))
conn.commit()
############# FETCHING WEATHER DATE FOR THE NEXT TWO WEEKENDS ####################
api_key="XXXXXXXXXXXXXXXXXXXXXXXXX" #darksun API here

cur.execute('DROP TABLE IF EXISTS Weather')
cur.execute('''
CREATE TABLE IF NOT EXISTS Weather (city_id INT, Temp_Sat FLOAT, Cloud_Sat FLOAT,
                                    Temp_Sun FLOAT, Cloud_Sun FLOAT, weekend_id INT, Duration INT, Score FLOAT)''')

def Weatherfind(day):
    weather = []
    count = 1
    cur.execute('SELECT * FROM Cities')
    cities = cur.fetchall()
    #    for place in cities[:10]: (to do only the first 10 iterations)
    for place in cities:
            ctyid = place[0]
            city = place[1]
            country=place[2]
            lat = float(place[3])
            lon = float(place[4])
            #wday= days+'T12:00:00' #we add the T12:00:00 to select the noon time temperature from DarkSky

            #####################   Dark Sky API   ################################
            # Darksky documentation: https://darksky.net/dev/docs#forecast-request
            api_url="https://api.forecast.io/forecast/%s/%f,%f,%s?units=si&exclude=currently,minutely,hourly,flags,alerts"
            query_url = api_url % (api_key, lon, lat, day)
            r = requests.get(query_url)
            if r.status_code != 200:
                print ("Error:", r.status_code)

            print ('Retrieving', query_url)
            js = r.json()
            #try taking [daily] might explode if the coords are not in city
            temp = js['daily']['data'][0]['apparentTemperatureHigh']
            cloud = js['daily']['data'][0]['cloudCover']
            #humidity =js['daily']['data'][0]['humidity']
            #print(js['daily']['data'][0]['summary'])

            #changing the UNIX timestamp from the JSON reply to human readable format
            #print(datetime.datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))

            print('Retrieved', day, city, country, 'APIcall', count)
            count = count+1

            time.sleep(1)
            if count % 10 == 0 :
                print('Pausing for a bit...')
                time.sleep(5)

            cur.execute('SELECT Duration FROM Flights WHERE city_id=?',(ctyid,))
            duration = cur.fetchone()[0]

            results = [ctyid,temp,cloud,duration]

            weather.append(results)
    return weather
            #note: if you put cur.execute here for each result then it wont work :S

weather= Weatherfind(weekend[0])

cur.executemany('''INSERT INTO Weather(city_id, Temp_Sat, Cloud_Sat, weekend_id, Duration) VALUES(?,?,?,1,?);''', weather)
conn.commit()

weather = Weatherfind(weekend[1])
for i in weather:
    cur.execute('''UPDATE Weather SET Temp_Sun = ?, Cloud_Sun = ? WHERE city_id = ? AND weekend_id = 1''', (i[1], i[2], i[0]))
conn.commit()
weather = Weatherfind(weekend[2])
cur.executemany('''INSERT INTO Weather(city_id, Temp_Sat, Cloud_Sat, weekend_id, Duration) VALUES(?,?,?,2,?);''', weather)
conn.commit()
weather = Weatherfind(weekend[3])
for i in weather:
    cur.execute('''UPDATE Weather SET Temp_Sun = ?, Cloud_Sun = ? WHERE city_id = ? AND weekend_id = 2''', (i[1], i[2], i[0]))
conn.commit()

#########################  CITYRANK ALGORITHM BELOW ############################
#using nympy and polynomial interpolate to describe the temperature, cloud cover and duration.
def Cityrank_t(temperature):
    te = (1/10)*temperature
    x = np.array([-5.0, -4.0, -3.0, -2.0, 0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0, 6.0])
    y = np.array([0, 0, 0, 0, 0.25, 0.65, 0.80, 1, 0.80, 0.70, 0.30, 0.10, 0, 0])
    z = np.polyfit(x, y, 7)

    p = np.poly1d(z)
    return(p(te))

def Cityrank_c(cloudcover):
    cl = cloudcover
    x = np.array([0.0, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00])
    y = np.array([1.0, 0.9, 0.75, 0.25, 0.10, 0.05, 0.01, 0.0])
    z = np.polyfit(x, y, 3)

    p = np.poly1d(z)
    return(p(cl))

def Cityrank_d(duration):
    dur =  (1/100)*duration
    x = np.array([0.50, 0.60, 1.20, 1.80, 2.40, 3.00])
    y = np.array([1.0, 0.90 ,0.75, 0.20, 0.10, 0.0])
    z = np.polyfit(x, y, 3)

    p = np.poly1d(z)
    return(p(dur))

cur.execute('''SELECT Temp_Sat, Cloud_Sat, Temp_Sun, Cloud_Sun, Duration FROM Weather''')
rows = cur.fetchall()

for spec in rows:
    te1=Cityrank_t(spec[0])
    te2=Cityrank_t(spec[2])
    cl1=Cityrank_c(spec[1])
    cl2=Cityrank_c(spec[3])
    du1=Cityrank_d(spec[4])
    total_score = 0.4*(cl1+cl2) + 0.3*(te1+te2) + 0.3*du1
    #maximum total_score is 1.7 score while lowest is zero
    cur.execute('''UPDATE Weather SET Score = ? WHERE Temp_Sat = ? AND Temp_Sun= ?''', (round(total_score,4), spec[0],spec[2]))

conn.commit()
cur.close()
