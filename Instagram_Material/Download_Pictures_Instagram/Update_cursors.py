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
    session = requests.Session()
    session.proxies = {"http": "socks5://localhost:9050", "https": "socks5://localhost:9050"}
    return session

def renew_connection(torPass):
    with Controller.from_port(port=9051) as c:
        c.authenticate(torPass)
        c.signal(Signal.NEWNYM)

class Instagram_Object():
	def __init__(self,data,location_id,until,since,session,cursor):
		self.location_id=location_id
		self.linkInst=data["link_Instagram"]
		self.cursorFile=data["path_cursor"]
		with open(self.cursorFile,"r+") as f:
			self.cursors=json.load(f)
		if location_id in self.cursors.keys():
			self.endCursor=self.cursors[location_id]["current_cursor"]
			self.firstCursorInt=self.cursors[location_id]["cursor_int"]
		else:
			self.endCursor=cursor
			self.firstCursorInt=0
			self.cursors[location_id]={
				"current_cursor":self.endCursor,
				"cursor_int":self.firstCursorInt
			}
		self.cursor_need_update=False
		self.candidatesCursor={}
		self.since=since
		self.until=until
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
				self.updateJsonCursors("","") #UPDATE THE JSON FILE -> NEXT TIME WE'LL START FROM UPDATED SOL
			return self.data
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print("3) An exception was launched! {},{},{}".format(e,exc_type,exc_tb.tb_lineno))
			renew_connection(self.torPass)
			self.session=get_tor_session()
			r=self.session.get(url)
			return ""

	def updateJsonCursors(self,whenUpdated,node_id):
		#DEPENDING ON WHERE I LAUNCHED THIS METHOD I'LL HAVE DIFFERENT BEHAVIOURS TO FIND A NEW INIT_CURSOR
		if whenUpdated=="": #IF WE ARRIVED HERE THROUGH THE NORMAL PROCEDURE
			edges=self.data['graphql']['location']['edge_location_to_media']['edges']
			edges.sort(key=lambda e:e["node"]["taken_at_timestamp"])
			changed=False
			for edge in edges:
				date_taken=datetime.fromtimestamp(edge["node"]["taken_at_timestamp"])
				node_id=edge["node"]["id"]
				if date_taken<self.until and date_taken>self.since and int(node_id)>int(self.cursors[self.location_id]["cursor_int"]):
					changed=True
					self.cursors[self.location_id]["cursor_int"]=node_id
		else: #IF WE ARRIVED HERE WHILE SEARCHING FOR A NEW END_CURSOR
			date_taken=whenUpdated
			if date_taken<self.until and date_taken>self.since and int(node_id)>int(self.cursors[self.location_id]["cursor_int"]):
				changed=True
				self.cursors[self.location_id]["cursor_int"]=node_id
		if changed==True:
			print("\tFinal update for the int_cursos is: {}".format(self.cursors[self.location_id]["cursor_int"]))
		self.cursors[self.location_id]["current_cursor"]=self.endCursor
		with open(self.cursorFile,"w+") as f:
			json.dump(self.cursors,f)		

class Downloader():
	def __init__(self, pathConfig,location_id,session,cursor,data):
		since=data["since"].split(",")
		until=data["until"].split(",")
		self.since=datetime(int(since[0]),int(since[1]),int(since[2]))
		self.until=datetime(int(until[0]),int(until[1]),int(until[2]))
		self.instagramObject=Instagram_Object(data,location_id,self.until,self.since,session,cursor)
		self.counter=0

	def search_content(self,field_to_search,data):
		#This cycle will determine my exiting conditions
		for e in data['graphql']['location'][field_to_search]['edges']:
			node=e["node"]
			date_taken=datetime.fromtimestamp(node["taken_at_timestamp"])
			id=str(node["id"])
			#FIRST I CHECK IF I HAVE TO UPLOAD THE PICTURE
			if date_taken>self.since and date_taken<self.until:
				try:
					self.counter+=1	
				except Exception as e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
			#THEN I CHECK IF THE CURSOR FOR THAT PAGE WAS EMPTY:
			if self.instagramObject.cursor_need_update==True:
				#print("\t\t New element we might consider as a candidate is: {}".format(str(id)))
				self.instagramObject.candidatesCursor[date_taken]=str(id)

		if self.instagramObject.candidatesCursor!={}: #IF THE PAGE WAS NOT EMPTY
			self.instagramObject.cursor_need_update=False
			keys=list(self.instagramObject.candidatesCursor)
			keys.sort(reverse=True)
			for key in keys:
				if self.instagramObject.candidatesCursor[key]<self.instagramObject.endCursor:
					#print("Updating old cursor ({}) with a new one ({})".format(self.instagramObject.endCursor,self.instagramObject.candidatesCursor[key]))
					self.instagramObject.endCursor=self.instagramObject.candidatesCursor[key]
					self.instagramObject.updateJsonCursors(key, self.instagramObject.candidatesCursor[key])
					self.instagramObject.candidatesCursor={}
					break

		#Returning the last date only to check the point at which I've arrived
		return datetime.fromtimestamp(data['graphql']['location'][field_to_search]['edges'][-1]["node"]["taken_at_timestamp"])
		
	def start(self):
		self.counter=0
		data=self.instagramObject.getPosts()
		if data!="": #"" IS THE VALUE I'VE RETURNED IN CASE OF ERRORS
			if len(data['graphql']['location']['edge_location_to_media']['edges'])!=0:
				#IF THE edge_location_to_media FIELD IS NOT EMPTY -> DEFAULT BEHAVIOUR
				last_date=self.search_content("edge_location_to_media",data)
			else:
				#TRY TO FIND SOMETHING ELSE TO PROCEDE
				last_date=self.search_content('edge_location_to_top_posts',data)
			return self.counter,last_date, self.instagramObject.endCursor
		else:
			return 0,0,0


if __name__ == '__main__':
	
	LOCATION_FILE="../Get_Locations/Json_locations/location_id_[openhousetorino].json"
	photo_per_location=50 #Limit the number of photo per site

	with open(LOCATION_FILE) as json_file: #Uploading the location I want to study
		locations = json.load(json_file)

	pathConfig="./catalog.json"
	with open(pathConfig) as json_file: #Upload the settings-information from the config
		data = json.load(json_file)

	#Try to get fastly the desired period
	since=data["since"].split(",")
	since=datetime(int(since[0]),int(since[1]),int(since[2]))
	until=data["until"].split(",")
	until=datetime(int(until[0]),int(until[1]),int(until[2]))
	start_pos=[str(el) for el in np.arange(2210000000000000000,2310000000000000000,10000000000000000)]
	linkInst=data["link_Instagram"]
	torPass=data["torPass"]

	s=get_tor_session()
	startFrom=0 #Used to eventually limit the number of JSON considered

	lenFile=len(list(locations.keys())[startFrom:])

	for key in list(locations.keys())[startFrom:]:
		#FIRST PART OF THE LOOP -> UNDERSTAND WHERE TO START SEARCHING FOR THAT LOCATION
		location_id=key
		print(key)
		emptyEdges=0 #counter which indicates that there are no pictures for that location
		for st in start_pos:
			cursor="" #The idea is trying to find the cursor of the last day of the desired period
			try:
				url=linkInst.format(location_id,st)
				r = s.get(url)
				post=json.loads(r.text)
				date_taken=datetime.fromtimestamp(post['graphql']['location']['edge_location_to_media']['edges'][0]["node"]["taken_at_timestamp"])
				print("The date is {}".format(date_taken))
				if date_taken>until:
					cursor=st
					print("Using the cursor {}".format(cursor))
					break
			except Exception as e:
				emptyEdges+=1
				exc_type, exc_obj, exc_tb = sys.exc_info()
				print("1) An exception was launched! {},{}".format(exc_type,exc_tb.tb_lineno))
				renew_connection(torPass)
				s=get_tor_session()
				r = s.get(url)

		indexKey=list(locations.keys())[startFrom:].index(key)
		print("For {} we have: ({} missing)".format(locations[key]["name"],lenFile-indexKey-1))

		#INSTANTIATE THE OBJECT DOWNLOADER -> 1 DOWNLOADER PER LOCATION
		d=Downloader(pathConfig,location_id,s,cursor,data)

		#SERIES OF PARAMETERS TO HANDLE CYCLE BELOW
		it=0
		stopped=0 #Whether we overtook the since-date; got stucked into the same date; too many iterations
		counter=0 #Counter to take account of pictures downloaded per location
		dateOld=""
		while counter<photo_per_location and stopped<3 and emptyEdges<len(start_pos):
			#print("\tStarting iteration: {}".format(it))
			try:
				try:
					increment,lastDate,endCursor=d.start()
				except:
					break
				counter+=increment
				print("\tDown. {} images for location {} at it {}; Last date: {}; Last cursos: {}"\
					.format(counter,locations[key]["name"],it+1,lastDate,endCursor))
				if lastDate==dateOld or lastDate<datetime(2016,12,31) or it>5000:
					stopped+=1
				dateOld=lastDate
				it+=1
				time.sleep(2)
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				print("2) An exception was launched! {},{}".format(exc_type,exc_tb.tb_lineno))				
		print("Ended location!\n")
	