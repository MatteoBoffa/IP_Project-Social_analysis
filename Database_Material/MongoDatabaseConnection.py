# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:32:15 2020

@author: Vincenzo
"""

import pymongo
from pymongo import MongoClient





####################################### CONNECT to the Database  ############################################

#the MongoClient accepts the password of  the user that can access the db (Ict), and the  name of the db (Database_try)


cluster = pymongo.MongoClient("mongodb+srv://vincenzo:Ict@clusterc.qvgo1.mongodb.net/Database_try?retryWrites=true&w=majority")

#in case of error need to install in the command line of spyder : 'pip install pymongo[srv]'
db = cluster['Database_try'] #(db)
collection =db['Sample_Data'] # (collection into the db - one db can have multiple connections, and a collection is made of posts/documents





####################################### INSERT lines into the Database  ############################################

post = {'user_id' : '00006', 'geotags' : 'Torino', 'timestamp' : '', 'tags' : 'Porta Susa', 'cluster' : 6 }
collection.insert_one(post)
# if we have more post (more lines to add) -----> collection.insert_many(arrayOfPosts)


###################################### GET a result from the Database  ###########################################

results = collection.find({'tags' : 'Piazza Vittorio'})  #results return the Cursor , that can be made of more posts

#for r in results:    to print the each post
 #   print(r)
 
#if we want to retrieve one single result -> collection.find_one({'...' : '...'})
 
 
 ###################################### DELETE a post from the Database  ###########################################
 
 #collection.delete_one({'...' : '...'})
result = collection.delete_one({'user_id' : '00005'})
#to delete more posts -> collection.delete_many({'...' : '...'})


 ###################################### UPDATE  the value of a single post of the Database  ###########################################
 
results = collection.update_one({'tags' : 'Piazza Vittorio'} , {'$set' : {'tags' : 'Crocetta'}})
#is possible her also to add a new field for one or more posts, simply specifyingthe new field after the $set
#to update more posts -> collection.update_many(...)



 ###################################### COUNT  the posts/documents inside a collection ###########################################
 
#count = collection.count_documents({})
#print(count)