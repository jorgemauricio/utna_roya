from api import claves 
from ftplib import FTP #Libreria utilizada para conectarse a un servidor FTP y obtener informacion
import os #Libreria utilizada para crear carpetas de almacenamiento
import pandas as pd #Libreria utilizada para leer los documentos (csv)
import numpy as np #Libreria utilizada para generar arreglos
import matplotlib.pyplot as plt #Libreria utilizada para la generacion de los mapas
from mpl_toolkits.basemap import Basemap #Libreria utilizada para establecer las coordenadas del mapa
import shapefile #Libreria utilizada para leer los shapes
import time
from scipy.interpolate import griddata as gd
from time import gmtime, strftime

def main():
    fecha = '2018-02-01'
    cve = claves()
    #fecha = obt_fecha(cve)
    cincodias = cinco_dias(fecha)
    #desc_docs(fecha,cve)
    mapa_tot(fecha,cincodias)
def obt_fecha(cve): #Obtener la fecha actual
    fecha = []
    ftp = FTP(cve.ip) #Nombre del servidor
    ftp.login(cve.usr, cve.pwd) #Usuario y contrasena del servidor
    ftp.dir(fecha.append) #Se almacena toda la informacion que se encuentra en el directorio actual dentro del arreglo
    fecha = fecha[-1].split()[-1] #Se toma el ultimo valor del arreglo, se separa la cadena en un arreglo dividido por espacios y se toma el ultimo valor.
    print ('Conexion realizada y fecha obtenida "{}"'.format(fecha))
    return fecha # Se devuelve el valor obtenido (la fecha)
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
    dias = []
    for n in range(0, 5): #Ciclo utilizado para almacenar los 5 dias
        if dia + n <= dias_mes:
            dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes, dia + n)) #'{:04d}-{:02d}-{:02d}' - Formato para la fecha
        else:                                                               #Agrega un sero en el caso de los nuemros unicos entre 1 - 9
            if mes != 12:
                dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes+1, n - (dias_mes - dia)))
            else:
                dias.append('{:04d}-01-{:02d}'.format(ano + 1, n - (dias_mes - dia)))
    print('Lista de 5 dias generada: {}'.format(dias))
    return dias #Develve la lista de los 5 dias
def desc_docs(fecha, cve): #Descargar los documentos de la carpeta con el nombre de la fecha actual
    ftp = FTP(cve.ip); #Nombre del servidor
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
        ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write) #Descarga los documentos
    ftp.quit()
    os.chdir('../..') #Sale de la carpeta con la fecha/datos al directorio raiz
def roya(Tpro,Dpoint,Noch_fres): #Funcion utilizada para devolver valores de 1/0 el lugar de Verdadero/Falso, en una declaracion posterior
    if Tpro >= 25 and Tpro <=30 and Dpoint > 5 and Noch_fres >= 15 and Noch_fres <=20: #Filtrado de datos donde se presenta la ROYA
        return 1
    else:
        return 0
def indice(d1,d2,d3,d4,d5):
    if d1==1 and d2==1 and d3==1 and d4==1 and d5==1:
        return 10 
    elif d1==0 and d2==1 and d3==1 and d4==1 and d5==1:
        return 9 
    elif d1==1 and d2==1 and d3==1 and d4==1 and d5==0:
        return 8 
    elif d1==1 and d2==1 and d3==1 and d4==0 and d5==0:
        return 7 
    elif d1==0 and d2==1 and d3==1 and d4==1 and d5==0:
        return 6
    elif d1==0 and d2==0 and d3==1 and d4==1 and d5==1:
        return 5 
    elif d1==1 and d2==1 and d3==0 and d4==0 and d5==0:
        return 4 
    elif d1==0 and d2==1 and d3==1 and d4==0 and d5==0:
        return 3 
    elif d1==0 and d2==0 and d3==1 and d4==1 and d5==0:
        return 2 
    elif d1==0 and d2==0 and d3==0 and d4==1 and d5==1:
        return 1 
    else:
        return 0
def mapa_tot(fecha, cincodias): #Generacion del Pronostico de ROYA en los 5 fias
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
    Long, Lat = np.array(df['Long']), np.array(df['Lat'])
    Long_min, Long_max, Lat_min, Lat_max = Long.min(), Long.max(), Lat.min(), Lat.max() 
    df = df.loc[df['WprSoil10_40'] <= 99]
    if not os.path.exists('mapas'): #Verifica si la carpeta mapas existe (donde se almacenaran los documentos a descargar)
        os.mkdir('mapas') #Crea la carpeta mapas
    os.chdir('mapas') #Accede a la carpeta mapas
    if not os.path.exists('{}'.format(fecha)): #Verificar si la carpeta fecha existe que es donde se almacenaran los mapas
        os.mkdir('{}'.format(fecha)) #Crea la carpeta fecha donde se almacenaran los documentos
    os.chdir('{}'.format(fecha)) #Ingresar a la carpeta fecha
    variables = ['Tpro','Dpoint','Noch_fres'] #Lista con las variables a utilizar
    
    for i in range (1,6): #Cliclo utilizado para crear 5 columnas (1 por cada filtro de variables), utilizando la funcion "roya" para determinar que filas cumplen las condiciones
        df['d{}'.format(i)] = df.apply(lambda x:roya(x['{}{}'.format(variables[0],i)],x['{}{}'.format(variables[1],i)],x['{}{}'.format(variables[2],i)]),axis=1)
    df['indice'] = df.apply(lambda x:indice(x['d1'],x['d2'],x['d3'],x['d4'],x['d5']),axis=1)
    
    '''for i in range (1, 6):
        map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), urcrnrlon=Long.max(), urcrnrlat=Lat.max())
        var = df.loc[df['d{}'.format(i)]==1]
        Eje_x, Eje_y = np.array(var['Long']), np.array(var['Lat'])
        x, y = map(Eje_x, Eje_y)
        map.scatter(x, y, marker='.',color='#00FF00',s=1)
        map.readshapefile("../../shapes/Estados", 'Mill')
        print ('Generando mapa de Pronostico de ROYA de {} ...'.format(cincodias[i-1]))
        plt.title('Pronostico de ROYA \n De {}'.format(cincodias[i-1]))
        plt.savefig(fname="Pronostico_ROYA_{}.png".format(cincodias[i-1]), dpi=300)
        plt.clf()
    
    colores = ['#00FF00','#00FF00','#00FF00','#00FF00','#FFFF00','#FFFF00','#FFFF00','#FF8000','#FF8000','#FF0000']
    map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), urcrnrlon=Long.max(), urcrnrlat=Lat.max())
    for i in range (1, 11):
        var = df.loc[df['indice']==i]  
        Eje_x, Eje_y = np.array(var['Long']), np.array(var['Lat'])
        x, y = map(Eje_x, Eje_y)
        map.scatter(x, y, marker='.',color='{}'.format(colores[i-1]),s=1)
        #map.contourf(x, y, z, color='{}'.format(colores[i-2]))
    map.readshapefile("../../shapes/Estados", 'Mill')
    print ('Generando mapa de Pronostico de ROYA de {} a {} ...'.format(cincodias[0], cincodias[4]))
    plt.title('Pronostico de ROYA \n De {} a {}'.format(cincodias[0], cincodias[4]))
    plt.savefig(fname="Pronostico_ROYA_{}_a_{}.png".format(cincodias[0], cincodias[4]), dpi=300)
    os.chdir('../..') #Sale de la carpeta con la fecha/datos al directorio raiz
    '''
    map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), urcrnrlon=Long.max(), urcrnrlat=Lat.max())
    x, y = map(np.array(df['Long']), np.array(df['Lat']))
    numCols=len(x)
    numRows=len(y)
    xi = np.linspace(x.min(), x.max(), numCols)
    yi = np.linspace(y.min(), y.max(), numRows)
    xi, yi = np.meshgrid(xi, yi)
    z = np.array(df['indice'])
    zi = gd((x,y), z, (xi,yi), method='cubic')
    mapa = map.contourf(xi, yi, zi, cmap='RdYlGn')
    cbar = map.colorbar(cs, location='rigth', pad='5%')
if __name__=="__main__":
    main()
