import sub.functions as sf

#CONFIGURATION VARIABLE: INDICATES INPUT/OUTPUT PATHS AND NAME OF FILES
UNDER_STUDY = "Center"
INPUT_PATH = "../After_QGIS_Processing/"+UNDER_STUDY+"/Modified/"
OUTPUT_PATH_FILES = "../csv_To_Plot/"+UNDER_STUDY+"/"
OUTPUT_PATH_PICTURES = "../Results/Graphs/"
OUTPUT_PICTURE = OUTPUT_PATH_PICTURES+UNDER_STUDY+".png"
files_input = ["Flickr_final.xls", "Instagram_final.xls"]
files_output = ["Summary_Flickr.csv","Summary_Instagram.csv"]

#OBTAINING INFORMATION PER ZONE
perception_zones = {} #Updated for each file we are considering
points_per_zone = {} #Collect lat and lng of each point per zone (useful to evaluate Inertia)
for file in files_input:
	file_input = INPUT_PATH+file
	perception_zones, points_per_zone = sf.obtain_perception(file_input, perception_zones, points_per_zone)

#PLOT STATS
sf.plot_results(perception_zones, points_per_zone, OUTPUT_PICTURE)

#POST-PROCESS THE DATA ABOUT THE ZONE (EXPORTING AIM)
density_per_zone = sf.process_data(perception_zones, points_per_zone) 
#OBTAINING THE FILES TO PLOT ON QGIS
for it,file in enumerate(files_input):
	file_input = INPUT_PATH+file
	file_output = OUTPUT_PATH_FILES+files_output[it]
	sf.export_file(file_input, perception_zones, points_per_zone, density_per_zone, file_output)

