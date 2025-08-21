import sys
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QTimer, pyqtSignal

DEBUG = False

# Clase separada para manejo de base de datos
class DatabaseManager(QThread):
	data_updated = pyqtSignal(dict)
	new_data_arrived = pyqtSignal(bool)

	def __init__(self):
		super().__init__()
		self.connection = None
		self.current_id=0
		self.current_ts=0
		self.connect()


	def connect(self):
		try:
			self.connection = mysql.connector.connect(
				host='localhost',
				database='sensor_data',
				user='laptop',
				password='1234'
			)
			
			if self.connection and self.connection.is_connected():
				self.connection.autocommit = True
				print(f"Conectado a MySQL Server versión {self.connection.get_server_info()}")
				return True
			else:
				print("Fallo al conectar a la base de datos")
				return False
				
		except Error as e:
			print(f"Error al conectar a MySQL: {e}")
			self.connection = None
			return False
	
	def setup_polling(self, time=8000):
		self.timer = QTimer()
		self.timer.timeout.connect(self.check_for_new_data)
		self.timer.start(time)
	
	def get_latest_record(self, table_name='readings', date_column='id'):
		if not self.connection:
			return None
		
		try:
			cursor = self.connection.cursor()
			query = f"SELECT * FROM {table_name} ORDER BY {date_column} DESC LIMIT 1"
			cursor.execute(query)
			
			columns = [desc[0] for desc in cursor.description]
			record = cursor.fetchone()
			cursor.close()
			
			if record:
				return dict(zip(columns, record))
			return None
			
		except Error as e:
			print(f"Error al leer datos: {e}")
			return None
	
	def check_for_new_data(self):
		try:
			latest_data = self.get_latest_record('readings')
			
			if latest_data is None:
				return
			
			if DEBUG: 
				print("last data enquiried:\n", latest_data)
				
			if self.current_id is None:
				if DEBUG: 
					print("current_id is None! reasigning...")
				self.current_id = latest_data['id']
				# Emitir el primer dato
				self.data_updated.emit(latest_data)
				
			elif self.current_id < latest_data['id']:
				if DEBUG: 
					print("(current_id < data_id) New Data! reasigning...")
				self.current_id = latest_data['id']
				self.current_ts = latest_data['timestamp']
				
				# Emitir los nuevos datos
				self.data_updated.emit(latest_data)
				
			elif self.current_id == latest_data['id']:
				if DEBUG: 
					print("(current_id => data_id) No new Data")
			
			if DEBUG: 
				print("current id: ", self.current_id, "  current ts: ", self.current_ts)
				
		except Exception as e:
			print(f"Error al consultar datos: {e}")
	
	def stop(self):
		if self.timer:
			self.timer.stop()