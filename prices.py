import sqlite3
import time
import requests
import datetime
import calendar
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

conn = sqlite3.connect('Skytroo.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Prices')
cur.execute('''CREATE TABLE IF NOT EXISTS Prices (city TEXT, price TEXT, weekend INT)''')

########### CREATE THE FUNCTION tprice to call later ##############
# dates are split between: d = departure ,  r = return
def tprice(url,destination,dyear,dmonth,dday,ryear,rmonth,rday):

    # create chrome instance
    #driver = webdriver.Chrome(executable_path='/Users/CREATE/Desktop/sitedev2/chromedriver') # this was from windows
    driver = webdriver.Chrome() #for macOS
    #options = webdriver.ChromeOptions()
    #options.binary_location = '/usr/local/bin/chromedriver'  #this doesnt work MacOS automatically finds it as in line 27 above
    #options.add_argument('window-size=800x841')
    #options.add_argument('headless')
    #driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.maximize_window()

######################insert flying from airport ###################################
    driver.find_element_by_id("sb3_cc_sb3_flight_sb3_flight_iataFrom").clear()
    inputElement00 = driver.find_element_by_id("sb3_cc_sb3_flight_sb3_flight_iataFrom")
    inputElement00.send_keys('london')

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#as_ul > li")))  # check again the CSS selector might be wrong
    inputElement00.send_keys(Keys.ARROW_DOWN)
    inputElement00.send_keys(Keys.RETURN)
    time.sleep(1)

#######################insert flying to airport #########################
    inputElement1 = driver.find_element_by_id("sb3_cc_sb3_flight_sb3_flight_iataTo")
    inputElement1.send_keys(destination)  #put Friedrichshafen city as a destination to test N/A of flight results: Friedrichshafen

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#as_ul > li"))) # check again the CSS selector might be wrong
    inputElement1.send_keys(Keys.ARROW_DOWN)
    inputElement1.send_keys(Keys.RETURN)
    time.sleep(1)

##########################inserting the outbound date 20-12-2018 ###########################################################################
    driver.find_element_by_id("sb3_cc_sb3_flight_sb3_flight_outboundDate").click()
    time.sleep(1)
#inserting year
    inputElement0 = Select(driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/div/div/select[2]'))
    inputElement0.select_by_value(dyear)
#inserting month
    inputElement2 = Select(driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/div/div/select[1]'))
    inputElement2.select_by_value(dmonth)  # Jan is 0, Feb is 1 ... Dec is 11
#inserting day
    inputElement3 = driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/table/tbody')
    elements = [x for x in inputElement3.find_elements_by_tag_name("td")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"

    for element in elements:
        if element.text == dday:
            element.click()
            break
    time.sleep(1)

#############################inserting the return date 8-01-2019 ####################################################################################
    driver.find_element_by_id("sb3_cc_sb3_flight_sb3_flight_returnDate").click()
    time.sleep(1)
#year
    inputElement0 = Select(driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/div/div/select[2]'))
    inputElement0.select_by_value(ryear)
#month
    inputElement4 = Select(driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/div/div/select[1]'))
    inputElement4.select_by_value(rmonth)
#day
    inputElement5 = driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/table/tbody')
    elements = [x for x in inputElement5.find_elements_by_tag_name("td")]
    for element in elements:
        if element.text == rday:
            element.click()
            break
    time.sleep(1)
#submitting data to form
    driver.find_element_by_xpath('//*[@id="sb3_cc_sb3_flight_sb3_flight_search_button"]/div').click()
    #time.sleep(5)


#####    lets find the best price from the results page        ##################################################
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bf_rsitem:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1)")))
        prices = driver.find_element_by_css_selector('div.bf_rsitem:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1)')
        #for price in prices: (for elements_by (plural) instead of element)
        fare = prices.text
    except:
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#nbf_container > div > section > div.bf_rctr > section > div > h2")))
            no_flight = driver.find_element_by_css_selector('#nbf_container > div > section > div.bf_rctr > section > div > h2')
            fare = no_flight.text

        except:
            # sometimes it just loads for hours unable to find a fare ###
            fare = 'timeoutException'
    driver.quit()
    return fare


#CITIES FOR FIRST WEEKEND 1, select only top 10 with good score (weather conditions)
cur.execute('SELECT city_id, Score FROM Weather WHERE weekend_id = ? ORDER BY Score DESC Limit 10', (1,))
cities = cur.fetchall()
cities_1w=[]
for city in cities:
        cur.execute('SELECT City FROM Cities WHERE city_id = ?', (city[0],))
        cityname = cur.fetchone() # cityname is tuple
        cities_1w.append(cityname[0])
print(cities_1w) # this is a list of all cities so we can iterate in a loop to get prices later.

#CITIES FOR SECOND WEEKEND 2
cur.execute('SELECT city_id, Score FROM Weather WHERE weekend_id = ? ORDER BY Score DESC Limit 10', (2,))
cities = cur.fetchall()
cities_2w=[]
for city in cities:
        cur.execute('SELECT City FROM Cities WHERE city_id = ?', (city[0],))
        cityname = cur.fetchone() # cityname is tuple
        cities_2w.append(cityname[0])
print(cities_2w) # this is a list of all cities so we can iterate in a loop to get prices later.

############# HERE WE SPLIT  WEEKEND 1  TO COLLECT YEARS, MONTHS, DAYS #################################
cur.execute('SELECT Saturday, Sunday FROM Weekends WHERE weekend_id = ?', (1,))
weekend = cur.fetchone()
################### SATURDAY -> FRIDAY #################
saturday = weekend[0].split('T')
day = saturday[0].split('-')
year1 = day[0] #year of the weekend 1 saturday

month1 = str(int(day[1])-1) # month of the weekend 1 saturday (-1 because site starts Jan being month 0)
if month1 == '10' or '0': # month of the weekend 1 saturday
    pass
else:
    month1 = month1.strip('0')

date1 = str(int(day[2])-1) # date of the weekend 1 saturday ( -1 because we want Friday as flight day)
if date1=='0':
    date1='30'  #FEBRUARY 2019 FRIDAY is 1st so minus 1 it will be 30 but JANUARY has 31 days. Same for March. Fix this!
    month1 = str(int(day[1])-2) # - 2 months because our day shows we are in 31st of the last month
if date1 == '10' or '20' or '30':
    pass
else:
     date1 = date1.strip('0')
##################### SUNDAY #################
sunday = weekend[1].split('T')
day = sunday[0].split('-')
year2 = day[0] #year of the weekend 1 sunday

month2 = str(int(day[1])-1)
if month2 == '10' or '0': # month of the weekend 1 sunday
    pass
else:
    month2 = month2.strip('0')

date2 = str(int(day[2])) # date of the weekend 1 sunday
if date2 == '10' or '20' or '30':
    pass
else:
    date2 = date2.strip('0')

print(year1,month1,date1)
print(year2,month2,date2)
#################################################################################################
############# HERE WE SPLIT  WEEKEND 2  TO COLLECT YEARS, MONTHS, DAYS ######################
##########################################################################################
cur.execute('SELECT Saturday, Sunday FROM Weekends WHERE weekend_id = ?', (2,))
weekend = cur.fetchone()
###################### SATURDAY - > FRIDAY #############
saturday = weekend[0].split('T')
day = saturday[0].split('-')
year3 = day[0] #year of the weekend 2 saturday

month3 = str(int(day[1])-1) # month of the weekend 2 saturday (-1 because site starts Jan being month 0)
if month3 == '10' or '0': # month of the weekend 2 saturday
    pass
else:
    month3 = month3.strip('0')

date3 = str(int(day[2])-1) # date of the weekend 2 saturday
if date3=='0':
    date3='31'
    month3 = str(int(day[1])-2)  # - 2 months because our day shows we are in 31st of the last month
if date3 != '10' or '20' or '30':
    date3 = date3.strip('0')

################## SUNDAY ##################
sunday = weekend[1].split('T')
day = sunday[0].split('-')
year4 = day[0] #year of the weekend 2 sunday

month4 = str(int(day[1])-1) # month of the weekend 1 saturday (-1 because site starts Jan being month 0)
if month4 == '10' or '0': # month of the weekend 1 saturday
    pass
else:
    month4 = month4.strip('0')

date4 = str(int(day[2])) # date of the weekend 1 saturday ( -1 because we want Friday as flight day)
if date4=='0':
    date4='31'  #FEBRUARY 2019 FRIDAY is 1st so minus 1 it will be 30 but JANUARY has 31 days. Same for March. Fix this!
    month4 = str(int(day[1])-2) # - 2 months because our day shows we are in 31st of the last month
if date4 == '10' or '20' or '30':
    pass
else:
     date4 = date4.strip('0')

print(year3,month3,date3)
print(year4,month4,date4)
####################################################################################################

url = "https://"  #this is the url used to find prices

###################### 1st WEEK SEARCH FOR TICKETS ###################################
for city in cities_1w:
    print('retrieving: ', city)
    # BE CAREFUL TO ASSIGN THE FUNCTION TPRICE TO FARE VARIABLE OTHERWISE IT WONT RETURN THE FARE (thanks for your attention)
    price_1 = tprice(url, city, year1, month1, date1, year2, month2, date2)
    print(price_1)

    cur.execute('''INSERT INTO Prices (city, price, weekend) VALUES(?,?,?);''', (city, price_1,1))
    conn.commit()


for city in cities_2w:
    print('retrieving: ', city)
###################### 2nd WEEK SEARCH FOR TICKETS ###################################
    price_2 = tprice(url, city, year3, month3, date3, year4, month4, date4)
    print(price_2)

    cur.execute('''INSERT INTO Prices (city, price, weekend) VALUES(?,?,?);''', (city, price_2, 2))
    conn.commit()

cur.close()
