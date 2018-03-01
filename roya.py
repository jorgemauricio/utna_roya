from api import claves 
from ftplib import FTP #Libreria utilizada para conectarse a un servidor FTP y obtener informacion
import os #Libreria utilizada para crear carpetas de almacenamiento
import pandas as pd #Libreria utilizada para leer los documentos (csv)
import numpy as np #Libreria utilizada para generar arreglos
import matplotlib.pyplot as plt #Libreria utilizada para la generacion de los mapas
from mpl_toolkits.basemap import Basemap #Libreria utilizada para establecer las coordenadas del mapa
import shapefile #Libreria utilizada para leer los shapes

def main():
    fecha = '2018-02-14'
    cve = claves()
    #fecha = obt_fecha(cve)
    cincodias = cinco_dias(fecha)
    #desc_docs(fecha,cve)
    df = data_frame(fecha)
    mapa_tot(df,fecha,cincodias)

def obt_fecha(cve): #Obtener la fecha actual
    fecha = []
    try:
        ftp = FTP(cve.ip) #Nombre del servidor
        ftp.login(cve.usr, cve.pwd) #Usuario y contrasena del servidor
        ftp.dir(fecha.append) #Se almacena toda la informacion que se encuentra en el directorio actual dentro del arreglo
        fecha = fecha[-1].split()[-1] #Se toma el ultimo valor del arreglo, se separa la cadena en un arreglo dividido por espacios y se toma el ultimo valor.
        print ('Conexion realizada y fecha obtenida "{}"'.format(fecha))
        return fecha # Se devuelve el valor obtenido (la fecha)
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
    return dias #Develve la lista de los 5 dias

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

def roya(Tpro,Dpoint,Noch_fres): #Funcion utilizada para devolver valores de 1/0 el lugar de Verdadero/Falso, en una declaracion posterior
    if Tpro >= 25 and Tpro <=30 and Dpoint > 5 and Noch_fres >= 15 and Noch_fres <=20: #Filtrado de datos donde se presenta la ROYA
        return 1
    else:
        return 0

def data_frame(fecha): #Generacion de un DataFrame
    df = pd.DataFrame() #Declaracion del DataFrame
    for i in range (1, 6): #Ciclo donde se prosesan los 5 documentos
        datos = pd.read_csv('datos/{}/d{}.txt'.format(fecha, i)) #Almacenar dato correspondiente en datos
        #Se almacena cada una de las variables a utilizar
        df['Tpro{}'.format(i)] = datos['Tpro'.format(i)] 
        df['Noch_fres{}'.format(i)] = (datos['Tmax'.format(i)] - datos['Tmin'.format(i)])
        df['Dpoint{}'.format(i)] = datos['Dpoint'.format(i)]
        #Estas variables solo se declaran para agregarlas al final del ciclo, ya que agregarlas 5 veces seria redundante porque tienen los
        #mismos valores
        Long, Lat, WprSoil10_40 = datos['Long'], datos['Lat'], datos['WprSoil10_40']
    df['Long'], df['Lat'] ,df['WprSoil10_40'] = Long, Lat, WprSoil10_40
    variables = ['Tpro','Dpoint','Noch_fres'] #Lista con las variables a utilizar
    for j in range (1,6): #Cliclo utilizado para crear 5 columnas (1 por cada filtro de variables), utilizando la funcion "roya" para determinar que filas cumplen las condiciones
        df['d{}'.format(j)] = df.apply(lambda x:roya(x['{}{}'.format(variables[0],j)],x['{}{}'.format(variables[1],j)],x['{}{}'.format(variables[2],j)]),axis=1)
    return df #Devuelve el DataFrame

def mapa_tot(df, fecha, cincodias): #Generacion del Pronostico de ROYA en los 5 fias
    if os.path.exists('mapas'): #Verifica si la carpeta mapas existe (donde se almacenaran los documentos a descargar)
        os.chdir('mapas') #Accede a la carpeta mapas
    else:
        os.mkdir('mapas') #Crea la carpeta mapas
        os.chdir('mapas') #Accede a la carpeta mapas
    if os.path.exists('{}'.format(fecha)): #Verificar si la carpeta fecha existe que es donde se almacenaran los mapas
        os.chdir('{}'.format(fecha)) #Ingresar a la carpeta fecha
    else:
        os.mkdir('{}'.format(fecha)) #Crea la carpeta fecha donde se almacenaran los documentos
        os.chdir('{}'.format(fecha)) #Ingresar a la carpeta fecha
    colores = ['#00FF00','#FFFF00','#FF8000','#FF0000','#000000']
    Tierra = df.loc[df['WprSoil10_40'] <= 99]
    Long= np.array(df['Long'])
    Long_min, Long_max = Long.min(), Long.max()
    Lat= np.array(df['Lat'])
    Lat_min, Lat_max = Lat.min(), Lat.max() 
    for i in range (1, 6):
        map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), urcrnrlon=Long.max(), urcrnrlat=Lat.max())
        var = df.loc[df['d{}'.format(i)]==1]
        Eje_x, Eje_y = np.array(var['Long']), np.array(var['Lat'])
        x, y = map(Eje_x, Eje_y)
        map.scatter(x, y, marker='.',color='{}'.format(colores[i-1]),s=1)
        map.readshapefile("../../shapes/Estados", 'Mill')
        print ('Generando mapa de Pronostico de ROYA de {} ...'.format(cincodias[i-1]))
        plt.title('Pronostico de ROYA \n De {}'.format(cincodias[i-1]))
        plt.savefig("Pronostico_ROYA_{}.png".format(cincodias[i-1]))
    map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), urcrnrlon=Long.max(), urcrnrlat=Lat.max())
    for i in range (2, 6):
        var = df.loc[(df['d1']+df['d2']+df['d3']+df['d4']+df['d5'])==i]
        Eje_x, Eje_y = np.array(var['Long']), np.array(var['Lat'])
        x, y = map(Eje_x, Eje_y)
        map.scatter(x, y, marker='.',color='{}'.format(colores[i-2]),s=1)
        #map.contourf(x, y, z, color='{}'.format(colores[i-2]))
    map.readshapefile("../../shapes/Estados", 'Mill')
    print ('Generando mapa de Pronostico de ROYA de {} a {} ...'.format(cincodias[0], cincodias[4]))
    plt.title('Pronostico de ROYA \n De {} a {}'.format(cincodias[0], cincodias[4]))
    plt.savefig("Pronostico_ROYA_{}_a_{}.png".format(cincodias[0], cincodias[4]))
    os.chdir('../..') #Sale de la carpeta con la fecha/datos al directorio raiz

if __name__=="__main__":
    main()
