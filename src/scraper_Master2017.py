# -*- coding: utf-8 -*-
"""
@author: iruizperez & jbustospelegri

Summary: Script para la automatización de la descarga del Master 2017, 
directamente a través de la URL de Google Docs en la que se encuentra alojado
"""

# Importamos librerías que utilizaremos para el scraping
from selenium import webdriver
import time
import os
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

def run(url):
    # Vamos a descargar de manera temporal los archivos a través de los enlaces dinámicos del site, al escritorio
    # A continuación lo moveremos a la ubicación en la que se está ejecutando el script
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    localpath = Path.cwd()
    
    # Para el movimiento de ficheros en el sistema operativo hemos averiguado mediante inspección el nombre con el que se guarda la descarga
    # Por consistencia en la nomenclatura, al renombrar utilizamos un nombre análogo al del Master 2018
    master2017file = desktop+'\\2017 Master Table - Sheet1.csv'
    destinationfile = str(localpath)+'\\2017 Master Table.csv'
    
    # Líneas de control para comprobar que se selecciona correctamente la ruta al escritorio, y a la ubicación final
    # Eliminar los dos siguientes comentarios para evaluar el punto de control
    
    print(desktop)
    print(destinationfile)
    
    # Creamos un perfil de usuario para el navegador Firefox
    fp = webdriver.FirefoxProfile()
    
    # Indicamos la ruta por defecto al escritorio (browser.download.folderlist=0)
    fp.set_preference("browser.download.folderList",0)
    # Indicamos que no haga la consulta de si almacenar en disco para archivos de tipo "text/csv"
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")
    
    # Asignamos el perfil al driver de Selenium que manejará la navegación por la URL
    driver = webdriver.Firefox(firefox_profile=fp)  
    
    # Navegamos a través del driver a la URL del Master 2017
    driver.get(url)
    
    # Descargamos el código fuente para navegar sus tags mediante BeautifulSoup
    source = driver.page_source
    sopa = BeautifulSoup(source)
    
    # En el siguiente bucle, buscamos los tags "a", y creamos una lista con las URL a las que apunta, que hagan referencia 
    # a "docs.google.com", es decir, a documentos de Google Docs
    labels = []
    for aes in sopa.find_all('a'):
        hrefs = aes.get('href')
        #print(hrefs)
        #print(str(type(hrefs)))
        if str(type(hrefs)).find('None') == -1:
            if str(hrefs).find('docs.google.com') != -1:
                labels.append(hrefs)
    
    # Cambiamos el foco del driver a la URL en la que se encuentra almacenado el documento en Google Docs
    driver.get(labels[0])
               
    # Averiguamos la secuencia de clicks necesarios para navegar al menú Archivo > Descargar > Archivo csv
    python_file = driver.find_element_by_id('docs-file-menu')
    python_file.click()
    python_save = driver.find_element_by_xpath("//div[12]/div/span/span")
    python_save.click()
    time.sleep(5) # Temporizador para forzar a que haya dado tiempo a asumir los clicks
    python_csv = driver.find_element_by_xpath("//span[contains(.,'Valores separados por comas (.csv, hoja actual)')]")
    python_csv.click()
    time.sleep(5) # Temporizador para forzar que haya dado tiempo a la descarga
    
    # Liberamos el driver
    driver.quit()
    
    # Movemos el archivo desde el escritorio, a la ubicación en la que se ejecuta el script
    shutil.move(master2017file, destinationfile)

