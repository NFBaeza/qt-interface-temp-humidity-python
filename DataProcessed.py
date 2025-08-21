import sys
from datetime import datetime
from mysql.connector import Error
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from dataclasses import dataclass, field
from DBManager import DatabaseManager
import Statistics as stat
import numpy as np

DEBUG = False
MAX_SAMPLE = 2

@dataclass
class value:
	current	:	float = 0.0
	average :	float = 0.0
	maximum :	float = 0.0
	minimum :	float = 0.0
	unit    :   str   = "°C"
	_list	:	list  = field(default_factory=list)

@dataclass
class ts:
	init	 :	datetime = datetime.today()
	end		 :	datetime = datetime.today()
	_list	 : 	list     = field(default_factory=list)



class DataProcessed(QThread):
	temperature_signal 		= pyqtSignal(object)
	humidity_signal  		= pyqtSignal(object)
	stats_process_status	= pyqtSignal(bool)
	plot_process_status		= pyqtSignal(bool)

	def __init__(self, db_worker):
		super().__init__()

		self.db_worker 			= db_worker
		self.temperature 		= value();
		self.humidity 			= value(unit="%");
		self.samples 			= 0;
		self.ts_data 			= ts();
		self.temp_list_graphic 	= []
		self.humi_list_graphic	= []
		self.processing			= False
		self.is_plot 			= False

		self.db_worker.data_updated.connect(self.new_data)

	def new_data(self, data):
		if DEBUG: print(f"Data: {data}")
		if DEBUG: print(f"Processing: {self.processing}")
		
		if (self.samples == 0) and self.processing:
			self.ts_data.init = data['timestamp']

		#LOGICA STATS
		if (self.samples < MAX_SAMPLE) and self.processing:
			if DEBUG: print(f"samples: {self.samples}")
			self.samples+=1
			self.temperature._list.append(data['temperature'])
			self.humidity._list.append(data['humidity'])
		elif (self.samples == MAX_SAMPLE):
			self.ts_data.end = data['timestamp']
			self.temperature._list.append(data['temperature'])
			self.humidity._list.append(data['humidity'])
			if self.is_plot:
				self.plotting()
				self.stats_metrics()
				self.stats_process_status.emit(self.processing)
				self.plot_process_status.emit(self.processing)
				self.is_plot = False
			else:
				self.stats_metrics()
				self.stats_process_status.emit(self.processing)

			self.samples = 0
			self.processing = False
		#------

		#LOGICA NEW DATA	
		if(self.temperature.unit == "°C"):
			self.temperature.current = data['temperature']
		else:
			self.temperature.current = stat.celsius_to_fahrenheit(data['temperature'])

		self.humidity.current = data['humidity']
		self.temperature_signal.emit(self.temperature)
		#--------

	def collecting_data(self):
		if DEBUG: print(f"collecting data...")
		self.samples = 0
		self.humidity._list=[]
		self.temperature._list=[]
		self.processing = True

	def collecting_plotting_data(self):
		if DEBUG: print(f"collecting data...")
		self.samples = 0
		self.humidity._list=[]
		self.temperature._list=[]
		self.processing = True
		self.is_plot = True

	def create_serie_time_list(self):
		timestamps = np.linspace(self.ts_data.init, self.ts_data.end, MAX_SAMPLE+1)
		return timestamps

	def plotting(self):
		self.ts_data._list = self.create_serie_time_list()
		if DEBUG: print(f"Tiempo: {self.ts_data._list}")	


	def unit_change(self, unit_name="°F"):
		if unit_name == "°C":
			self.temperature.current = stat.fahrenheit_to_celsius(self.temperature.current)
			self.temperature._list = [stat.fahrenheit_to_celsius(temp_i) for temp_i in self.temperature._list]
			self.temperature.average = stat.fahrenheit_to_celsius(self.temperature.average)
			self.temperature.maximum = stat.fahrenheit_to_celsius(self.temperature.maximum)
			self.temperature.minimum = stat.fahrenheit_to_celsius(self.temperature.minimum)

		else:
			self.temperature.current = stat.celsius_to_fahrenheit(self.temperature.current)
			self.temperature._list = [stat.celsius_to_fahrenheit(temp_i) for temp_i in self.temperature._list]
			self.temperature.average = stat.celsius_to_fahrenheit(self.temperature.average)
			self.temperature.maximum = stat.celsius_to_fahrenheit(self.temperature.maximum)
			self.temperature.minimum = stat.celsius_to_fahrenheit(self.temperature.minimum)
		self.temperature.unit = unit_name
		self.temperature_signal.emit(self.temperature)

	def stats_metrics(self):
		if DEBUG: print(f"List temp: {self.temperature._list}")
		if DEBUG: print(f"List humi: {self.humidity._list}")
		self.humidity.average = stat.average(self.humidity._list)
		self.humidity.maximum = stat.maximum(self.humidity._list)
		self.humidity.minimum = stat.minimum(self.humidity._list)

		self.temperature.average = stat.average(self.temperature._list)
		self.temperature.maximum = stat.maximum(self.temperature._list)
		self.temperature.minimum = stat.minimum(self.temperature._list)

		self.unit_change()

