import sub.DBSCAN as DB
import sub.KMEANS as KM
import sub.GUI as GUI
import os
import json

if __name__ == '__main__':

	INPUT_PATH = "./Raw_data/"
	OUTPUT = "./Output/"
	dict_stats = {}
	datasets = ["Flickr_v2", "Instagram_Data"]


	print("\n"+"#" * 36 +f" STARTING GUI "+"#" * 36+"\n")
	print("\nInstantiating the GUI object...")
	gui = GUI.Thinker(INPUT_PATH, dict_stats)	
	for dataset in datasets:
		print(f"\nSaving results for dataset {dataset}...")
		gui.save_data(dataset)
	INPUT_PATH, chosen_file = gui.get_folder()
	print("\n"+"#" * 36 +f" END OF GUI "+"#" * 36+"\n")
	

	print("\n"+"#" * 36 +f" STARTING DBSCAN ALGORITHM ({chosen_file}) "+"#" * 36+"\n")
	print("\nInstantiating the DBSCAN object...")
	dbscan = DB.DBSCAN(INPUT_PATH, OUTPUT, chosen_file, dict_stats)
	print("\nStarting the 'M' tuning...")
	dbscan.tune()
	print("\nBest results are: ")
	dbscan.get_best()
	print("\nRunning best results...")
	dbscan.run_best()
	print("\nSaving the results...")
	df = dbscan.save_results()
	print("\n"+"#" * 36 +"  DBSCAN ALGORITHM ENDED "+"#" * 36+"\n")


	print("\n"+"#" * 36 +f" STARTING KMEANS ALGORITHM ({chosen_file}) "+"#" * 36+"\n")
	print("\nInstantiating the KMEANS object...")
	kmeans = KM.KMEANS(df, OUTPUT, chosen_file, dict_stats)
	print("\nStarting the 'K' tuning...")
	kmeans.tune()
	print("\nRunning best results...")
	kmeans.best_run()
	print("\n"+"#" * 36 +"  KMEANS ALGORITHM ENDED "+"#" * 36+"\n")

	print("\nSaving stats on json file...")
	with open(OUTPUT+"Json_info/"+chosen_file+".json","w+") as fb:
		json.dump(dict_stats,fb,indent=4)
