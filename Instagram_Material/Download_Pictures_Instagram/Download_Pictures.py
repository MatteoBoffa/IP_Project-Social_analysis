import dropbox
import json
import time
import pymongo
from pymongo import MongoClient
import requests
from io import BytesIO
from datetime import datetime
from itertools import islice
import sys
import os
from stem.control import Controller
from stem import Signal
import numpy as np

def get_tor_session():
    # initialize a requests Session
    session = requests.Session()
    # setting the proxy of both http & https to the localhost:9050 
    # this requires a running Tor service in your machine and listening on port 9050 (by default)
    session.proxies = {"http": "socks5://localhost:9050", "https": "socks5://localhost:9050"}
    return session

def renew_connection(torPass):
    with Controller.from_port(port=9051) as c:
        c.authenticate(torPass)
        # send NEWNYM signal to establish a new clean connection through the Tor network
        c.signal(Signal.NEWNYM)

class Dropbox_Object():
	def __init__(self,data):
		self.dropbox_token=data["Token_Dropbox"]
		self.dropbox_path=data["dropbox_path"]
		self.local_path=data["local_path"]
		self.dbx=dropbox.Dropbox(self.dropbox_token)

	def uploadContent(self,buffer,identifier):
		self.dbx.files_upload(buffer.getvalue(), self.dropbox_path+identifier)

class PyMongo_Object():
	def __init__(self,data):
		self.cluster=pymongo.MongoClient(data["mongo_cluster"])
		self.db=self.cluster[data["cluster"]]
		self.collection=self.db[data["dataset"]]
	def addElement(self, dict_to_add):
		self.collection.insert_one(dict_to_add)

class Instagram_Object():
	def __init__(self,data,location_id,session,cursors):
		self.location_id=location_id
		self.linkInst=data["link_Instagram"]
		self.endCursor=cursors["current_cursor"]
		self.firstCursorInt=cursors["cursor_init"]
		self.cursor_need_update=False
		self.candidatesCursor={}
		since=data["since"].split(",")
		until=data["until"].split(",")
		self.since=datetime(int(since[0]),int(since[1]),int(since[2]))
		self.until=datetime(int(until[0]),int(until[1]),int(until[2]))
		self.data=""
		self.session=session
		self.torPass=data["torPass"]


	def getPosts(self):
		url = self.linkInst.format(self.location_id,self.endCursor)
		try:
			r = self.session.get(url)
			self.data=json.loads(r.text)
			newCursor=self.data['graphql']['location']['edge_location_to_media']['page_info']['end_cursor']
			if newCursor=="": #THE PAGE HAS THIS MISSING FIELD -> WILL HAVE TO SEARCH FOR ANOTHER CURSOR LATER
				self.cursor_need_update=True
			else:
				self.endCursor=newCursor
				self.updateJsonCursors() #UPDATE THE JSON FILE -> NEXT TIME WE'LL START FROM UPDATED SOL
			return self.data
		except Exception as e:
			#In case of exception, renew connection
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print("3) An exception was launched! {},{},{}".format(e,exc_type,exc_tb.tb_lineno))
			renew_connection(self.torPass)
			self.session=get_tor_session()
			r=self.session.get(url)
			return ""

	def updateJsonCursors(self):
		with open("../Results/joined_results.json","r") as f:
			cursors=json.load(f)	
		cursors[self.location_id]["current_cursor"]	= self.endCursor
		with open("../Results/joined_results.json","w") as f:
			json.dump(cursors,f)			

class Downloader():
	def __init__(self,location_id,session,data,pymongoObject,dropboxObject,cursors):
		since=data["since"].split(",")
		until=data["until"].split(",")
		self.since=datetime(int(since[0]),int(since[1]),int(since[2]))
		self.until=datetime(int(until[0]),int(until[1]),int(until[2]))
		self.dropboxObject=dropboxObject
		self.instagramObject=Instagram_Object(data,location_id,session,cursors)
		self.pymongoObject=pymongoObject
		self.counter=0
		self.idAlreadyPresent=[]

	def upload_info(self,field_to_search,data):
		lenEdges=len(data['graphql']['location'][field_to_search]['edges'])
		numberOfPosts=int(data['graphql']['location'][field_to_search]["count"])
		if numberOfPosts>20000:
			step=24
		elif numberOfPosts>10000 and numberOfPosts<=20000:
			step=12
		elif numberOfPosts<=10000 and numberOfPosts>5000:
			step=6
		elif numberOfPosts<=5000 and numberOfPosts>1000:
			step=3
		else:
			step=1
		for e in data['graphql']['location'][field_to_search]['edges'][0:lenEdges:step]:
			node=e["node"]
			isVideo=node["is_video"]
			date_taken=datetime.fromtimestamp(node["taken_at_timestamp"])
			id=str(node["id"])
			alreadyPresent=(id in self.idAlreadyPresent)
			#FIRST I CHECK IF I HAVE TO UPLOAD THE PICTURE
			if date_taken>self.since and date_taken<self.until and isVideo==False \
			and alreadyPresent==False:
				try:
					name_place=data['graphql']['location']["name"]
					lat=data['graphql']['location']["lat"]
					lng=data['graphql']['location']["lng"]
					description=data['graphql']['location']["blurb"]
					url=node["display_url"]
					owner_id=node["owner"]["id"]
					if len(e['node']["edge_media_to_caption"]["edges"])!=0:
						title=e['node']["edge_media_to_caption"]["edges"][0]["node"]["text"]
					else:
						title=""
					r = self.instagramObject.session.get(url)
					with BytesIO() as buffer:
						buffer.write(r.content)
						self.dropboxObject.uploadContent(buffer,id+".jpeg")
					dictToSave={
					"id":id,
					"owner":owner_id,
					"title":title,
					"date_taken":date_taken,
					"url":url,
					"name_place":name_place,
					"lat":lat,
					"lng":lng,
					"location_descr":description,
					"location_id":self.instagramObject.location_id
					}
					self.pymongoObject.addElement(dictToSave)
					print("\tOne more download")
					self.counter+=1	
				
				except Exception as e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					print("4) An exception was launched! {},{}".format(exc_type,exc_tb.tb_lineno))
					renew_connection(self.instagramObject.torPass)
					self.instagramObject.session=get_tor_session()
					r=self.instagramObject.session.get(url)
				
			#THEN I CHECK IF THE CURSOR FOR THAT PAGE WAS EMPTY:
			if self.instagramObject.cursor_need_update==True:
				#print("\t\t New element we might consider as a candidate is: {}".format(str(id)))
				self.instagramObject.candidatesCursor[date_taken]=str(id)

		if self.instagramObject.cursor_need_update==True:
			if self.instagramObject.candidatesCursor!={}: #IF THE CURSOR HAD TO BE UPDATED AND THE PAGE WAS NOT EMPTY
				self.instagramObject.cursor_need_update=False
				keys=list(self.instagramObject.candidatesCursor)
				keys.sort(reverse=True)
				for key in keys:
					if self.instagramObject.candidatesCursor[key]<self.instagramObject.endCursor:
						#print("Updating old cursor ({}) with a new one ({})".format(self.instagramObject.endCursor,self.instagramObject.candidatesCursor[key]))
						self.instagramObject.endCursor=self.instagramObject.candidatesCursor[key]
						self.instagramObject.updateJsonCursors()
						self.instagramObject.candidatesCursor={}
						break
			else:#IF THE CURSOR HAD TO BE UPDATED BUT THE PAGE WAS EMPTY
				pass #DO NOTHING; THE CYCLE WILL BE STOPPED AFTER THREE ITERATIONS

		try:
			toReturn=datetime.fromtimestamp(data['graphql']['location'][field_to_search]['edges'][-1]["node"]["taken_at_timestamp"])
		except: 
			print("\tThe page was empty!")
			toReturn=0

		return toReturn
		

	def start(self,key):
		idAlreadyPresent=list(self.pymongoObject.collection.find({"location_id":"{}".format(str(key))}))
		self.idAlreadyPresent=[el["id"] for el in idAlreadyPresent]
		self.counter=0
		data=self.instagramObject.getPosts()
		if data!="": #"" IS THE VALUE I'VE RETURNED IN CASE OF ERRORS
			if len(data['graphql']['location']['edge_location_to_media']['edges'])!=0:
				#IF THE edge_location_to_media FIELD IS NOT EMPTY -> DEFAULT BEHAVIOUR
				last_date=self.upload_info("edge_location_to_media",data)
			else:
				#TRY TO FIND SOMETHING ELSE TO PROCEDE
				last_date=self.upload_info('edge_location_to_top_posts',data)
			return self.counter,last_date, self.instagramObject.endCursor
		else:
			return 0,0,0


if __name__ == '__main__':
	
	LOCATION_AND_CURSORS="../Results/joined_results.json"
	photo_per_location=400 #Limit the number of photo per site
	with open(LOCATION_AND_CURSORS) as json_file: #Uploading the location I want to study
		locations_and_cursors = json.load(json_file)
	pathConfig="./catalog.json"
	with open(pathConfig) as json_file: #Upload the settings-information from the config
		data = json.load(json_file)
	#NEED TO CREATE THEM JUST ONCE -> OTHERWISE EXCEPTION
	pymongoObject=PyMongo_Object(data)
	dropboxObject=Dropbox_Object(data)
	s=get_tor_session()
	startFrom=data["start_from"] #Used to eventually limit the number of JSON considered
	endWith=data["end_with"]
	lenFile=len(list(locations_and_cursors.keys())[startFrom:endWith])
	for key in list(locations_and_cursors.keys())[startFrom:endWith]:
		#FIRST PART OF THE LOOP -> UNDERSTAND WHERE TO START SEARCHING FOR THAT LOCATION
		location_id=key
		cursors=locations_and_cursors[key]
		indexKey=list(locations_and_cursors.keys())[startFrom:endWith].index(key)
		data["start_from"]=indexKey+startFrom
		print("For {} ({} missing) we have: ".format(locations_and_cursors[key]["name"],lenFile-indexKey-1))
		#INSTANTIATE THE OBJECT DOWNLOADER -> 1 DOWNLOADER PER LOCATION
		d=Downloader(location_id,s,data,pymongoObject,dropboxObject,cursors)
		#SERIES OF PARAMETERS TO HANDLE CYCLE BELOW
		no_downloads=0 #counter for iterations without downloading
		stopped=0 #number of exceptions allowed
		counter=0 #pictures downloaded per location
		dateOld=""
		oldCounter=counter
		while counter<photo_per_location and stopped<3:
			#print("\tStarting iteration: {}".format(it))
			try:				
				increment,lastDate,endCursor=d.start(key)
				counter+=increment
				print("\tDown. {} images for location {}; Last date: {}; Last cursos: {}"\
					.format(counter,locations_and_cursors[key]["name"],lastDate,endCursor))
				if lastDate==dateOld or lastDate<datetime(2016,12,31) or no_downloads>4:
					stopped+=1
				dateOld=lastDate
				if oldCounter==counter:
					no_downloads+=1
				else:
					no_downloads=0
				oldCounter=counter
				time.sleep(2)
			except KeyboardInterrupt:
				print("\n\tYou interrupted the program at iteration {}".format(data["start_from"]))
				with open(pathConfig,"w") as json_file: #Upload the settings-information from the config
					json.dump(data,json_file,indent=4,sort_keys=True,default="ftr")
				exit()
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				print("2) An exception was launched! {},{}".format(exc_type,exc_tb.tb_lineno))
				break				
		print("Ended location!\n")
