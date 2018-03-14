from scipy.interpolate import griddata as gd
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
#Variables Globales 
colores = ['#00FF00','#00FF00','#00FF00','#00FF00','#FFFF00','#FFFF00','#FFFF00','#FF8000','#FF8000','#FF0000']
rangos = ('00011', '00110', '01100', '11000', '00111', '01110', '11100', '01111', '11110', '11111')
grado = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
var = ['Tpro', 'Dpoint', 'NocFres']
Rango = [25,30,5,15,20]
lista = []

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

	def descarga(self):
		'''Metodo para descar los 5 dias respectivo a la fecha 
		ingresada por parametro'''
		self.ftp = ftplib.FTP(self.clv.ip)
		self.ftp.login(self.clv.usr, self.clv.pwd)
		self.ftp.cwd('{}'.format(fecha))
		for i in range(1, 6):
			print("Descargando el Archivo d{}.txt".format(i))
			self.ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write)
		self.ftp.quit()

	def descDocs(self, fecha):
		'''Descargar los 5 archivos respectivo a la fecha
		ingresada por parametro'''
		if os.path.exists('data'):
			os.chdir('data')
		else:
			os.mkdir('data')
			os.chdir('data')
		if os.path.exists('{}'.format(fecha)):
			os.chdir('{}'.format(fecha))
			DescargarArchivos().descarga()
		else:
			os.mkdir('{}'.format(fecha))
			os.chdir('{}'.format(fecha))
			DescargarArchivos().descarga()
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
		op = 1
		while(op != 2):
			eleccion = input("Selecciona la opcion: ")
			accion = self.elecciones.get(eleccion)
			if(accion):
				accion()
				op += 1
			else:
				print("{} no es una eleccion valida".format(eleccion))

	def IngresarPara(self):
		validar = 0
		while (validar != 1):
			try:
				lista.append(int(input("Temperatura promedio Minima: ")))
				validar += 1
			except ValueError:
				print("Ingresa solo numeros")
		while (validar != 2):
			try:
				lista.append(int(input("Temperatura promedio Maxima: ")))
				validar += 1
			except ValueError:
				print("Ingresa solo numeros")
		while (validar != 3):
			try:
				lista.append(int(input("Dpoint: ")))
				validar += 1
			except ValueError:
				print("Ingresa soo numeros")
		for i in range(0, 3):
			Rango[i] = lista[i]

	def Default(self):
		pass

	def salir(self):
		print("Gracias por usar la aplicacion ROYA")
		sys.exit(0)

class DataFrame:
	def roya(self, Tpro, Dpoint, NocFres):
		'''Metodo para la generacion de valo 1 o 0 de cada fila del DataFrame,
		Y poder pronosticar si la enfermedad roya se presenta en el dia'''
		if (Tpro >= Rango[0] and Tpro <= Rango[1]  and Dpoint > Rango[2] and NocFres >= Rango[3] and NocFres <= Rango[4]):
			return '1'
		else:
			return '0'

	def indice(self, d1, d2, d3, d4, d5):
		'''Metodo que evalua el grado de'''
		rango = '{}{}{}{}{}'.format(d1,d2,d3,d4,d5)
		if rango in rangos:
			for i in range(0, len(rangos)):
				if rangos[i] == rango:
					indice = rangos.index(rangos[i])
					return grado[indice]
		else:
			return 0

	def BaseDataFrame(self, fecha):
		'''Genera un DataFrame uniendo las variables (Tmax, Tmin, Tpro, Dpoint)
		de los 5 archivos descargados desde el ftp'''
		os.chdir('data/{}'.format(fecha))
		print('El proceso de creacion de DataFrame a comenzado espera unos segundos...')
		df = pd.DataFrame()
		for i in range(1, 6):
			data = pd.read_csv("d{}.txt".format(i))
			if i == 1:
				df['Lat'] = data['Lat']
				df['Long'] = data['Long']
				df['WprSoil10_40'] = data['WprSoil10_40']
			df['Tpro{}'.format(i)] = data['Tpro']
			df['NocFres{}'.format(i)] = (data['Tmax']-data['Tmin'])
			df['Dpoint{}'.format(i)] = data['Dpoint']
		df = df.loc[df['WprSoil10_40'] <= 99]
		for j in range(1,6):
			df['d{}'.format(j)] = df.apply(lambda x:DataFrame().roya(x['{}{}'.format(var[0],j)],
				x['{}{}'.format(var[1],j)],x['{}{}'.format(var[2],j)]),axis=1)
		df['Indice'] = df.apply(lambda x: DataFrame().indice(x['d1'], x['d2'], x['d3'], x['d4'], x['d5']), axis=1)
		os.chdir('../..')
		return df

class Mapas:
	def GenerarMapas(self, df, fecha, FehasArreglo):
		if os.path.exists('mapas'):
			os.chdir('mapas')
		else:
			os.mkdir('mapas')
			os.chdir('mapas')
		if os.path.exists('{}'.format(fecha)):
			os.chdir('{}'.format(fecha))
		else:
			os.mkdir('{}'.format(fecha))
			os.chdir('{}'.format(fecha))
		Long = np.array(df['Long'])
		Lat = np.array(df['Lat'])
		for i in range (1, 7):
			map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), 
				urcrnrlon=Long.max(), urcrnrlat=Lat.max())
			if (i > 0 and i < 6):
				roya = df.loc[df['d{}'.format(i)]=='1']
				x, y = map(np.array(roya['Long']), np.array(roya['Lat']))
				map.scatter(x, y, marker='.', color='green', s=1)
				map.readshapefile('../../shapes/Estados', 'Mill')
				print('Generando mapa del dia {}'.format(FehasArreglo[i-1]))
				plt.title('Pronostico de ROYA \n del {}'.format(FehasArreglo[i-1]))
				plt.savefig('Pronostico de ROYA del {}.png'.format(FehasArreglo[i-1]), dpi=300)
			if (i == 6):
				roya = df.loc[df['d1']=='1']
				x, y = map(np.array(roya['Long']), np.array(roya['Lat'])) 
				numCols = len(x)
				numRows = len(y)
				xi = np.linspace(x.min(), x.max(), numCols)
				yi = np.linspace(y.min(), y.max(), numRows)
				xi, yi = np.meshgrid(xi, yi)
				z = np.array(roya['Indice'])
				zi = gd((x,y), z, (xi, yi), method='cubic')
				cs = map.contourf(xi, yi, zi, grado, cmap='RdYlGn_r')
				map.colorbar(cs)
				map.readshapefile('../../shapes/Estados', 'Mill')
				print('Generando mapa de los 5 Dias')
				plt.title('Pronostico de ROYA General')
				plt.savefig('Pronostico de ROYA General.png', dpi=300)
			plt.clf()

if __name__ == "__main__":
	fecha = Fecha().obtencionFecha()
	FehasArreglo = ArregloFecha().fechas(fecha)
	print('El proceso de descarga de archivo a empezado')
	print('Espera algunos minutos para que el proceso llegue a finalizar...')
	DescargarArchivos().descDocs(fecha)
	print("*"*40)
	Menu().run()
	df = DataFrame().BaseDataFrame(fecha)
	Mapas().GenerarMapas(df,fecha,FehasArreglo)