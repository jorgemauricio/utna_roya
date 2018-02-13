from api import claves
from ftplib import FTP #Libreria utilizada para conectarse a un servidor FTP y obtener informacion
import os #Libreria utilizada para crear carpetas de almacenamiento
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import shapefile

def main():
    fecha = '2018-02-09'
    cve = claves()
    fecha = obt_fecha(cve)
    cinco_dias(fecha)
    desc_docs(fecha,cve)
        

def obt_fecha(cve): #Obtener la fecha actual
    fecha = []
    try:
        ftp = FTP(cve.ip) #Nombre del servidor
        ftp.login(cve.usr, cve.pwd) #Usuario y contrasena del servidor
        ftp.dir(fecha.append) #Se almacena toda la informacion que se encuentra en el directorio actual dentro del arreglo
        fecha = fecha[-1].split()[-1] #Se toma el ultimo valor del arreglo, se separa la cadena en un arreglo dividido por espacios y se toma el ultimo valor.
        print ('Conexion realizada y fecha obtenida "{}"'.format(fecha))
        return fecha # Se devuelve el valor obtenido
    except ValueError:
        print ('Error de conexion')
        return fecha

def cinco_dias(fecha): #Obtener cuatro dias posteriores a la fecha obtenida
    ano, mes, dia = (int(n) for n in fecha.split("-")) #Almacenamos cada dato correspondiente dividiendolo por un (-)
    if mes in (1, 3, 5, 7, 8, 10, 12): #Validacion de fecha
        dias_mes = 31
    elif mes == 2:
        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0): #Si el mes se visiesto
            dias_mes = 29
        else:
            dias_mes = 28
    elif mes in (4, 6, 9, 11):
        dias_mes = 30
    dias = []
    for n in range(0, 5): #Ciclo utilizado para almacenar los 5 dias
        if dia + n <= dias_mes:
            dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes, dia + n)) #'{:04d}-{:02d}-{:02d}' - Formato para la fecha
        else:                                                               #Agrega un sero en el caso de los nuemros unicos entre 1 - 9
            if mes != 12:
                dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes+1, n - (dias_mes - dia)))
            else:
                dias.append('{:04d}-01-{:02d}'.format(ano + 1, n - (dias_mes - dia)))
    return dias

def desc_docs(fecha, cve): #Descargar los documentos de la carpeta con el nombre de la fecha actual
    ftp = FTP(cve.ip); #Nombre del servidor
    ftp.login(cve.usr, cve.pwd) #Usuario y contrasena del servidor
    ftp.cwd('{}'.format(fecha)) #Infresa a una carpeta dentro del servidor
    if os.path.exists('datos'): #Verifica si la carpeta datos existe (donde se almacenaran los documentos a descargar)
        os.chdir('datos') #Accede a la carpeta datos
    else:
        os.mkdir('datos') #Crea la carpeta datos
        os.chdir('datos') #Accede a la carpeta datos
    if os.path.exists('{}'.format(fecha)): #Verificar si la carpeta fecha existe que es donde se almacenaran los datos
        os.chdir('{}'.format(fecha)) #Ingresar a la carpeta fecha
    else:
        os.mkdir('{}'.format(fecha)) #Crea la carpeta fecha donde se almacenaran los documentos
        os.chdir('{}'.format(fecha)) #Ingresar a la carpeta fecha
    for i in range(1, 6): #Ciclo que realiza 5 veces el proceso incrementando su valor en 1
        print ('Descargando archivo d{}.txt, de la fecha {} ...'.format(i, fecha))
        ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write) #Descarga los documentos
    ftp.quit()
    os.chdir('../..') #Sale de la carpeta con la fecha/datos al directorio raiz

def crear_mapas (fecha):
    if os.path.exists('mapas'):
        os.chdir('mapas')
    else:
        os.mkdir('mapas')
        os.chdir('mapas')
    os.chdir('..')
    datos = pd.read_csv('datos/{}}/d1.txt'.format(fecha))
    Tierra = datos.loc[datos['WprSoil10_40'] <= 99]
    T_pro = Tierra.loc[Tierra['Tpro'] >=25]
    T_pro = T_pro.loc[T_pro['Tpro'] <=30]
    Eje_x = np.array(T_pro['Long'])
    Eje_y = np.array(T_pro['Lat'])
    Long= np.array(datos['Long'])
    Long_min=Long.min()
    Long_max=Long.max()
    Lat= np.array(datos['Lat'])
    Lat_min=Lat.min()
    Lat_max=Lat.max() 
    map = Basemap(projection='mill',
              resolution='c',
              llcrnrlon=Long.min(), llcrnrlat=Lat.min(),
              urcrnrlon=Long.max(), urcrnrlat=Lat.max())
    x, y = map(Eje_x, Eje_y)
    map.scatter(x, y, marker='.',color='#0000FF')
    map.readshapefile("shapes/Estados", 'Mill')


if __name__=="__main__":
    main()
