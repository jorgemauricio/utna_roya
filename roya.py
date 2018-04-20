from scipy.interpolate import griddata as gd
from mpl_toolkits.basemap import Basemap #Libreria utilizada para la visualizacion de los datos y la generacion de los mapas 
import matplotlib.pyplot as plt #Libreria utilizada para la visualizacion de los datos y la generacion de los mapas 
from api import claves #Modulo que contiene datos confidenciales
import pandas as pd #Libreria utilizada para la manipulacion de los documentos
import numpy as np #Libreria utilizada para generar arreglos
import shapefile #Libreria utilizada para leer los shapes
import ftplib #Libreria utilizada para conectarse a un servidor FTP 
import time
import os #Libreria utilizada para crear carpetas de almacenamiento

rangos = ('00011', '00110', '01100', '11000', '00111', '01110', '11100', '01111', '11110', '11111') # Lista de rangos 
grado = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) #Lista de grados asociados a los rangos
var = ('Tpro','Dpoint','Tmax','Tmin') #Lista con las variables a utilizar

def main():
    cve = claves()
    fecha = obt_fecha(cve)
    cincodias = cinco_dias(fecha)
    desc_docs(fecha,cve)
    df = data_frame(fecha)
    gen_mapas(df, fecha, cincodias)

def obt_fecha(cve): #Obtiene la fecha actual
    fecha = []
    ftp = ftplib.FTP(cve.ip) #Nombre del servidor
    ftp.login(cve.usr, cve.pwd) #Usuario y contrasena del servidor
    ftp.dir(fecha.append) #Se almacena toda la informacion que se encuentra en el directorio actual dentro del arreglo
    fecha = fecha[-1].split()[-1] #Se toma el ultimo valor del arreglo, se separa la cadena en un arreglo dividido por espacios y se toma el ultimo valor.
    print ('Conexion realizada y fecha obtenida "{}".\n'.format(fecha))
    return fecha # Se devuelve el valor obtenido (la fecha)

def modelo(Tpro,Dpoint,Tmax,Tmin): #Funcion utilizada para devolver valores de 1/0 el lugar de Verdadero/Falso, en una declaracion posterior
    if Tpro >= 25 and Tpro <=30 and Dpoint > 5 and (Tmax-Tmin) >= 15 and (Tmax-Tmin) <=20:  #Filtrado de datos donde se presenta la ROYA
        return '1'
    else:
        return '0'

def indice(d1,d2,d3,d4,d5): #Funcion utilizada para generar un indice que determinara el grado de impacto de la ROYA en base al modelo
    rango = '{}{}{}{}{}'.format(d1,d2,d3,d4,d5)
    if rango in rangos:
        for i in range(0, len(rangos)):
            if rangos[i] == rango:
                ubic = rangos.index(rangos[i])
                return grado[ubic]
    else:
        return 0

def cinco_dias(fecha): #Obtener cuatro dias posteriores a la fecha obtenida
    ano, mes, dia = (int(i) for i in fecha.split("-")) #Almacenamos cada dato correspondiente dividiendolo por un (-)
    if mes in (1, 3, 5, 7, 8, 10, 12): #Validacion de fecha
        dias_mes = 31
    elif mes == 2:
        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0): #Si el mes se visiesto
            dias_mes = 29
        else:
            dias_mes = 28
    elif mes in (4, 6, 9, 11):
        dias_mes = 30
    cincodias = []
    for n in range(0, 5): #Ciclo utilizado para almacenar los 5 dias
        if dia + n <= dias_mes:
            cincodias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes, dia + n)) #'{:04d}-{:02d}-{:02d}' - Formato para la fecha
        else:                                                               #Agrega un sero en el caso de los nuemros unicos entre 1 - 9
            if mes != 12:
                cincodias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes+1, n - (dias_mes - dia)))
            else:
                cincodias.append('{:04d}-01-{:02d}'.format(ano + 1, n - (dias_mes - dia)))
    print('Lista de 5 dias generada: {}.\n'.format(cincodias))
    return cincodias #Develve la lista de los 5 dias

def desc_docs(fecha, cve): #Descarga los documentos de la carpeta con el nombre de la fecha actual
    ftp = ftplib.FTP(cve.ip); #Nombre del servidor
    ftp.login(cve.usr, cve.pwd) #Usuario y contrasena del servidor
    ftp.cwd('{}'.format(fecha)) #Infresa a una carpeta dentro del servidor
    if not os.path.exists('datos'): #Verifica si la carpeta datos existe (donde se almacenaran los documentos a descargar)
        os.mkdir('datos') #Crea la carpeta datos
    os.chdir('datos') #Accede a la carpeta datos
    if not os.path.exists('{}'.format(fecha)): #Verificar si la carpeta fecha existe que es donde se almacenaran los datos
        os.mkdir('{}'.format(fecha)) #Crea la carpeta fecha donde se almacenaran los documentos
    os.chdir('{}'.format(fecha)) #Ingresar a la carpeta fecha
    for i in range(1, 6): #Ciclo que realiza 5 veces el proceso incrementando su valor en 1
        print ('Descargando archivo d{}.txt, de la fecha {} ...'.format(i, fecha))
        #ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write) #Descarga los documentos
    ftp.quit()
    os.chdir('../..') #Sale de la carpeta con la fecha/datos al directorio raiz

def data_frame(fecha): #Generacion de un DataFrame con las variables a utilizr, al igual que 5 columnas para la deteccion de ROYA y un indice de impacto
    df = pd.DataFrame() #Declaracion del DataFrame
    print ('\nGenerando DataFrame ...')
    for i in range (1, 6): #Ciclo donde se prosesan los 5 documentos
        datos = pd.read_csv('datos/{}/d{}.txt'.format(fecha, i))  #Almacenar dato correspondiente en datos
        for j in var: #Ciclo para almacenar las variables de cada dia respectivamente
            df['{}{}'.format(j,i)] = datos[j] 
        #Estas variables solo se declaran para agregarlas al final del ciclo, ya que agregarlas 5 veces seria redundante porque tienen los mismos valores
        Long, Lat, WprSoil10_40 = datos['Long'], datos['Lat'], datos['WprSoil10_40']
    df['Long'], df['Lat'] ,df['WprSoil10_40'] = Long, Lat, WprSoil10_40
    df = df.loc[df['WprSoil10_40'] <= 99] #Filtrado para solo mapear en el area de Tierra
    for i in range (1,6): #Ciclo para generar cinco columnas una para cada dia, usando la funcion de validacion del modelo 
        df['d{}'.format(i)] = df.apply(lambda x:modelo(x['{}{}'.format(var[0],i)],x['{}{}'.format(var[1],i)],x['{}{}'.format(var[2],i)],x['{}{}'.format(var[3],i)]),axis=1)
    df['indice'] = df.apply(lambda x:indice(x['d1'],x['d2'],x['d3'],x['d4'],x['d5']),axis=1)
    print ('DataFrame generado.\n')
    return df #Devielve el DataFrame generado

def gen_mapas(df, fecha, cincodias): #Genera 5 mapas de cada respectivo dia, y uno del pronostico de los 5 dias
    if not os.path.exists('mapas'): #Verifica si la carpeta mapas existe (donde se almacenaran los documentos a descargar)
        os.mkdir('mapas') #Crea la carpeta mapas
    os.chdir('mapas') #Accede a la carpeta mapas
    if not os.path.exists('{}'.format(fecha)): #Verificar si la carpeta fecha existe que es donde se almacenaran los mapas
        os.mkdir('{}'.format(fecha)) #Crea la carpeta fecha donde se almacenaran los documentos
    os.chdir('{}'.format(fecha)) #Ingresar a la carpeta fecha
    Long = np.array(df['Long'])
    Lat = np.array(df['Lat'])
    for i in range (1, 7):
        map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), urcrnrlon=Long.max(), urcrnrlat=Lat.max())
        if (i > 0 and i < 6):
            roya = df.loc[df['d{}'.format(i)]=='1']
            x, y = map(np.array(roya['Long']), np.array(roya['Lat']))
            map.scatter(x, y, marker='.', color='green', s=1)
            map.readshapefile('../../shapes/Estados', 'Mill')
            print('Generando mapa del dia {} ...'.format(cincodias[i-1]))
            plt.title('Pronostico de ROYA \n del {}'.format(cincodias[i-1]))
            plt.savefig('Pronostico_de_ROYA_del_{}.png'.format(cincodias[i-1]), dpi=300)
        if (i == 6):
            roya = df.loc[df['indice']>1]
            x, y = map(np.array(roya['Long']), np.array(roya['Lat'])) 
            numCols = len(x)
            numRows = len(y)
            xi = np.linspace(x.min(), x.max(), numCols)
            yi = np.linspace(y.min(), y.max(), numRows)
            xi, yi = np.meshgrid(xi, yi)
            z = np.array(roya['indice'])
            zi = gd((x,y), z, (xi, yi), method='cubic')
            cs = map.contourf(xi, yi, zi, grado, cmap='RdYlGn_r')
            map.colorbar(cs)
            map.readshapefile('../../shapes/Estados', 'Mill')
            print('\nGenerando mapa del pronostico del {} al {} ...'.format(cincodias[0], cincodias[4]))
            plt.title('Pronostico de ROYA del {} al {}'.format(cincodias[0], cincodias[4]))
            plt.savefig('Pronostico_de_ROYA_del_{}_al_{}.png'.format(cincodias[0], cincodias[4]), dpi=300)
        plt.clf()
    os.chdir('../..') #Sale de la carpeta con la fecha/datos al directorio raiz

if __name__=="__main__":
    main()