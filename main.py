from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QHBoxLayout, QCheckBox, QLineEdit, QFrame, QVBoxLayout, QSpinBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator, QPixmap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from datetime import datetime
import numpy as np
from DataProcessed import DataProcessed
from DBManager import DatabaseManager

DEBUG = False
temperature_range = {"°F": [-20, 212], "°C": [-100,100]}

class MainWindow(QMainWindow):
	statistic_button_signal = pyqtSignal(bool)
	plot_button_signal  	= pyqtSignal(bool)

	def __init__(self):
		super().__init__()

		self.db_worker = DatabaseManager()
		self.db_worker.setup_polling(5000) 

		self.setWindowTitle("My App")
		self.resize(1000, 600) 

		self.data = DataProcessed(self.db_worker)

		self.temperature_unit_name = "°F"
		self.humidity_unit_name = "%"

		self.data.temperature_signal.connect(self.update_ui)
		self.data.stats_process_status.connect(self.stats_button_ui_manager)
		self.data.plot_process_status.connect(self.update_graphic_temp)
		self.statistic_button_signal.connect(self.data.collecting_data)
		self.plot_button_signal.connect(self.data.collecting_plotting_data)

		self.container_init()

	def closeEvent(self, event):
		self.db_worker.stop()
		event.accept()


	def unit_change_checkbox(self, state):
		self.modo_activo = (state == Qt.Checked)
		if state == Qt.Checked:
			self.temperature_unit_name = "°C"
			self.data.unit_change(self.temperature_unit_name)

		else:
			self.temperature_unit_name = "°F"
			self.data.unit_change(self.temperature_unit_name)

		self.update_ui_graphic_temp()
		self.update_ui()

	def stats_button_ui_manager(self, status):
		if status: 
			self.statistic_button.setEnabled(True)
			self.graphic_button.setEnabled(True)
			self.checkbox.setEnabled(True)
			self.update_ui();

		else:
			self.statistic_button.setEnabled(False)
			self.graphic_button.setEnabled(False)
			self.checkbox.setEnabled(False)
			self.statistic_button_signal.emit(True)

	def update_ui_graphic_temp(self):
		if hasattr(self, 'temp_line_plot') and self.data.temperature._list:
			temp_threshold = self.temp_threshold_spin.value()
			if DEBUG: print(f'Threshold: {temp_threshold}')

			temp_new_color = ['red' if temp > temp_threshold else 'purple' 
						 for temp in self.data.temperature._list]

			self.temp_line_plot.set_ydata(self.data.temperature._list)
			self.temp_line_scatter.remove()
			self.temp_line_scatter = self.ax.scatter(self.data.ts_data._list, self.data.temperature._list,
									c=temp_new_color,
									s=50,
									alpha=0.8,
									label='Temperature',
									marker="^")

			self.ax.legend(loc='lower right', fontsize='small')
			self.ax.set_ylabel(self.temperature_unit_name)
			self.ax.relim()
			self.ax.autoscale_view(scaley=True)
			self.canvas.draw()


	def update_ui_graphic_humi(self):
		if hasattr(self, 'humi_line_plot') and self.data.humidity._list:
			humi_threshold = self.humi_threshold_spin.value()
			if DEBUG: print(f'Threshold: {humi_threshold}')

			humi_new_colors = ['cyan' if humi > humi_threshold else 'blue' 
						 for humi in self.data.humidity._list]

			self.humi_line_plot.set_ydata(self.data.humidity._list)
			self.humi_line_scatter.remove()
			self.humi_line_scatter = self.ax2.scatter(self.data.ts_data._list, self.data.humidity._list,
                                                c=humi_new_colors,
	                                            s=50,
	                                            alpha=0.6,
	                                            label='Humidity')

			self.ax.legend(loc='lower right', fontsize='small')
			self.ax.set_ylabel(self.humidity_unit_name)
			self.ax.relim()
			self.ax.autoscale_view(scaley=True)
			self.canvas.draw()
			
			
	def update_graphic_temp(self):
		self.statistic_button.setEnabled(True)
		self.graphic_button.setEnabled(True)
		self.checkbox.setEnabled(True)
		self.humi_threshold_spin.setEnabled(True)
		self.temp_threshold_spin.setEnabled(True)

		self.temp_line_plot, = self.ax.plot(self.data.ts_data._list, self.data.temperature._list, linestyle="--", color='purple', alpha=0.5, linewidth=1.5)
		self.temp_line_scatter = self.ax.scatter(self.data.ts_data._list, self.data.temperature._list, c='purple', s=50, alpha=0.8, label='Temperature', marker="^")
		self.ax.set_ylabel(self.temperature_unit_name)

		self.ax2 = self.ax.twinx()
		self.humi_line_plot, = self.ax2.plot(self.data.ts_data._list, self.data.humidity._list, linestyle="--", color='blue', alpha=0.5, linewidth=1.5)
		self.humi_line_scatter = self.ax2.scatter(self.data.ts_data._list, self.data.humidity._list, c='blue', s=50, alpha=0.6, label='Humidity')
		self.ax2.set_ylabel(self.humidity_unit_name)

		self.ax.set_xlabel('Time')
		self.ax.set_title('Temperature & Humidity')
		self.ax.legend(loc='lower right', fontsize='small')
		self.canvas.draw()


	def create_graphic(self):
		self.canvas.setVisible(True)
		self.etiqueta_imagen.setVisible(False)
		self.statistic_button.setEnabled(False)
		self.graphic_button.setEnabled(False)
		self.checkbox.setEnabled(False)
		self.humi_threshold_spin.setEnabled(False)
		self.temp_threshold_spin.setEnabled(False)

		self.plot.clear()
		self.ax = self.plot.add_subplot(111)	
		self.ax.grid(True, alpha=0.3)

		self.plot_button_signal.emit(True)

			
	def update_ui(self):
		self.timestamp_lapse.setText("{:<10} {} {} {}\n".format("Time lapse:", self.data.ts_data.init.strftime("%d/%m/%y %H:%M:%S"), "-" , self.data.ts_data.end.strftime("%H:%M:%S")))
		self.temperature_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.data.temperature.current, self.temperature_unit_name))
		self.humidity_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.humidity.current, self.humidity_unit_name))
		self.temperature_avg_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.data.temperature.average, self.temperature_unit_name))
		self.temperature_max_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.data.temperature.maximum, self.temperature_unit_name))
		self.temperature_min_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Temperatura:", self.data.temperature.minimum, self.temperature_unit_name))
		self.humidity_avg_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.humidity.average, self.humidity_unit_name))
		self.humidity_max_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.humidity.maximum, self.humidity_unit_name))
		self.humidity_min_label.setText("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.humidity.minimum, self.humidity_unit_name))
		self.temperature_alarm_threshold.setValidator(QIntValidator(temperature_range[self.temperature_unit_name][0],temperature_range[self.temperature_unit_name][1]))  
		self.temperature_unit_label.setText(self.temperature_unit_name)
		self.temp_threshold_spin.setRange(temperature_range[self.temperature_unit_name][0], temperature_range[self.temperature_unit_name][1])



	def container_init(self):
		widget_central = QWidget()

		container = QGridLayout()
		container.setContentsMargins(10, 7, 10, 7)

		self.checkbox = QCheckBox("°C")
		self.checkbox.stateChanged.connect(self.unit_change_checkbox)

		pixmap = QPixmap("misc/original.jpg")

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
		self.statistic_button.clicked.connect(self.stats_button_ui_manager)


		buttons_layout.addWidget(self.graphic_button)
		buttons_layout.addWidget(self.statistic_button)
		
		buttons_layout.setSpacing(40)

		
		buttons_container = QWidget()
		buttons_container.setLayout(buttons_layout)
		buttons_container.setStyleSheet("background-color: #a3c1da;") 


		data_layout = QGridLayout()
		
		self.temperature_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.data.temperature.current, self.temperature_unit_name))
		self.humidity_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.humidity.current, self.humidity_unit_name))


		avg_label = QLabel("Average")
		avg_label.setStyleSheet("padding-left: 8px; font-size: 12px")
		self.timestamp_lapse = QLabel("{:<10} {} {} {}\n".format("Time lapse:", self.data.ts_data.init.strftime("%d/%m/%y %H:%M:%S"), "-" , self.data.ts_data.init.strftime("%H:%M:%S")))
		self.temperature_avg_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.data.temperature.average, self.temperature_unit_name))
		self.humidity_avg_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.temperature.average, self.humidity_unit_name))

		max_label = QLabel("Highest Sample")
		max_label.setStyleSheet("padding-left: 8px")
		self.temperature_max_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.data.temperature.maximum, self.temperature_unit_name))
		self.humidity_max_label= QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.temperature.maximum, self.humidity_unit_name))

		min_label = QLabel("Lowest Sample")
		min_label.setStyleSheet("padding-left: 8px")
		self.temperature_min_label = QLabel("{:<10} {:>4.1f} {:<4}\n".format("Temperature:", self.data.temperature.minimum, self.temperature_unit_name))
		self.humidity_min_label =QLabel("{:<10} {:>4.1f} {:<4}\n".format("Humidity:", self.data.temperature.minimum, self.humidity_unit_name))

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

		self.temp_threshold_spin = QSpinBox()
		self.temp_threshold_spin.setRange(temperature_range[self.temperature_unit_name][0], temperature_range[self.temperature_unit_name][1])
		self.temp_threshold_spin.setValue(0)
		self.temp_threshold_spin.valueChanged.connect(self.update_ui_graphic_temp)

		self.humi_threshold_spin = QSpinBox()
		self.humi_threshold_spin.setRange(0, 100)
		self.humi_threshold_spin.setValue(0)
		self.humi_threshold_spin.valueChanged.connect(self.update_ui_graphic_humi)

		data_layout.addWidget(alarm_label, 10, 0, 1, 3)  
		data_layout.addWidget(temperature_name_label, 11, 0)  
		data_layout.addWidget(self.temp_threshold_spin, 11, 1)  
		data_layout.addWidget(self.temperature_unit_label, 11, 2)  
		
		data_layout.addWidget(humidity_name_label, 12, 0)  
		data_layout.addWidget(self.humi_threshold_spin, 12, 1)  
		data_layout.addWidget(humidity_unit_label, 12, 2)  
	   
		data_container = QWidget()
		data_container.setLayout(data_layout)

		container.addWidget(buttons_container, 6, 0, 1, 1)

		container.addWidget(self.canvas, 0, 0, 1, 1, Qt.AlignLeft)
		container.addWidget(self.etiqueta_imagen, 0, 0, 1, 1, Qt.AlignLeft)
		self.canvas.setVisible(False)

		container.addWidget(data_container, 0, 1, 1, 1, Qt.AlignRight)   
		container.addWidget(self.checkbox, 6, 1, 1, 2, Qt.AlignCenter)  

		widget_central.setLayout(container)

		self.setCentralWidget(widget_central)


app = QApplication([])

window = MainWindow()
window.show()

app.exec()

