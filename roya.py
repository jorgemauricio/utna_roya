from mpl_toolkits.basemap import Basemap 
import matplotlib.pyplot as plt 
from ftplib import FTP 
from api import claves 
import shapefile
import pandas as pd 
import numpy as np 
import os
from scipy.interpolate import griddata as gd

def main(): #Contiene las funciones que se ejecutarán
    cve = claves()
    fecha = obt_fecha(cve)
    cincodias = cinco_dias(fecha)
    desc_docs(fecha,cve)
    mapa_tot(fecha,cincodias)

def obt_fecha(cve): #Obtiene la fecha desde el FTP del Instituto
    fecha = []
    ftp = FTP(cve.ip) 
    ftp.login(cve.usr, cve.pwd) 
    ftp.dir(fecha.append) 
    fecha = fecha[-1].split()[-1] 
    print('La conexión fue un exito y la fecha obtenida es "{}".\n'.format(fecha))
    return fecha 

def cinco_dias(fecha): #Genera un arreglo de 5 fechas subsecuentes a la fecha ingresada por parametro
    ano, mes, dia = (int(i) for i in fecha.split("-")) #Se almacenan los datos y estos son divididos por un "-"
    if mes in (1, 3, 5, 7, 8, 10, 12): #Aqui se muestra la validación de la fecha
        dias_mes = 31
    elif mes == 2:
        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0): 
            dias_mes = 29
        else:
            dias_mes = 28
    elif mes in (4, 6, 9, 11):
        dias_mes = 30
    dias = []
    for n in range(0, 5):
        if dia + n <= dias_mes:
            dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes, dia + n))
        else:                                                               
            if mes != 12:
                dias.append('{:04d}-{:02d}-{:02d}'.format(ano, mes+1, n - (dias_mes - dia)))
            else:
                dias.append('{:04d}-01-{:02d}'.format(ano + 1, n - (dias_mes - dia)))
    print('La lista se generó correctamente: {}.\n'.format(dias))
    return dias 

def desc_docs(fecha, cve): #Descarga los 5 archivos respectivos a la fecha ingresada por parametro
    ftp = FTP(cve.ip); 
    ftp.login(cve.usr, cve.pwd) 
    ftp.cwd('{}'.format(fecha)) 
    if not os.path.exists('datos'): 
        os.mkdir('datos') 
    os.chdir('datos') 
    if not os.path.exists('{}'.format(fecha)): 
        os.mkdir('{}'.format(fecha)) 
    os.chdir('{}'.format(fecha)) 
    for i in range(1, 6): 
        print ('Descargando archivo d{}.txt, de la fecha {} ...'.format(i, fecha))
        ftp.retrbinary('RETR d{}.txt'.format(i),open('d{}.txt'.format(i),'wb').write) 
    ftp.quit()
    os.chdir('../..') 

def roya(Tpro,Dpoint,Noch_fres): #Función para la creación del modelo para calcular la probabilidad de aparición de roya
    if Tpro >= 25 and Tpro <=30 and Dpoint > 5 and Noch_fres >= 15 and Noch_fres <=20: 
        return 1
    else:
        return 0

def indice(d1,d2,d3,d4,d5): #Función que crea el indice para la probabilidad de aparición de la roya
    if d1==1 and d2==1 and d3==1 and d4==1 and d5==1:
        return 10 
    elif d1==0 and d2==1 and d3==1 and d4==1 and d5==1:
        return 9 
    elif d1==1 and d2==1 and d3==1 and d4==1 and d5==1:
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

def mapa_tot(fecha, cincodias): 
    colores = ['#00FF00','#00FF00','#00FF00','#00FF00','#FFFF00','#FFFF00','#FFFF00','#FF8000','#FF8000','#FF0000']
    rangos = ('00011', '00110', '01100', '11000', '00111', '01110', '11100', '01111', '11110', '11111')
    grado = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    var = ['Tpro', 'Dpoint', 'Noch_fres']
    df = pd.DataFrame()
    for i in range (1, 6):
        datos = pd.read_csv('datos/{}/d{}.txt'.format(fecha, i)) 
        df['Tpro{}'.format(i)] = datos['Tpro'.format(i)] 
        df['Noch_fres{}'.format(i)] = (datos['Tmax'.format(i)] - datos['Tmin'.format(i)])
        df['Dpoint{}'.format(i)] = datos['Dpoint'.format(i)]
        Long, Lat, WprSoil10_40 = datos['Long'], datos['Lat'], datos['WprSoil10_40']
    df['Long'], df['Lat'] ,df['WprSoil10_40'] = Long, Lat, WprSoil10_40
    Long= np.array(df['Long'])
    Long_min, Long_max = Long.min(), Long.max()
    Lat= np.array(df['Lat'])
    Lat_min, Lat_max = Lat.min(), Lat.max() 
    df = df.loc[df['WprSoil10_40'] <= 99]
    if not os.path.exists('mapas'): 
        os.mkdir('mapas') 
    os.chdir('mapas')
    if not os.path.exists('{}'.format(fecha)): 
        os.mkdir('{}'.format(fecha)) 
    os.chdir('{}'.format(fecha))
    
    for i in range (1,6): 
        df['d{}'.format(i)] = df.apply(lambda x:roya(x['{}{}'.format(var[0],i)],x['{}{}'.format(var[1],i)],x['{}{}'.format(var[2],i)]),axis=1)
    df['indice'] = df.apply(lambda x:indice(x['d1'],x['d2'],x['d3'],x['d4'],x['d5']),axis=1)
    
    Long = np.array(df['Long'])
    Lat = np.array(df['Lat'])
    for i in range (1, 7):
        map = Basemap(projection='mill', resolution='c', llcrnrlon=Long.min(), llcrnrlat=Lat.min(), 
            urcrnrlon=Long.max(), urcrnrlat=Lat.max())
        if (i > 0 and i < 6):
            royam = df.loc[df['d{}'.format(i)]==1]
            x, y = map(np.array(royam['Long']), np.array(royam['Lat']))
            map.scatter(x, y, marker='.', color='green', s=1)
            map.readshapefile('../../shapes/Estados', 'Mill')
            print('Generando mapa del dia {}'.format(cincodias[i-1]))
            plt.text(x =1.0536e+06, y =1.33233e+06, s = u' @2018 INIFAP', fontsize = 15 ,color='green')
            plt.title('Pronostico de ROYA \n del {}'.format(cincodias[i-1]))
            plt.savefig('d{}.png'.format(i), dpi=300)
        if (i == 6):
            royam = df.loc[df['indice'] > 0]
            x, y = map(np.array(royam['Long']), np.array(royam['Lat'])) 
            numCols = len(x)
            numRows = len(y)
            xi = np.linspace(x.min(), x.max(), numCols)
            yi = np.linspace(y.min(), y.max(), numRows)
            xi, yi = np.meshgrid(xi, yi)
            z = np.array(royam['indice'])
            zi = gd((x,y), z, (xi, yi), method='cubic')
            cs = map.contourf(xi, yi, zi, grado, cmap='RdYlGn_r')
            map.colorbar(cs)
            map.readshapefile('../../shapes/Estados', 'Mill')
            print('Generando mapa de Pronostico del: {} al {}'.format(cincodias[0],cincodias[-1]))
            plt.text(x =1.0536e+06, y =1.33233e+06, s = u' @2018 INIFAP', fontsize = 15 ,color='green')
            plt.title('Índice de probabilidad de presencia de ROYA a 5 dias \n del: {} al {}'.format(cincodias[0],cincodias[-1]))
            plt.savefig('d{}.png'.format(i), dpi=300)
        plt.clf()

if __name__=="__main__":
    main()