from datetime import datetime
import instaloader
import json
import time

listTags=["torino_photogroup","torinoarte","torinodascoprire",\
"torinofoodporn","torinomusei","sporttorino"]

dictCoordinates={}
alreadyHave=[]
with open("../Results/joined_results.json") as json_file:
	locations = json.load(json_file)
	alreadyHave=list(locations.keys())

L = instaloader.Instaloader()

L.login("username","password")

namePage="openhousetorino"

posts = L.get_hashtag_posts(namePage)

i=0

for post in posts:
	print("Post number: {}".format(i+1))
	try:
		if post.location!=None and str(post.location.id) not in list(dictCoordinates.keys()) and str(post.location.id) not in alreadyHave:
			if post.location.lat!=None and post.location.lat>44.95 and post.location.lat<45.15:
				if post.location.lng!=None and post.location.lng>7.51 and post.location.lng<7.85:
					print("\tThis was a good one!")
					dictCoordinates[str(post.location.id)]={
					"name":post.location.name,
					"slug":post.location.slug,
					"has_public_page":post.location.has_public_page,
					"lat":post.location.lat,
					"lng":post.location.lng
					}
					i+=1
					#L.download_post(post, "#"+namePage)
				if i==200:
					break
	except Exception as e:
		print(e)
		break

print("****\tGot {} new places\t****".format(i))
with open("./Json_locations/location_id_[{}].json".format(namePage), "a+") as write_file:
    json.dump(dictCoordinates, write_file, indent=4, sort_keys=True)
