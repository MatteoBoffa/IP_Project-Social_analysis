import flickrapi
import os
import requests

api_key = "d69d71f5e752c16c60f11fab7b1c2dcd"
secret_api_key = "6a9f76bf504824e9"

import pymongo
from pymongo import MongoClient



flickr = flickrapi.FlickrAPI(api_key, secret_api_key)

SIZES = ["url_h", "url_l", "url_c", "url_k", "url_o", "url_t"]  # in order of preference
extras = ','.join(['geo', 'date_upload', 'date_taken', 'tag']) + ','.join(SIZES)

lat = 45.116177
lon = 7.742615

# SET HERE THE PATH TO THE LOCAL DROPBOX FOLDER (Flickr folder will be created automatically)
path = r"C:\Users\Vincenzo\Dropbox (Politecnico Di Torino Studenti)\Pictures_IP\Flickr"

cluster = pymongo.MongoClient("mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority")

db = cluster['Images_Data'] #(db)
collection =db['Flickr_Data'] # (collection into the db - one db can have multiple connections, and a collection is made of posts/documents

if not os.path.isdir(path):
    os.makedirs(path)


photos = flickr.walk(
                     api_key=api_key,
                     lat=lat,
                     lon=lon,
                     radius=32,
                     radius_units='km',
                     #woe_id=3165524,  # Filter per Turin
                     min_taken_date=1483228800, # 1/1/2017
                     max_taken_date=1577750400,  # 31/12/2019
                     #accuracy=11,  # city level accuracy
                     content_type=1,  # for retrieving only photos and not screenshots
                     extras=extras,
                     per_page=150,
                     #The possible values are: date-posted-asc, date-posted-desc, date-taken-asc, date-taken-desc, interestingness-desc, interestingness-asc, and relevance
                     sort= 'interestingness-desc')

new_images_counter = 0

for i, photo in enumerate(photos):
    image_url = ""
    for i in range(len(SIZES)):  # makes sure the loop is done in the order we want
        url = photo.get(SIZES[i])
        if url:  # if url is None try with the next size
            image_url = url
            break
    image_name = url.split("/")[-1]
    extension = image_name[-4:]
    image_name = image_name[:-6] + extension
    image_path = os.path.join(path, image_name)

    if not os.path.isfile(image_path):  # ignore if already downloaded
        try:
            response = requests.get(url, stream=True)
            with open(image_path, 'wb') as outfile:
                outfile.write(response.content)

            _id = photo.get("id")
            secret = photo.get("secret")
            id_secret = _id+"_"+secret
            # occhio perchè image_name con cui viene salvata la foto non coincide con id, ma con id+_+secret+.jpg
            owner = photo.get("owner")
            title = photo.get("title")
            dateupload = photo.get("dateupload")
            datetaken = photo.get("datetaken")
            latitude = photo.get("latitude")
            longitude = photo.get("longitude")
            place_id = photo.get("place_id")
            woeid = photo.get("woeid")
            picture_name = id_secret+".jpg"
            
        
            post = {'id' : _id, 'secret' : secret , 'id_secret' : id_secret, 'picture_name' : picture_name, 'owner' : owner,  'Title': title, 'date_upload': dateupload, 'date_taken' : datetaken, 'latitude' : latitude, 'longitude' : longitude, 'place_id' : place_id, 'woeid' : woeid  }

            collection.insert_one(post)
            
            
            new_images_counter += 1
            print(new_images_counter)

        except requests.exceptions.RequestException as e:
            print(f"download {image_name} failed")
            raise SystemExit(e)

print(f"{new_images_counter} new images were found and downloaded in this session")




