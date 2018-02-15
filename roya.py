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
		arreglo = arregloFecha[-1].split()
		for i in arreglo:
			if i == time.strftime("%Y-%m-%d"):
				return (i)

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

class CreacionMapas:
	def Mapas(self, fecha):
		'''La siguiente funcion procesara y filtrara la informacion para 
		generar los respectivos mapas de los diferentes cambios climatologicos'''
		os.chdir('data/{}'.format(fecha))
		VariablesClima = ('Tpro','Dpoint','Noch_fres')
		for i in range(1, 3):
			print('Procesando la informacion del Documento d{}.txt'.format(i))
			data = pd.read_csv('d{}.txt'.format(i))
			for j in range(len(VariablesClima)):
				print('Procesando Mapa {} del {}'.format(VariablesClima[j], fecha))
				Tierra = data.loc[data['WprSoil10_40'] <= 99]
				x , y = 'Long', 'Lat' 
				Long = np.array(data['{}'.format(x)])
				Lat = np.array(data['{}'.format(y)])
				if i == 0:
					procesado = Tierra.loc[Tierra['{}'.format(VariablesClima[j])] >=25]
					procesado = procesado.loc[procesado['{}'.format(VariablesClima[j] <= 30)]]
				elif i == 1:
					procesado = Tierra.loc[Tierra['{}'.format(VariablesClima[j])] > 5]
				elif i == 2:
					procesado = Tierra.loc[(Tierra['Tmax'] - Tierra['Tmin']) >=15]
					procesado = Tierra.loc[(Tierra['Tmax'] - Tierra['Tmin']) <=20]

				Eje_x = np.array(procesado['{}'.format(x)])
				Eje_y = np.array(procesado['{}'.format(y)])

				map = Basemap(projection='mill',
								resolution='l',
								area_thresh=0.01,
								llcrnrlon=Long.min(), llcrnrlat=Lat.min(),
								urcrnrlon=Long.max(), urcrnrlat=Lat.max())
				x1, x2 = map(Eje_x, Eje_y)
				map.scatter(x1, x2, marker='.',color='#0000FF')
				os.chdir('../..')
				map.readshapefile('shapes/Estados','mill')
				od.chdir('data/{}'.format(fecha))
				plt.title('{} del {}'.format(VariablesClima[j], fecha))
				plt.savefig('{} del {}.png'.format(VariablesClima[j],fecha))

if __name__ == "__main__":
	fecha = Fecha().obtencionFecha()
	FehasArreglo = ArregloFecha().fechas(fecha)
	print('El proceso de descarga de archivo a empezado')
	print('Espera algunos minutos para que el proceso llegue a finalizar...')
	DescargarArchivos().descDocs(fecha)
	print('------------------------------')
	CreacionMapas().Mapas(fecha)