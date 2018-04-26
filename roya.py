from scipy.interpolate import griddata as gd
from mpl_toolkits.basemap import Basemap #Librería utilizada para la visualización de los datos y la generación de los mapas
import matplotlib.pyplot as plt #Librería utilizada para la visualización de los datos y la generación de los mapas
from api import claves #Modulo que contiene datos confidenciales
import pandas as pd #Librería utilizada para la manipulación de los documentos
import numpy as np #Librería utilizada para generar arreglos
import shapefile #Librería utilizada para leer los shapes
import ftplib #Librería utilizada para conectarse a un servidor FTP
import os #Librería utilizada para crear carpetas de almacenamiento

rangos = ('00011', '00110', '01100', '11000', '00111', '01110', '11100', '01111', '11110', '11111') #Lista de rangos
grado = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) #Lista de grados asociados a los rangos
var = ('Tpro','Dpoint','Tmax','Tmin') #Lista de variables a utilizar

def main():
    #fecha = '2018-02-14'
    cve = claves()
    fecha = obt_fecha(cve)
    cincodias = cinco_dias(fecha)
    desc_docs(fecha,cve)
    df = data_frame(fecha)
    gen_mapas(df, fecha, cincodias)

def obt_fecha(cve):
    """Función creada para obtener la fecha desde el servidor FTP"""
    fecha = []
    ftp = ftplib.FTP(cve.ip) 
    """Nombre del servidor"""
    ftp.login(cve.usr, cve.pwd) 
    """Usuario y contrasena del servidor"""
    ftp.dir(fecha.append) 
    fecha = fecha[-1].split()[-1]
    print ('Conexion realizada y fecha obtenida "{}".\n'.format(fecha))
    return fecha 

def modelo(Tpro,Dpoint,Tmax,Tmin): 
    """Función utilizada para devolver valores de 1/0 el lugar de Verdadero/Falso, en una declaración posterior"""
    if Tpro >= 25 and Tpro <=30 and Dpoint > 5 and (Tmax-Tmin) >= 15 and (Tmax-Tmin) <=20:  
        """Modelo para el filtrado de datos donde se presenta la roya"""
        return '1'
    else:
        return '0'

def indice(d1,d2,d3,d4,d5): 
    """Función utilizada para generar un índice que determinara el grado de impacto de la ROYA en base al modelo"""
    rango = '{}{}{}{}{}'.format(d1,d2,d3,d4,d5)
    if rango in rangos:
        for i in range(0, len(rangos)):
            if rangos[i] == rango:
                ubic = rangos.index(rangos[i])
                return grado[ubic]
    else:
        return 0

def cinco_dias(fecha): 
    """Función para obtener cuatro días posteriores a la fecha obtenida y almacenarlos en una lista junto con dicha fecha"""
    ano, mes, dia = (int(i) for i in fecha.split("-")) 
    if mes in (1, 3, 5, 7, 8, 10, 12):
        dias_mes = 31
    elif mes == 2:
        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0): 
            dias_mes = 29
        else:
            dias_mes = 28
    elif mes in (4, 6, 9, 11):
        dias_mes = 30
    cincodias = []
    for n in range(0, 5): 
        """Ciclo utilizado para almacenar las 5 fechas"""
        if dia + n <= dias_mes:
            cincodias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes, dia + n))
        else:
            if mes != 12:
                cincodias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes+1, n - (dias_mes - dia)))
            else:
                cincodias.append('{:04d}-01-{:02d}'.format(ano + 1, n - (dias_mes - dia)))
    print('Lista de 5 dias generada: {}.\n'.format(cincodias))
    return cincodias 

def desc_docs(fecha, cve): 
    """Función para la descarga los documentos de la carpeta con el nombre de la fecha actual"""
    ftp = ftplib.FTP(cve.ip); 
    ftp.login(cve.usr, cve.pwd) 
    ftp.cwd('{}'.format(fecha))
    if not os.path.exists('datos'):
        os.mkdir('datos')
    os.chdir('datos')
    if not os.path.exists('{}'.format(fecha)):
        os.mkdir('{}'.format(fecha))
    os.chdir('{}'.format(fecha))
    for i in range(1, 6): 
        """Ciclo que realiza 5 veces el proceso incrementando su valor en 1 para la descarga de cada documento"""
        print ('Descargando archivo d{}.txt, de la fecha {} ...'.format(i, fecha))
        ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write) 
        """Descarga los documentos"""
    ftp.quit()
    os.chdir('../..')

def data_frame(fecha): 
    """Función para la generación de un DataFrame, para tomar las variables a utilizar"""
    df = pd.DataFrame() 
    print ('\nGenerando DataFrame ...')
    for i in range (1, 6): 
        """Ciclo donde se prosesan los 5 documentos"""
        datos = pd.read_csv('datos/{}/d{}.txt'.format(fecha, i))
        for j in var:
            df['{}{}'.format(j,i)] = datos[j] 
        Long, Lat, WprSoil10_40 = datos['Long'], datos['Lat'], datos['WprSoil10_40']
    df['Long'], df['Lat'] ,df['WprSoil10_40'] = Long, Lat, WprSoil10_40
    df = df.loc[df['WprSoil10_40'] <= 99]
    for i in range (1,6): 
        """Ciclo para generar cinco columnas una para cada dia, usando la funcion de validacion del modelo"""
        df['d{}'.format(i)] = df.apply(lambda x:modelo(x['{}{}'.format(var[0],i)],x['{}{}'.format(var[1],i)],x['{}{}'.format(var[2],i)],x['{}{}'.format(var[3],i)]),axis=1)
    df['indice'] = df.apply(lambda x:indice(x['d1'],x['d2'],x['d3'],x['d4'],x['d5']),axis=1) 
    """Generación de un índice en base a las 5 columnas para determinar la constante frecuencia de la roya"""
    print ('DataFrame generado.\n')
    return df 

def gen_mapas(df, fecha, cincodias): 
    """Genera 5 mapas de cada respectivo día, y uno del pronóstico de los 5 días"""
    if not os.path.exists('mapas'):
        os.mkdir('mapas')
    os.chdir('mapas') 
    if not os.path.exists('{}'.format(fecha)):
        os.mkdir('{}'.format(fecha))
    os.chdir('{}'.format(fecha))
    Long = np.array(df['Long'])
    Lat = np.array(df['Lat'])
    for i in range (1, 7): 
        """Generación de los 5 mapas en base a las 5 columnas del DataFrame"""
        map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), urcrnrlon=Long.max(), urcrnrlat=Lat.max())
        if (i > 0 and i < 6):
            roya = df.loc[df['d{}'.format(i)]=='1']
            x, y = map(np.array(roya['Long']), np.array(roya['Lat']))
            map.scatter(x, y, marker='.', color='green', s=1)
            map.readshapefile('../../shapes/Estados', 'Mill')
            print('Generando mapa del dia {} ...'.format(cincodias[i-1]))
            plt.title('Pronostico de ROYA \n del {}'.format(cincodias[i-1]))
            plt.text(x =1.0536e+06, y =1.33233e+06, s = u' @ INIFAP', fontsize = 15 ,color='green')
            plt.savefig('Pronostico_de_ROYA_del_{}.png'.format(cincodias[i-1]), dpi=300)
        if (i == 6): 
            """Generación de un mapa genérico en base al índice del DataFrame"""
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
            plt.text(x =1.0536e+06, y =1.33233e+06, s = u' @ INIFAP', fontsize = 15 ,color='green')
            plt.savefig('Pronostico_de_ROYA_del_{}_al_{}.png'.format(cincodias[0], cincodias[4]), dpi=300)
        plt.clf()
    os.chdir('../..')

if __name__=="__main__":
    main()