#from mpl_toolkits.basemap import Basemap
#import matplotlib.pyplot as plt
from api import claves
import pandas as pd 
import numpy as np
import shapefile 
import ftplib 
import time
import sys
import os
listaParametros = [25,30,5]

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

class Menu:
	'''Muestra un menu y responde a la eleccion seleccionada por el usuario'''
	def __init__(self):
		self.elecciones = {
			"1": self.IngresarPara,
			"2": self.Default,
			"3": self.salir
		}

	def MostrarMenu(self):
		'''Menu de la aplicacion ROYA'''
		print("""\tMenu Roya
1 Ingresar rangos a las variables de clima
2 Enviar variables por default
3 Cancelar y salir. """)

	def run(self):
		'''Muestra el menu y responde a la eleccion.'''
		self.MostrarMenu()
		eleccion = input("Selecciona la opcion: ")
		accion = self.elecciones.get(eleccion)
		if(accion):
			accion()
		else:
			print("{} no es una eleccion valida".format(eleccion))

	def IngresarPara(self):
		TproMin = int(input("Temperatura promedio Minima: "))
		TproMax = int(input("Temperatura promedio Maxima: "))
		Dpoint = int(input("Dpoint: "))
		listaParametros[0] = TproMin
		listaParametros[1] = TproMax
		listaParametros[2] = Dpoint

	def Default(self):
		pass

	def salir(self):
		print("Gracias por usar la aplicacion ROYA")
		sys.exit(0)

class DataFrame:
	def BaseDataFrame(self, fecha):
		'''Genera un DataFrame uniendo las variables (Tmax, Tmin, Tpro, Dpoint)
		de los 5 archivos descargados desde el ftp'''
		os.chdir('data/{}'.format(fecha))
		for i in range(1, 6):
			data = pd.read_csv("d{}.txt".format(i))
			if i == 1:
				df = data[['Long','Lat','WprSoil10_40']]
			if i > 0:
				df['Tpro{}'.format(i)] = data['Tpro']
				df['NocFres{}'.format(i)] = (data['Tmax']-data['Tmin'])
				df['Dpoint{}'.format(i)] = data['Dpoint']				
		return df 

	def FiltarInformacion(self, dataFrame):
		for i in range(1,6):
			x, y = 'Long', 'Lat'
			Long = np.array(dataFrame['{}'.format(x)])
			Lat = np.array(dataFrame['{}'.format(y)])
			Mexico = dataFrame.loc[dataFrame['WprSoil10_40'] <= 99]
			Mexico = Mexico.loc[Mexico['Tpro{}'.format(i)] >= listaParametros[0]]
			Mexico = Mexico.loc[Mexico['Tpro{}'.format(i)] <= listaParametros[1]]
			Mexico = Mexico.loc[Mexico['Dpoint{}'.format(i)] > listaParametros[2]]
			Mexico = Mexico.loc[(Mexico['Tmax{}'.format(i)] - Mexico['Tmin{}'.format(i)])]

if __name__ == "__main__":
	fecha = Fecha().obtencionFecha()
	FehasArreglo = ArregloFecha().fechas(fecha)
	print('El proceso de descarga de archivo a empezado')
	print('Espera algunos minutos para que el proceso llegue a finalizar...')
	DescargarArchivos().descDocs(fecha)
	print("*"*40)
	Menu().run()
	dataFrame = DataFrame().BaseDataFrame(fecha)
	print(dataFrame.head(2))