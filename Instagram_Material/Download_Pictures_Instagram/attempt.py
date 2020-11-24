import pymongo
from pymongo import MongoClient

cluster = pymongo.MongoClient("mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority")
db = cluster['Images_Data'] #(db)
collection =db['Instagram_Data']
collection.delete_many({"location_id":"1003920854"})
#results=[el[id] for el in list(collection.find({"location_id":"1003920854"}))]
print("DONE")