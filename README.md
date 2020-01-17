# Skytroo
Skytroo is an app that helps travellers find sunny weekend destinations across Europe.

The idea for this app dawned to me while living in UK where sun sometimes is a luxury. I wanted to quickly calculate 
where is the closest and cheapest destination to fly to and spend a sunny weekend. The app has three steps:

1) The landing page where the user gives the fly from destination i.e. London, the weekend that he/she is available
and the activity that he/she wants to do, for example explore a city, romantic destination, do sports etc. 
(photo: Skytroo Landing page) 

2) The app uses APIs to collect temperature, cloud cover and plane ticket prices for 186 popular destinations across Europe mainly cities and towns. Then based on the data the app ranks these cities to find the top 5 destinations and pin them down on a google map. (photo: Skytroo Results page)

3) The user inspects the destinations by clicking the pins to learn more details and if he/she feels happy about it can click the link to go to skyscanner and buy the ticket. The idea is that every purchase at skyscanner will offer a small commissioning back to Skytroo (business model). (photo: Skytroo Results page - Details)

Other files:

Application.py - the code that runs the localhost server and web pages. I did not include the front-end html/css/JS in this repo.

wload. py - this is the one of the two programs that finds fresh weather & cloud cover from Darksun API and rank all 184 destinations. Because weather conditions change this program needs to run weekly. A good forecast can only see two weeks ahead.

prices.py - this is a simple scrapper used to find ticket prices. Its bespoke so I suggest you write your own code. I used this program weekly to find new prices as prices flactuate.

Skytroo.db - this is the database that contains all the data from APIs. Some of the tables in the database were created by using crawlers which I can share if requested.


Play around with the code and please reach out if you are excited!

Thanks!

Yannis

APIs used and special mentions:
- Dark Sun for temperature, cloud cover data
- Google maps API to present the results
- Website templates by 2016 Free HTML5 - Modifications by Yannis Georgas
- Special thanks to Skyscanner for giving me Affiliate status for the test period.
- Commission Junction profile created to receive commissioning from Skyscanner.
- Used Amazon Web Services Elastic Beanstalk to host www.Skytroo.com website (now no longer active)
- Landing page Photo by Yannis Georgas copyright. It is the lovely island of Isla Mujeres, Quintana Roo, Mexico
