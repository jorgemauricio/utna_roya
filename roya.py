from api import claves
import pandas as pd 
import ftplib 
import time 
import sys
import requests
import os
import shapefile 
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


class Login(): # Contiene las clases constructuras.
	def __init__(self):
		self.clv = claves()
		self.ftp = ftplib.FTP(self.clv.ip)
		self.ftp.login(self.clv.usr, self.clv.pwd)

class Fecha(Login):
	def __init__(self):
		super().__init__()

	def obtencionFecha(self): #Obtiene la fecha desde el FTP del Instituto
		try:
			arregloFecha = []
			self.ftp.dir(arregloFecha.append)
			arreglo = arregloFecha[-1].split()
			for i in arreglo:
				if i == time.strftime("%Y-%m-%d"):
					return (i)
		except ValueError:
			print('El servidor no a encontrado la fecha establecida')

class ArregloFecha():
	def fechas(self, fecha): #Genera un arreglo de 5 fechas subsecuentes a la fecha ingresada por parametro
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

	def descDocs(self, fecha): #Descarga los 5 archivos respectivos a la fecha ingresada por parametro
		self.ftp = ftplib.FTP(self.clv.ip)
		self.ftp.login(self.clv.usr, self.clv.pwd)
		self.ftp.cwd('{}'.format(fecha))
		try: 
			if os.path.exists('data'):
				os.chdir('data')
			else:
				os.mkdir('data')
				os.chdir('data')
			if os.path.exists('{}'.format(fecha)):
				os.chdir('{}'.format(fecha))
				for i in range(1, 6):
					print("La descarga del documento esta en proceso d{}.txt".format(i))
					self.ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write)
			else:
				os.mkdir('{}'.format(fecha))
				os.chdir('{}'.format(fecha))
				for i in range(1, 6):
					print("La descarga del documento esta en proceso d{}.txt".format(i))
					self.ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i), 'wb').write)
			self.ftp.quit()
			os.chdir('../..')
		except ValueError:
			print("No se a podido encontrar o crear la carpeta establecida")

class GenerarModelo():
	def Modelo(Tpro, Tmax, Tmin, Dpoint):
		if 


class DataFrame:
	def BaseDataFrame(self, fecha): #Funcion que genera un dataframe tomando las variables(Tmax, Tmin, Tpro y Dpoint)
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

class GeneracionIndice():
	def Indice(d1, d2, d3, d4, d5):
		if d1 == 1 and d2 == 1 and d3 == 1 and d4 == 1 and d5 == 1:
			return 10
		elif d1 == 0 and d2 == 1 and d3 == 1 and d4 == 1 and d5 == 1:
			return 9
		elif d1 == 1 and d2 == 1 and d3 == 1 and d4 == 1 and d5 == 0:
			return 8
		elif d1 == 1 and d2 == 1 and d3 == 1 and d4 == 0 and d5 == 0:
			return 7
		elif d1 == 0 and d2 == 1 and d3 == 1 and d4 == 1 and d5 == 0:
			return 6
		elif d1 == 0 and d2 == 0 and d3 == 1 and d4 == 1 and d5 == 1:
			return 5
		elif d1 == 1 and d2 == 1 and d3 == 0 and d4 == 0 and d5 == 0:

'''class GeneracionMapas():
	def Crea_Map(fecha):	#Funcion para la realizacion de mapas
		variables = ['Tpro','Dpoint', 'No_Fre']
		for i in variables:
			data = pd.read_csv('data/{}/d1.txt'.format(fecha))
			x = 'Long'
			y = 'Lat'
			Suelo = data.loc[data['WprSoil10_40'] <=99]
			Long = np.array(data['{}'.format(x)])
			Long_min = Long.min()
			Long_max = Long.max()
			Lat = np.array(data['{}'.format(y)])
			Lat_min = Lat.min()
			Lat_max = Lat.max()
			if i == 'Tpro':
				Var = Suelo.loc[Suelo['{}'.format(i)] >=25]
				Var = Var.loc[Suelo['{}'.format(i)] <=30]
			elif i == 'Dpoint':
				Var = Suelo.loc[Suelo['{}'.format(i)] >5]
			elif i == 'No_Fre':
				Var = Suelo.loc[(Suelo['Tmax'] - Suelo['Tmin']) >=15]
				Var = Suelo.loc[(Suelo['Tmax'] - Suelo['Tmin']) <=20]

			Eje_x = np.array(Var['{}'.format(x)])
			Eje_y = np.array(Var['{}'.format(y)])

			map = Basemap(projection = 'mill', 
				   resolution = 'l',
				   area_thresh = 0.01,
				   llcrnrlon = Long.min(), llcrnrlat = Lat.min(), 
				   urcrnrlon = Long.max(), urcrnrlat = Lat.max())
	        #map.drawcountries(color="gray")
			#map.fillcontinents(color='#CD5C5C', lake_color='#53BEFD')
			#map.drawmapboundary(color='black', linewidth=0.5, fill_color='#008080')

			x,y = map(Eje_x, Eje_y)
			map.scatter(x,y, marker='.', color='k')
			map.readshapefile("Estados", 'Mill')
			plt.savefig("mapas/{}_{}_d1.png".format(fecha, i))
			print ('Generando Mapa "{}_{}_d1.jpg"'.format(fecha, i))'''


	
if __name__ == "__main__":
	fecha = Fecha().obtencionFecha()
	print("Fecha Obtenida: {}".format(fecha))
	FehasArreglo = ArregloFecha().fechas(fecha)
	print("Fechas subsecuentes al dia actual: {}".format(FehasArreglo))
	DescargarArchivos().descDocs(fecha)
	#GeneracionMapas.Crea_Map(fecha)
	dataFrame = DataFrame().BaseDataFrame(fecha)
print(dataFrame.head(2))
	
	