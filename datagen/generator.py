import random
import decimal
import string
import datetime
import pandas as pd
import LatLon
from LatLon import *

#configurations used to generate the data
total_readings = 24
total_pop = 1
name_size = 7
timehr_range_start = 17
timehr_range_end = 21
timemm_range_start = 10
timemm_range_end = 60
#the four below restrict the generation of arbitrary location coordinates
#to a certain geographical area. It is a roughly rectangular block carved
#from a locality.
latstart = 18565000
latend = 18565500
lonstart = 73907100
lonend = 73910999

col_names = ['name','lat','lon','date','time','condition']
datasetdf = pd.DataFrame(columns = col_names)

for p in range(0, total_pop):
	name = ''.join(random.choice(string.ascii_uppercase) for _ in range(name_size))
	#print(name)
	condition = "healthy"
	con = random.randint(10,20)
	if(con>=15):
		condition = "sick"
	#print("Person: " + name + " is: " + condition)
	
	for p2 in range(0, total_readings):
		x = datetime.datetime.now()
		date = x.strftime("%d-%m-%Y")
		#print(date)
	
		timehr = random.randint(timehr_range_start, timehr_range_end)
		timemm = random.randint(timemm_range_start, timemm_range_end)
		time = str(timehr) + str(timemm)
		#print(time)

		lat=decimal.Decimal(random.randrange(latstart,latend))/1000000
		lon=decimal.Decimal(random.randrange(lonstart,lonend))/1000000
		currloc = LatLon(Latitude(lat),Longitude(lon))
		#print(currloc) #the current location of this person

		datasetdf = datasetdf.append({'name': name, 'lat':lat, 'lon':lon, 'date': date, 'time': time, 'condition': condition}, ignore_index=True)

print(datasetdf)
