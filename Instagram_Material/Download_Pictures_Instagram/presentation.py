


#GET ALL THE PICTURES UPLOADED FROM A LOCATION
pictures_uploaded=pymongo_database.find({"location_id":location_id})
			
if picture not in pictures_uploaded:
	"""
	DOWNLOAD IMAGE 
		&
	COLLECT METADATA HERE
	"""
	pymongo_database.insert_one(METADATA,ID_PICTURE)
	dropbox_folder.files_upload(STREAMED_PICTURE, DROPBOX_PATH, ID_PICTURE)

