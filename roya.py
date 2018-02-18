from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from api import claves
import pandas as pd 
import numpy as np
import shapefile 
import ftplib 
import time
import sys
import os

class Login():
	'''Clase constructura.'''
	def __init__(self):
		self.clv = claves()
		self.ftp = ftplib.FTP(self.clv.ip)
		self.ftp.login(self.clv.usr, self.clv.pwd)

class Fecha(Login):
	def __init__(self):
		super().__init__()

	def obtencionFecha(self):
		'''Obtiene la fecha desde el FTP del Instituto'''
		arregloFecha = []
		self.ftp.dir(arregloFecha.append)
		a = -1
		while(True):
			arreglo = arregloFecha[a].split()
			for i in arreglo:
				if i == time.strftime("%Y-%m-%d"):
					return (i)
			a -= 1

class ArregloFecha():
	def fechas(self, fecha):
		'''Genera un arreglo de 5 fechas subsecuentes 
		a la fecha ingresada por parametro'''
		ano, mes, dia = (int(arreglo) for arreglo in fecha.split('-'))
		if mes in (1 , 3, 5, 7, 8, 10, 12):
			dias_mes = 31
		elif mes == 2:
			if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
				dias_mes = 29
			else:
				dias_mes = 28
		elif mes in (4, 6, 9, 11):
			dias_mes = 30
		dias = []
		for i in range(5):
			if dia + i <= dias_mes:
				dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes, dia + i))
			else:
				if mes != 12:
					dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes+1, i - (dias_mes - dia)))
				else:
					dias.append('{:04d}-01-{:02d}'.format(ano+1, i - (dias_mes - dia)))
		return dias

class DescargarArchivos(Login):
	def __init__(self):
		super().__init__()

	def descDocs(self, fecha):
		'''Descargar los 5 archivos respectivo a la fecha
		ingresada por parametro'''
		self.ftp = ftplib.FTP(self.clv.ip)
		self.ftp.login(self.clv.usr, self.clv.pwd)
		self.ftp.cwd('{}'.format(fecha))
		if os.path.exists('data'):
			os.chdir('data')
		else:
			os.mkdir('data')
			os.chdir('data')
		if os.path.exists('{}'.format(fecha)):
			os.chdir('{}'.format(fecha))
			for i in range(1, 6):
				print("Descargando el Archivo d{}.txt".format(i))
				self.ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write)
		else:
			os.mkdir('{}'.format(fecha))
			os.chdir('{}'.format(fecha))
			for i in range(1, 6):
				print("Descargando el Archivo d{}.txt".format(i))
				self.ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i), 'wb').write)
		self.ftp.quit()
		os.chdir('../..')

class DataFrame:
	def BaseDataFrame(self, fecha):
		'''Genera un DataFrame uniendo las variables (Tmax, Tmin, Tpro, Dpoint)
		de los 5 archivos descargados desde el ftp'''
		os.chdir('data/{}'.format(fecha))
		for i in range(1, 6):
			data = pd.read_csv("d{}.txt".format(i))
			if i == 1:
				df = data[['Long','Lat',]]
				df = (df.assign(Tmax1 = data['Tmax']))
				df = (df.assign(Tmin1 = data['Tmin']))
				df = (df.assign(Tpro1 = data['Tpro']))
				df = (df.assign(Dpoint1 = data['Dpoint']))
			elif i == 2:
				df = (df.assign(Tmax2 = data['Tmax']))
				df = (df.assign(Tmin2 = data['Tmin']))
				df = (df.assign(Tpro2 = data['Tpro']))
				df = (df.assign(Dpoint2 = data['Dpoint']))
			elif i == 3:
				df = (df.assign(Tmax3 = data['Tmax']))
				df = (df.assign(Tmin3 = data['Tmin']))
				df = (df.assign(Tpro3 = data['Tpro']))
				df = (df.assign(Dpoint3 = data['Dpoint']))
			elif i == 4:
				df = (df.assign(Tmax4 = data['Tmax']))
				df = (df.assign(Tmin4 = data['Tmin']))
				df = (df.assign(Tpro4 = data['Tpro']))
				df = (df.assign(Dpoint4 = data['Dpoint']))
			elif i == 5:
				df = (df.assign(Tmax5 = data['Tmax']))
				df = (df.assign(Tmin5 = data['Tmin']))
				df = (df.assign(Tpro5 = data['Tpro']))
				df = (df.assign(Dpoint5 = data['Dpoint']))
		return df


if __name__ == "__main__":
	fecha = Fecha().obtencionFecha()
	FehasArreglo = ArregloFecha().fechas(fecha)
	print('El proceso de descarga de archivo a empezado')
	print('Espera algunos minutos para que el proceso llegue a finalizar...')
	DescargarArchivos().descDocs(fecha)
	print('------------------------------')
	dataFrame = DataFrame().BaseDataFrame(fecha)
	print(dataFrame.head(2))