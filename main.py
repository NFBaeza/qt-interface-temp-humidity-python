from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QHBoxLayout, QCheckBox, QLineEdit, QFrame, QVBoxLayout, QSpinBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator, QPixmap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from datetime import datetime
import staticts as stat
import numpy as np
from db import DatabaseManager

DEBUG = True
MAX_SAMPLE = 2
datetime_init = datetime.today()

temperature_range = {"°F": [-212, 212], "°C": [-100,100]}

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.db_worker = DatabaseManager()
		self.db_worker.setup_polling(5000) 
		self.db_worker.data_updated.connect(self.update_ui_with_data)
		
		#datos = self.db_manager.get_latest_record('readings')
		#self.db_manager.setup_polling()
		
		self.setWindowTitle("My App")
		self.resize(1000, 600) 

		self.temperature = 0.0
		self.humidity = 0.0
		self.temperature_unit_name = "°F"
		self.humidity_unit_name = "%"

		self.temperature_avg = self.temperature_max = self.temperature_min = 0.0
		self.humidity_avg = self.humidity_max = self.humidity_min = 0.0

		self.stats_was_pressed = False	
		self.create_graphic_button_was_pressed =  False
		self.samples = 0
		self.ts_data = [datetime_init, datetime_init]
		self.temp_list = []
		self.humi_list = []
		self.temp_list_graphic = []
		self.time_list = []
		self.plot1 = None

		self.container_init()

	def closeEvent(self, event):
		self.db_worker.stop()
		event.accept()

	def update_ui_with_data(self, data_dict):
		if DEBUG: print(f"Data: {data_dict}")

		if (self.stats_was_pressed or self.create_graphic_button_was_pressed):
			if (self.samples == 0):
					self.ts_data[0]= data_dict['timestamp']

			if(self.samples < MAX_SAMPLE):
				self.temp_list.append(data_dict['id'])
				self.humi_list.append(data_dict['humidity'])
				self.samples= self.samples+1
				if DEBUG: print("sample collected: ", self.samples)
				
			if(self.samples == MAX_SAMPLE):
				self.ts_data[1]= data_dict['timestamp']				
				if(self.stats_was_pressed):
					self.stats_metrics(True)
				else:
					self.create_graphic(True)
				self.samples = 0
				self.temp_list = []
				self.humi_list = []

		if (self.temperature_unit_name == "°C"):
			self.temperature=data_dict['id']
		else:
			self.temperature=stat.celsius_to_fahrenheit(data_dict['id'])

		self.humidity=data_dict['humidity']
		self.update_ui()

	def unit_change(self, state):
		self.modo_activo = (state == Qt.Checked)
		if state == Qt.Checked:
			self.temperature_unit_name = "°C"
			self.temperature = stat.fahrenheit_to_celsius(self.temperature)
			self.temp_list_graphic = [stat.fahrenheit_to_celsius(temp_i) for temp_i in self.temp_list_graphic]
			self.avg_temperature = stat.fahrenheit_to_celsius(self.temperature_avg)
			self.avg_temperature = stat.fahrenheit_to_celsius(self.temperature_avg)
			self.max_temperature = stat.fahrenheit_to_celsius(self.temperature_max)
			self.min_temperature = stat.fahrenheit_to_celsius(self.temperature_min)

		else:
			self.temperature_unit_name = "°F"
			self.temperature = stat.celsius_to_fahrenheit(self.temperature)
			self.temp_list_graphic = [stat.celsius_to_fahrenheit(temp_i) for temp_i in self.temp_list_graphic]
			self.avg_temperature = stat.celsius_to_fahrenheit(self.temperature_avg)
			self.max_temperature = stat.celsius_to_fahrenheit(self.temperature_max)
			self.min_temperature = stat.celsius_to_fahrenheit(self.temperature_min)

		self.update_ui()

	def stats_metrics(self, done=False):
		self.stats_was_pressed = True;
		if (self.stats_was_pressed): 
			self.statistic_button.setEnabled(False)
			self.graphic_button.setEnabled(False)	

		if done:
			self.statistic_button.setEnabled(True)
			self.graphic_button.setEnabled(True)
			self.stats_was_pressed = False;
			self.temperature_avg = stat.average(self.temp_list)
			self.temperature_max = stat.maximum(self.temp_list)
			self.temperature_min = stat.minimum(self.temp_list)
			self.humidity_avg = stat.average(self.humi_list)
			self.humidity_max = stat.maximum(self.humi_list)
			self.humidity_min = stat.minimum(self.humi_list)
			self.update_ui();
			

	def update_ui(self):
		self.timestamp_lapse.setText("{:<10} {} {} {}\n".format("Time lapse:", self.ts_data[0].strftime("%d/%m/%y %H:%M:%S"), "-" , self.ts_data[1].strftime("%H:%M:%S")))
		self.temperature_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.temperature, self.temperature_unit_name))
		self.humidity_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.humidity, self.humidity_unit_name))
		self.temperature_avg_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.temperature_avg, self.temperature_unit_name))
		self.temperature_max_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.temperature_max, self.temperature_unit_name))
		self.temperature_min_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.temperature_min, self.temperature_unit_name))
		self.humidity_avg_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.humidity_avg, self.humidity_unit_name))
		self.humidity_max_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.humidity_max, self.humidity_unit_name))
		self.humidity_min_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.humidity_min, self.humidity_unit_name))
		self.temperature_alarm_threshold.setValidator(QIntValidator(temperature_range[self.temperature_unit_name][0],temperature_range[self.temperature_unit_name][1]))  
		self.temperature_unit_label.setText(self.temperature_unit_name)

		if (self.temp_list_graphic != []):
			
			self.plot1.set_ydata(self.temp_list_graphic)
			self.ax.set_ylabel(self.temperature_unit_name)
			
			self.ax.relim()                    # Recalcular límites basado en nuevos dato
			self.ax.autoscale_view()
			self.canvas.draw()


	def create_serie_time_list(self):
		timestamps = np.linspace(self.ts_data[0], self.ts_data[1], MAX_SAMPLE)
		return timestamps

	def create_graphic(self, done = False):
		self.create_graphic_button_was_pressed = True;
		self.temp_list_graphic =[]

		if (self.create_graphic_button_was_pressed): 
			self.canvas.setVisible(True)
			self.etiqueta_imagen.setVisible(False)
			self.statistic_button.setEnabled(False)
			self.graphic_button.setEnabled(False)

			self.plot.clear()
			self.ax = self.plot.add_subplot(111)	
			self.ax.grid(True, alpha=0.3)

		if done:
			self.create_graphic_button_was_pressed = False;
			self.statistic_button.setEnabled(True)
			self.graphic_button.setEnabled(True)

			self.time_list = self.create_serie_time_list()
			self.temp_list_graphic = self.temp_list 

			if (self.temperature_unit_name == "°F"):
				self.temp_list_graphic = [stat.celsius_to_fahrenheit(temp_i) for temp_i in self.temp_list]
			else:
				self.temp_list_graphic = self.temp_list 

			self.plot1, = self.ax.plot(self.time_list, self.temp_list_graphic,  linestyle="--", marker='o', label='id', color='purple')
			self.ax.set_ylabel(self.temperature_unit_name)
			ax2 = self.ax.twinx()
			ax2.plot(self.time_list, self.humi_list, linestyle="--", marker='x', label='Humidity', color='cyan')
			self.ax.set_xlabel('time')
			ax2.set_ylabel(self.humidity_unit_name)
			self.ax.set_title('Temperature & Humidity')
			self.ax.legend(loc='lower right', fontsize='small')
			ax2.legend()
			self.canvas.draw()
			

	def actualizar_grafico(self):
		umbral = self.umbral_spin.value()

		#self.ax.clear()
		print(umbral)
		
		temp_colors = ['red' if y > umbral else 'purple' for y in self.temp_list_graphic]
		humi_colors = ['red' if y > umbral else 'cyan' for y in self.humi_list]
		
		self.plot1.scatter(self.time_list, self.temp_list_graphic, c=temp_colors, s=30, alpha=0.7)
		##self.ax.scatter(self.time_list, self.humi_list, c=humi_colors, s=30, alpha=0.7)

		self.canvas.draw()


	def container_init(self):
		widget_central = QWidget()

		container = QGridLayout()
		container.setContentsMargins(10, 7, 10, 7)

		checkbox = QCheckBox("°C")
		checkbox.stateChanged.connect(self.unit_change)

		pixmap = QPixmap("original.jpg")

		self.etiqueta_imagen = QLabel()
		self.etiqueta_imagen.setPixmap(pixmap)
		self.etiqueta_imagen.setMinimumSize(300, 200)
		self.etiqueta_imagen.setScaledContents(True)  
		self.etiqueta_imagen.setStyleSheet("padding: 5px")

		self.plot = Figure()
		self.canvas = FigureCanvas(self.plot)
		self.canvas.setMinimumSize(300,548)
		
		buttons_layout = QHBoxLayout()

		self.graphic_button = QPushButton("graphic")
		self.graphic_button.clicked.connect(self.create_graphic)

		self.statistic_button = QPushButton("statistic")
		self.statistic_button.clicked.connect(self.stats_metrics)

		button3 = QPushButton("set threshold")

		buttons_layout.addWidget(self.graphic_button)
		buttons_layout.addWidget(self.statistic_button)
		buttons_layout.addWidget(button3)
		
		buttons_layout.setSpacing(40)

		
		buttons_container = QWidget()
		buttons_container.setLayout(buttons_layout)
		buttons_container.setStyleSheet("background-color: #a3c1da;") 


		data_layout = QGridLayout()
		
		self.temperature_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.temperature, self.temperature_unit_name))
		self.humidity_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.humidity, self.humidity_unit_name))


		avg_label = QLabel("Average")
		avg_label.setStyleSheet("padding-left: 8px; font-size: 12px")
		self.timestamp_lapse = QLabel("{:<10} {} {} {}\n".format("Time lapse:", self.ts_data[0].strftime("%d/%m/%y %H:%M:%S"), "-" , self.ts_data[1].strftime("%H:%M:%S")))
		self.temperature_avg_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.temperature_avg, self.temperature_unit_name))
		self.humidity_avg_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.humidity_avg, self.humidity_unit_name))

		max_label = QLabel("Highest Sample")
		max_label.setStyleSheet("padding-left: 8px")
		self.temperature_max_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.temperature_max, self.temperature_unit_name))
		self.humidity_max_label= QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.humidity_max, self.humidity_unit_name))

		min_label = QLabel("Lowest Sample")
		min_label.setStyleSheet("padding-left: 8px")
		self.temperature_min_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.temperature_min, self.temperature_unit_name))
		self.humidity_min_label =QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.humidity_min, self.humidity_unit_name))

		data_label = QLabel("Instantanea Data")
		data_label.setFixedSize(300, 30)
		data_label.setStyleSheet("font-size: 14px; padding: 3px; background-color: #DDEEFF; font-weight: bold; qproperty-alignment: AlignCenter")

		stat_label = QLabel("Statistic")
		stat_label.setFixedSize(300, 30)
		stat_label.setStyleSheet("font-size: 14px; padding: 3px; background-color: #DDEEFF; font-weight: bold; qproperty-alignment: AlignCenter")

		alarm_label = QLabel("Alarm Level Threshold")
		alarm_label.setFixedSize(300, 30)
		alarm_label.setStyleSheet("font-size: 14px; padding: 3px; background-color: #DDEEFF; font-weight: bold; qproperty-alignment: AlignCenter")

		temperature_name_label = QLabel("Temperature: ")
		humidity_name_label = QLabel("Humidity: ")
		self.temperature_unit_label = QLabel(self.temperature_unit_name)
		humidity_unit_label = QLabel(self.humidity_unit_name)
		self.temperature_alarm_threshold = QLineEdit(self)
		self.temperature_alarm_threshold.setValidator(QIntValidator(temperature_range[self.temperature_unit_name][0],temperature_range[self.temperature_unit_name][1]))  

		self.humidity_alarm_threshold = QLineEdit(self)
		self.humidity_alarm_threshold.setValidator(QIntValidator(0, 100))  
 
		data_layout.addWidget(data_label, 0, 0, 1 , 3)  
		data_layout.addWidget(self.temperature_label, 1, 0)  
		data_layout.addWidget(self.humidity_label, 1, 1)  

		data_layout.addWidget(stat_label, 2, 0, 1 , 3)  
		data_layout.addWidget(self.timestamp_lapse, 3, 0, 1 , 3)

		data_layout.addWidget(avg_label, 4, 0, 1 , 3)  
		data_layout.addWidget(QFrame(frameShape=QFrame.Panel, frameShadow=QFrame.Sunken),4,0,1,3)
		data_layout.addWidget(self.temperature_avg_label, 5, 0)  
		data_layout.addWidget(self.humidity_avg_label, 5, 1)  

		data_layout.addWidget(max_label, 6, 0, 1 , 3)  
		data_layout.addWidget(QFrame(frameShape=QFrame.Panel, frameShadow=QFrame.Sunken),6,0,1,3)
		data_layout.addWidget(self.temperature_max_label, 7, 0)  
		data_layout.addWidget(self.humidity_max_label, 7, 1)  

		data_layout.addWidget(min_label, 8, 0, 1 , 3)  
		data_layout.addWidget(QFrame(frameShape=QFrame.Panel, frameShadow=QFrame.Sunken),8,0,1,3)
		data_layout.addWidget(self.temperature_min_label, 9, 0)  
		data_layout.addWidget(self.humidity_min_label, 9, 1)  

		
### aca estoy 
		self.umbral_spin = QSpinBox()
		self.umbral_spin.setRange(-10000, 10000)
		self.umbral_spin.setValue(0)
		self.umbral_spin.valueChanged.connect(self.actualizar_grafico)


		data_layout.addWidget(alarm_label, 10, 0, 1, 3)  
		data_layout.addWidget(temperature_name_label, 11, 0)  
		data_layout.addWidget(self.umbral_spin, 11, 1)  
		data_layout.addWidget(self.temperature_unit_label, 11, 2)  
		
		data_layout.addWidget(humidity_name_label, 12, 0)  
		data_layout.addWidget(self.humidity_alarm_threshold, 12, 1)  
		data_layout.addWidget(humidity_unit_label, 12, 2)  
	   
		data_container = QWidget()
		data_container.setLayout(data_layout)

		container.addWidget(buttons_container, 6, 0, 1, 1)

		container.addWidget(self.canvas, 0, 0, 1, 1, Qt.AlignLeft)
		container.addWidget(self.etiqueta_imagen, 0, 0, 1, 1, Qt.AlignLeft)
		self.canvas.setVisible(False)

		container.addWidget(data_container, 0, 1, 1, 1, Qt.AlignRight)   
		container.addWidget(checkbox, 6, 1, 1, 2, Qt.AlignCenter)  

		widget_central.setLayout(container)

		self.setCentralWidget(widget_central)


app = QApplication([])

window = MainWindow()
window.show()

app.exec()

