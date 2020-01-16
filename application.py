import os
import sqlite3
#import pprint
#import time
#import iata_codes
from flask import Flask, request, render_template

application = Flask(__name__)
@application.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
            
    elif request.method == 'POST':
        conn = sqlite3.connect('skytroo.db')
        cur = conn.cursor()
        weekendid= request.form['weekend']

#        homecity = request.form['City']
#        homecity = 'London'  ##### change with a request from webpage

######## FINDING THE COORDINATES OF THE HOMECITY (manually is London in this version)#############
######## for different cities i.e. berlin we will use different databases: cities and flights #########
        myData=[]

        cur.execute('''SELECT city_id, Temp_Sat, Cloud_Sat, Temp_Sun, Cloud_Sun, Duration, Score
        FROM Weather WHERE weekend_id = ? ORDER BY Score DESC LIMIT 10''', (weekendid,))
        row = cur.fetchall()
        for i in row:
            if i[5] < 240: #lets than 240/60 = 4 hours distance from departure city
                average_temp = (i[1]+i[3])/2
                average_clouds = (i[2]+i[4])/2
                flight = i[5]
                score = i[6]
                cur.execute('''SELECT * FROM Cities WHERE city_id = ?''', (i[0],))
                coords=cur.fetchone()
                if average_clouds<=0.3:
                    type = 'mostly sunny'
                elif 0.3>average_clouds<0.5:
                    type = 'sun and clouds'
                elif 0.5>average_clouds:
                    type = 'partial sunshine'
                cur.execute('''SELECT price FROM Prices WHERE city = ? AND weekend = ?''', (coords[1], weekendid))
                price=cur.fetchone()
                # a quick 'if' command to check and remove N/A flights from the results on the map#
                # careful there must be 20 number of prices to match 20 weather results. if there are less prices then the object returned is NoneType and the code blows
                #######  the if excludes higher prices from 300 quid and unavailable flights ##############
                if price[0]!= 'timeoutException' and price[0]!='Sorry, there are no results that match your search' and price[0]!='Sorry, there are no results that match your filters':
                    if float(price[0].strip('£'))<300:
                        zz = [coords[4], coords[3], coords[1], coords[2], round(average_temp,0), type, flight, price[0]]
                        myData.append(zz)
#        print(myData)
    return render_template('where.html', myData=myData)
#    return render_template('where.html')
#@application.route('/results')
#def results():
#    return render_template('where.html', myData=myData)

#@application.route('/contact/')
#def contact():
#    return render_template('contact.html')

#@application.route('/pricing/')
#def pricing():
#    return render_template('pricing.html')

if __name__ == '__main__':
    application.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 80))
    application.run(host=host, port=port)
