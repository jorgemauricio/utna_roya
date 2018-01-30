from api import claves
from ftplib import FTP #Libreria utilizada para conectarse a un servidor FTP y obtener informacion
import os #Libreria utilizada para crear carpetas de almacenamiento
import requests #Libreria utilizada para obtener el url
import sys #Libreria utilizada para obtener el codigo obtenido

def obt_url(url): #Obtener fecha del url
    fecha = requests.get(url)
    if fecha.status_code != 200: #Validar el estado de codigo, para validar que se encontro el url
        sys.stdout.write('! Error {} el url no es correcto "{}" '.format(fecha.status_code, url))
        return None #No retorna ningun valor

    return fecha.text #Retorna el valor obtenido en el url

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

def desc_info(fehca):
	ftp = FTP(ip); #Nombre del servidor
	ftp.login(user=usr, passwd=pwd) #Usuario y contrasena del servidor
	ftp.cwd('{}'.format(fecha)) #Infresa a una carpeta dentro del servidor
	for i in range(1, 6): #Ciclo utilizaro para imprimir los 5 archivos que son los pronosticos (dia actual mas 4 subsecuentes)
	    ftp.retrbinary('RETR d{}.txt'.format(i),open('{}-d{}.txt'.format(fecha, i),'wb').write) #Descarga los documentos asignandoles
	ftp.quit() 

cve = claves()
fecha = obt_url(cve.url)
print (cinco_dias(fecha))