# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 16:27:06 2021

@author: Vincenzo
"""

import pymongo as pm
from datetime import timezone, datetime
import matplotlib.pyplot as plt
import numpy as np
import sklearn.cluster as clus

client = pm.MongoClient('bigdatadb.polito.it',
                        ssl=True,
                        authSource = 'carsharing',
                        tlsAllowInvalidCertificates=True)
db = client['carsharing']
db.authenticate('ictts', 'Ictts16!') 
Bookings_collection = db['PermanentBookings']
Parkings_collection = db['PermanentParkings']

dt = datetime(2017, 11, 1)
startUnixTime = dt.replace(tzinfo=timezone.utc).timestamp()
dt = datetime(2017, 12, 1)
endUnixTime = dt.replace(tzinfo=timezone.utc).timestamp()
CITY = "Milano"


Parkings_per_hours_date_no_filtered = list(Parkings_collection.aggregate([
{
    "$match":{
        "city": f"{CITY}",
        "init_time":{"$gte":startUnixTime,"$lte":endUnixTime},
        "final_time":{"$gte":startUnixTime,"$lte":endUnixTime},
    }
},
{
    "$project":{
        "hour": { "$hour": "$init_date" },
        "day": { "$dayOfMonth": "$init_date" },
        "duration":{"$divide" : [{"$subtract":["$final_time","$init_time"]},60]},
    }    
},
{
    "$group":{"_id": {"day":"$day","hour":"$hour"},"average_duration": {"$avg":"$duration"}, "totalParkings": {"$sum":1},"st_Dev_duration":{"$stdDevPop":"$duration"} }
}
]))                  

Parkings_per_hours_date_no_filtered.sort(key=lambda x:(x["_id"]["day"],x["_id"]["hour"]))

totalParks_no_filtered=[el["totalParkings"] for el in Parkings_per_hours_date_no_filtered]

Parkings_per_hours_date_filtered = list(Parkings_collection.aggregate([
{
    "$match":{
        "city": f"{CITY}",
        "init_time":{"$gte":startUnixTime,"$lte":endUnixTime},
        "final_time":{"$gte":startUnixTime,"$lte":endUnixTime},
    }
},
{
    "$project":{
        "hour": { "$hour": "$init_date" },
        "day": { "$dayOfMonth": "$init_date" },
        "duration":{"$divide" : [{"$subtract":["$final_time","$init_time"]},60]},
        "loc":1
    }    
},
{
    "$group":{"_id": {"day":"$day","hour":"$hour"},
    "list_durations": { "$push": "$duration" }, "list_positions": { "$push": "$loc" }}
}
]))                       

Parkings_per_hours_date_filtered.sort(key=lambda x:(x["_id"]["day"],x["_id"]["hour"]))
Parkings_per_hours_date_filtered.sort(key=lambda x:(x["_id"]["day"],x["_id"]["hour"]))

#WANT TO SHOW THE DAY ONLY ONCE AT THHE BEGINNING OF THE 23 HOURS
daysIndex1=[0]
currentDay1=[Parkings_per_hours_date_filtered[0]["_id"]["day"]]
for it in range(len(Parkings_per_hours_date_filtered)):
    el=Parkings_per_hours_date_filtered[it]
    if it!=0 and el["_id"]["day"]!=currentDay1[-1]:
        currentDay1.append(el["_id"]["day"])
        daysIndex1.append(it)
index=np.arange(len([el["_id"]["day"] for el in Parkings_per_hours_date_filtered]))

#STILL HAVE TO FILTER THE PARKINGS
cutIndicesSpace={}
cutIndicesTime={}
itKey=0
for obs in Parkings_per_hours_date_filtered:
    cutSpace=[]
    cutTime=[]
    coordinates=[el["coordinates"] for el in obs["list_positions"]]
    x_coord=[el[0] for el in coordinates]
    y_coord=[el[1] for el in coordinates]
    meanX=np.mean(x_coord)
    meanY=np.mean(y_coord)
    stdevX=np.std(x_coord)
    stdevY=np.std(y_coord)
    #KEEPING ONLY THE 99% of the data
    for it in range(len(coordinates)):
        el=coordinates[it]
        if (el[0]-meanX)/stdevX<-2.58 or (el[0]-meanX)/stdevX>2.58 or (el[1]-meanY)/stdevY<-2.58 or (el[1]-meanY)/stdevY>2.58:
            cutSpace.append(it)
    array=np.array(obs["list_durations"])
    km_clusters=clus.KMeans(n_clusters=2).fit(array.reshape(-1,1))
    lab2=km_clusters.labels_
    pos1=[it for it in range(len(lab2)) if lab2[it]==1]
    pos0=[it for it in range(len(lab2)) if lab2[it]==0]
    for it in range(len(lab2)):
        if len(pos1)>len(pos0) and lab2[it]==0:
            cutTime.append(it)
        elif len(pos0)>len(pos1) and lab2[it]==1:
            cutTime.append(it)
    cutIndicesSpace[itKey]=cutSpace
    cutIndicesTime[itKey]=cutTime
    itKey+=1

totalParks_filtered={}
for it in range(len(Parkings_per_hours_date_filtered)):
    tot_p=0
    for it2 in range(len(Parkings_per_hours_date_filtered[it]["list_durations"])):
        if it2 not in cutIndicesTime[it] and it2 not in cutIndicesSpace[it]:
            tot_p+=1
    totalParks_filtered[it]=tot_p

plt.figure()
plt.plot(index,totalParks_no_filtered,label="non filtered parks")
plt.plot(index, list(totalParks_filtered.values()), label='filtered parks')
plt.xticks(daysIndex1, currentDay1,rotation=60)
plt.grid()
plt.legend()
plt.xlabel('Day')
plt.ylabel('Occurrencies')
plt.title('Number of parkings  per hour and day in {}, November 2017'.format(CITY))
plt.show()

