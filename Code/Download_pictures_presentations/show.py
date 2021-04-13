import os 
import pandas as pd
import dropbox
import pymongo


INPUT_PATH = os.getcwd()+"/Input/"
OUTPUT_PATH = os.getcwd()+"/Output/"
n_pic = 25 #Number of pics to download
token = "aRrjQsduclkAAAAAAAAAAYVVcfozeAj3GyFLXcwjwmQK8sK8JqRcntH9iZ8vB7VV"
dropbox_instance = dropbox.Dropbox(token)

list_convertor = ["Palaces","Miscellaneous","Food","Facilities","Natural_views",\
					"Animals","Shopping","Transportation","Urbanscape",\
					"Exhibits","Religion","Residence","Entertainment","People"]
dict_traslator = {}
for it in range(len(list_convertor)):
	dict_traslator[it+1]=list_convertor[it] 

# GIVING INPUTS
print("Available input files:")
dict_files = {}
for subfolder in os.listdir(INPUT_PATH):
	for it, file in enumerate(os.listdir(INPUT_PATH+subfolder)):
		print(f"\t{it+1}) {subfolder}/{file}")
		dict_files[it+1] = INPUT_PATH+subfolder+"/"+file

file = int(input("\nWhich file do you choose? "))
while file not in dict_files.keys():
	file = int(input("Option not available: which file do you choose? "))

file = dict_files[file]
input_file = pd.read_csv(file)
df = input_file.sample(frac=1).reset_index(drop=True) #SHUFFLE ROWS TO PICK DIFFERENT PIC

clusters = set(df["CLUSTER_ID"])
dict_cluster = {}
print("\nAvailable clusters:")
for it, cluster in enumerate(clusters):
	print(f"\t{it}) {cluster}")
	dict_cluster[it] = cluster

chosen_cluster = int(input("\nWhich cluster do you choose? "))
while chosen_cluster not in dict_cluster.keys():
	chosen_cluster = int(input("Option not available: which cluster do you choose? "))
chosen_cluster = dict_cluster[chosen_cluster]

print("\nAvailable macro-classes:")
for key, value in zip(dict_traslator.keys(), dict_traslator.values()):
	print(f"\t{key}) {value}")

chosen_class = int(input("\nWhich class do you choose? "))
while chosen_class not in dict_traslator.keys():
	chosen_class = int(input("Option not available: which class do you choose? "))
chosen_class = dict_traslator[chosen_class]

dataset = file.split("/")[-1].split(".")[0]
if dataset == "Flickr_final": #To download photos here we need the secret id...
	auth = "mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority"
	pymongo_instance = pymongo.MongoClient(auth)
	db_instance = pymongo_instance['Images_Data']
	collection = db_instance["Flickr_v2"]

output_folder = f"{dataset}_cluster_{chosen_cluster}_class_{chosen_class}/"

os.makedirs(OUTPUT_PATH+output_folder,exist_ok=True)

counter = 0
done = False
#NOW SEARCHING THE PIC TO DOWNLOAD
print("Start downloading pictures...")
for id, predictions, cluster in zip(df["ids"],df["predictions"],df["CLUSTER_ID"]):
	if done == True:
		print("\nEndend downloading!")
		break
	else:
		if cluster == chosen_cluster:
			try: #SOME PREDICTIONS MIGHT BE NAN
				predictions = predictions.split(",")
				for pred in predictions:
					main_class = pred.split(":")[0].strip()
					prob = float(pred.split(":")[1].strip())
					if dict_traslator[int(main_class)] == chosen_class and prob>0.50:
						#PHOTO WE WANT TO DOWNLOAD!
						try:
							with open(OUTPUT_PATH+output_folder+f"pic_{counter+1}.jpg", "wb+") as f:
								if dataset.split("_")[0] == "Flickr":
									result = collection.find({"id":str(id)})
									id_sectret = list(result)[0]["id_secret"]
									try:
										metadata, res = dropbox_instance.files_download(path="/Interdisciplinary Project/Flickr_v2/"+str(id_sectret)+".jpg")
									except:
										metadata, res = dropbox_instance.files_download(path="/Interdisciplinary Project/Flickr/"+str(id_sectret)+".jpg")
								else:
									metadata, res = dropbox_instance.files_download(path="/Interdisciplinary Project/Instagram/"+str(id)+".jpeg")
								print(f"\tDownloaded picture {id}")
								f.write(res.content)
								counter+=1
						except Exception as e: 
							print(f"\t\t\tFailed to download picture {id} - {e}")
							pass
					if counter==n_pic:
						done = True
						break
			except Exception as e:
				print(f"\t\t{predictions} - {e}")
				pass
