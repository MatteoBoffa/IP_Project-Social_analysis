import pymongo
from datetime import datetime
import pandas as pd
import tkinter as tk
import os  
from tkcalendar import Calendar, DateEntry
from tqdm import tqdm

class Thinker():

	def __init__(self,INPUT_PATH, dict_stats):
		self.INPUT_PATH = INPUT_PATH
		self.dates = []
		self.dict_stats = dict_stats
		self.select_period()
		self.create_folder()

	def send_dates(self):
		response_startDate = self.startDate_input.get()
		response_endDate = self.endDate_input.get()
		if response_startDate and response_endDate and (self.weekdays.get() == 1 or self.weekends.get() == 1) :
			self.dates.append(response_startDate)
			self.dates.append(response_endDate)
		elif self.startDate_input.get() == '':
			self.labelframe.config(text='Select a starting date ')
		elif self.endDate_input.get() == '':
			self.labelframe.config(text='Select an ending date')
		elif self.weekdays.get() == 0 and self.weekends.get() == 0:
			self.labelframe.config(text='Before proceding, you should choose at least one type of day')
	def print_selection(self):
		if (self.weekdays.get() == 0) & (self.weekends.get() == 0):
			self.labelframe.config(text='Before proceding, you should choose at least one type of day')
		if (self.morning.get() == 0) & (self.afternoon.get() == 0) & (self.evening.get() == 0) & (self.night.get() == 0):
			self.labelframe.config(text='Before proceding, you should choose at least one type a period of the day')
		else:
			self.labelframe.config(text='Choose Dates')

	def on_closing(self):
		self.window.destroy()

	def select_period(self):

		self.window = tk.Tk()
		self.window.title("Interdisciplinary Project")
		self.labelframe = tk.LabelFrame(self.window, text="Choose Dates", fg='red', font=('Helvetica', 14))
		self.labelframe.grid()
		text = ('Welcome to this python script.\nHere you can select the dates, starting and final, to filter Flickr data in order to further cluster them\
				\n Please insert the date in the following format : YYYY-mm-dd HH:MM:SS, hour is not required.')
		text_output = tk.Label(self.labelframe, text= text, font=('Helvetica', 12, 'bold'))
		text_output.grid(row=0, column=0, sticky='W')
		self.startDate = tk.Label(self.labelframe,
							text= 'Starting Date : ',
							font= ('Helvetica', 12, 'bold'))
		self.startDate.grid(row=1, column=0, sticky='W', pady=20)
		self.startDate_input = tk.Entry(self.labelframe, width=50)
		self.startDate_input.grid(row=1, column=0, pady=20)
		self.endDate = tk.Label(self.labelframe,
							text= 'Ending Date : ',
							font= ('Helvetica', 12, 'bold'))
		self.endDate.grid(row=2, column=0, sticky='W', pady=20)
		self.endDate_input = tk.Entry(self.labelframe, width=50)
		self.endDate_input.grid(row=2, column=0, pady=20)

		self.weekdays = tk.IntVar()
		self.weekends = tk.IntVar()

		self.morning = tk.IntVar()
		self.afternoon = tk.IntVar()
		self.evening = tk.IntVar()
		self.night = tk.IntVar()

		c1 = tk.Checkbutton(self.labelframe, text='Weekdays',variable=self.weekdays, onvalue=1, offvalue=0, font=('Helvetica', 12, 'bold'), command=self.print_selection)
		c1.grid(row=1, column=1, sticky = 'W')
		c2 = tk.Checkbutton(self.labelframe, text='Weekends',variable=self.weekends, onvalue=1, offvalue=0,font=('Helvetica', 12, 'bold'), command=self.print_selection)
		c2.grid(row=2, column=1, sticky = 'W')

		c3 = tk.Checkbutton(self.labelframe, text='Morning (7:00 - 13:00)',variable=self.morning, onvalue=1, offvalue=0, font=('Helvetica', 12, 'bold'), command=self.print_selection)
		c3.grid(row=1, column=2, sticky = 'W', pady=15, padx= 10)
		c4 = tk.Checkbutton(self.labelframe, text='Afternoon (14:00 - 19:00)',variable=self.afternoon, onvalue=1, offvalue=0,font=('Helvetica', 12, 'bold'), command=self.print_selection)
		c4.grid(row=2, column=2, sticky = 'W', pady=15, padx= 10)

		c5 = tk.Checkbutton(self.labelframe, text='Evening (20:00 - 23:00)',variable=self.evening, onvalue=1, offvalue=0, font=('Helvetica', 12, 'bold'), command=self.print_selection)
		c5.grid(row=3, column=2, sticky = 'W', pady=15, padx= 10)
		c6 = tk.Checkbutton(self.labelframe, text='Night (00:00 - 6:00)',variable=self.night, onvalue=1, offvalue=0,font=('Helvetica', 12, 'bold'), command=self.print_selection)
		c6.grid(row=4, column=2, sticky = 'W', pady=15, padx= 10)

		send_button = tk.Button(text='Apply',fg='red', font= ('Helvetica', 12), command=self.send_dates)
		send_button.grid(row=5, column=0, pady=10, padx=10)

		confirm_button = tk.Button(text='Confirm', fg='red',font= ('Helvetica', 12), command=self.on_closing)
		confirm_button.grid(row=6, column=0, pady=10, padx=10)

		self.window.mainloop()
		self.dateStart = self.dates[0]
		self.dateEnd = self.dates[1]
		self.weekdays_output = self.weekdays.get()
		self.weekends_output = self.weekends.get()
		self.morning_output = self.morning.get()
		self.afternoon_output = self.afternoon.get()
		self.evening_output = self.evening.get()
		self.night_output = self.night.get()
		self.print_choices()

	def print_choices(self):
		print("\n\tYour choice were:")
		print(f"\t\t- Period: {self.dateStart} to {self.dateEnd}")
		print(f"\t\t- Weekends: {self.weekends_output}")
		print(f"\t\t- Weekdays: {self.weekdays_output}")
		print(f"\t\t- Mornings: {self.morning_output}")
		print(f"\t\t- Afternoons: {self.afternoon_output}")
		print(f"\t\t- Evenings: {self.evening_output}")
		print(f"\t\t- Nights: {self.night_output}")

		#UPDATE STATS
		self.dict_stats["start_date"] = self.dateStart
		self.dict_stats["end_date"] = self.dateEnd
		self.dict_stats["weekdays"] = self.weekdays_output
		self.dict_stats["weekends"] = self.weekends_output
		self.dict_stats["morning"] = self.morning_output
		self.dict_stats["afternoon"] = self.afternoon_output
		self.dict_stats["evening"] = self.evening_output
		self.dict_stats["night"] = self.night_output

	def create_folder(self):
		yearStart = self.dateStart.split("-")[0]
		monthStart = self.dateStart.split("-")[1]
		dayStart = self.dateStart.split("-")[2]
		yearEnd = self.dateEnd.split("-")[0]
		monthEnd = self.dateEnd.split("-")[1]
		dayEnd = self.dateEnd.split("-")[2]
		try:
			name_folder = f'points_from _{yearStart}-{monthStart}-{dayStart}_to_{yearEnd}-{monthEnd}-{dayEnd}_weekdays_{self.weekdays_output}_weekends_{self.weekends_output}_morning_{self.morning_output}_afternoon_{self.afternoon_output}_evening_{self.evening_output}_night_{self.night_output}'
			self.FOLDER = self.INPUT_PATH+name_folder
			if name_folder not in os.listdir(self.INPUT_PATH):
				os.mkdir(self.FOLDER)
				print ("\n\tSuccessfully created the directory %s " % self.FOLDER)
			else:
				print ("\n\tDirectory %s already present" % self.FOLDER)
		except Exception as e:
			print ("\n\tCreation of the directory %s failed" % self.FOLDER)			
	
	def get_folder(self):
		file = self.dateStart+"_to_"+self.dateEnd+"_"+str(self.weekends_output)+str(self.weekdays_output)+"_"+str(self.morning_output)+str(self.afternoon_output)+str(self.evening_output)+str(self.night_output)
		return self.FOLDER, file

	def query_dataset(self,dataset):
		cluster = pymongo.MongoClient("mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority")
		db = cluster['Images_Data'] #(db)
		collection =db[dataset]
		if dataset == "Flickr_v2":
			lat_key = "latitude"
			lng_key = "longitude"
		else:
			lat_key = "lat"
			lng_key = "lng"
		results=list(collection.aggregate([
				{'$project':{
					"date_taken":1,
					f"{lat_key}":1,
					f"{lng_key}":1,
					"macro_predictions":1,
					"id":1
				}}
			]))
		return results
		   
	def save_data(self, dataset):
		data = pd.DataFrame()
		results = self.query_dataset(dataset)
		good_days = self.obtain_good_days()		
		good_hours = self.obtain_good_hours()    
		listLat,listLon, listId,listPred = self.return_lists_elements(results, good_days, good_hours, dataset)
		data['lat'] = listLat
		data['lon'] = listLon
		data['id'] = listId
		data['predictions'] = listPred
		data.to_csv(self.FOLDER+f'/{dataset}.csv')

	def obtain_good_hours(self):
		if self.morning_output == 1 and self.afternoon_output == 1 and self.evening_output == 1 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
		if self.morning_output == 1 and self.afternoon_output == 0 and self.evening_output == 0 and self.night_output == 0:
			good_hours = [7, 8, 9, 10, 11, 12, 13]
		if self.morning_output == 0 and self.afternoon_output == 1 and self.evening_output == 0 and self.night_output == 0:
			good_hours = [14, 15, 16, 17, 18, 19]
		if self.morning_output == 0 and self.afternoon_output == 0 and self.evening_output == 1 and self.night_output == 0:
			good_hours = [20, 21, 22, 23]
		if self.morning_output == 0 and self.afternoon_output == 0 and self.evening_output == 0 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6]
		if self.morning_output == 1 and self.afternoon_output == 1 and self.evening_output == 0 and self.night_output == 0:
			good_hours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
		if self.morning_output == 1 and self.afternoon_output == 0 and self.evening_output == 1 and self.night_output == 0:
			good_hours = [7, 8, 9, 10, 11, 12, 13, 20, 21, 22, 23]
		if self.morning_output == 1 and self.afternoon_output == 0 and self.evening_output == 0 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
		if self.morning_output == 0 and self.afternoon_output == 1 and self.evening_output == 0 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6, 14, 15, 16, 17, 18, 19]
		if self.morning_output == 0 and self.afternoon_output == 1 and self.evening_output == 1 and self.night_output == 0:
			good_hours = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
		if self.morning_output == 0 and self.afternoon_output == 0 and self.evening_output == 1 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6, 20, 21, 22, 23]
		if self.morning_output == 1 and self.afternoon_output == 1 and self.evening_output == 1 and self.night_output == 0:
			good_hours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
		if self.morning_output == 1 and self.afternoon_output == 1 and self.evening_output == 0 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
		if self.morning_output == 1 and self.afternoon_output == 0 and self.evening_output == 1 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 20, 21, 22, 23]
		if self.morning_output == 0 and self.afternoon_output == 1 and self.evening_output == 1 and self.night_output == 1:
			good_hours = [0, 1, 2, 3, 4, 5, 6, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
		return good_hours

	def obtain_good_days(self):
		if self.weekdays_output == 1 and self.weekends_output == 1:
			good_days = [0, 1, 2, 3, 4, 5, 6]
		elif self.weekdays_output == 1 and self.weekends_output == 0:
			good_days = [0, 1, 2, 3, 4, 5]
		elif self.weekdays_output == 0 and self.weekends_output == 1:
			good_days = [6]
		return good_days

	def return_lists_elements(self,results, good_days, good_hours, dataset):

		listLat = []
		listLon = []
		listId = []
		listPred = []
		lat_lim=[45.00,45.15]
		lon_lim=[7.576,7.7724]
		count = 0
		count_exceptions = 0
		flag_exception = False

		if dataset == "Flickr_v2":
			lat_key = "latitude"
			lng_key = "longitude"
		else:
			lat_key = "lat"
			lng_key = "lng"

		for it in tqdm(range(len(results))):
			el = results[it]
			lat=float(el[lat_key])
			lng=float(el[lng_key])
			id_photo = el["id"]
			try:
				pred = el["macro_predictions"]
				flag_exception = False
			except:
				count_exceptions += 1
				flag_exception = True
				
			if lat>=lat_lim[0] and lat<=lat_lim[1] and lng>=lon_lim[0] and lng<=lon_lim[1]:
				try:
					date=datetime.strptime(el["date_taken"], '%Y-%m-%d %H:%M:%S')
				except:
					date=el["date_taken"]
				hour_date = date.hour
				x = self.dates[0]
				y = self.dates[1]
				dateStart = datetime.strptime(x, '%Y-%m-%d')
				dateEnd = datetime.strptime(y, '%Y-%m-%d')
				if date >= dateStart and date <= dateEnd:
					day = date.weekday()
					if day in good_days:
						if hour_date in good_hours:
							listLat.append(lat)
							listLon.append(lng)
							listId.append(id_photo)
							if flag_exception == False:
								listPred.append(pred)
							else:
								listPred.append("")
							count += 1
		#UPDATE_STATS
		self.dict_stats[f"[photo]_{dataset}"] = str(count)
		return listLat,listLon, listId,listPred