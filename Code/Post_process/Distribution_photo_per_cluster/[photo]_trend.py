import sys
import sub.Post_proceser as pp

###############################################
"""
This is a script to check whether there are unusual trends in the numerosity of the taken pictures of an observed cluster
The idea is that, in the presence of anomalies, some strange event might have occurred (concert, event...)
"""
###############################################

assert len(sys.argv) == 4, "Attenton: three parameters are required to run this script (cluster under study, year, save_pictures_flag)"

cluster_analysed = sys.argv[1]
chosen_year = sys.argv[2]
save_pictures = sys.argv[3]

assert cluster_analysed.isdigit(), "Attention: an integer number as chosen cluster is required to run this script"
assert chosen_year.isdigit(), "Attention: an integer number is required as year to run this script"
assert save_pictures in ["yes","no"], "Attention: a yes/no flag is required as save_pictures_flag to run this script"


print("\nInitializing the dropbox instance and the required variables....")

files = ["Flickr_Labeled.csv","Instagram_Labeled.csv"]
id_name = ["ids","id"]
datasets = ["Flickr_v2","Instagram_Data"]
OUTPUT_PATH = "./Output/"
INPUT_PATH = "./Three_years_dataset/"

print("\nStart the analysis considering the number of useful pictures...")
post_proceser = pp.Post_Proceser(files, id_name, cluster_analysed, chosen_year, datasets, OUTPUT_PATH, INPUT_PATH)
post_proceser.get_daily_info()
print("\nPlot the obtained trend...")
post_proceser.plot_trend()
print("\nPrint the top_10 dates:")
post_proceser.best_print()
print("\nSome useful stats (saved on json_file) ...")
list_outliers = post_proceser.get_stats()
if save_pictures == "yes":
	print("\nFinally, saving some pictures of the peaks...")
	post_proceser.save_pictures_peaks(list_outliers)