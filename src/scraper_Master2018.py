# -*- coding: utf-8 -*-
"""
@author: iruizperez & jbustospelegri

Summary: Script para la automatización de la descarga del Master 2018, directamente a través de la URL 
en la que se encuentra el control dinámico de JavaScript que permite su descarga
"""
# Importamos librerías que utilizaremos para el scraping
from selenium import webdriver
import time
import os
import shutil
from pathlib import Path

def run(url):
    # Vamos a descargar de manera temporal los archivos a través de los elementos dinámicos del site, al escritorio
    # A continuación lo moveremos a la ubicación en la que se está ejecutando el script
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    localpath = Path.cwd()
    master2018file = desktop+'\\2018 Master Table.csv'
    
    # Línea de control para comprobar que se selecciona correctamente la ruta al escritorio
    # Eliminar el siguiente comentario para evaluar el punto de control
    #print(desktop)
    
    # Creamos un perfil de usuario para el navegador Firefox
    fp = webdriver.FirefoxProfile()
    
    # Indicamos la ruta por defecto al escritorio (browser.download.folderlist=0)
    fp.set_preference("browser.download.folderList",0)
    
    # Indicamos que no haga la consulta de si almacenar en disco para archivos de tipo "text/csv"
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")
    driver = webdriver.Firefox(firefox_profile=fp)  
    
    # Asignamos el perfil al driver de Selenium que manejará la navegación por la URL
    driver.get(url)
    
    # Averiguamos la secuencia de clicks necesarios para descargar el archivo a través del elemento dinámico
    python_button = driver.find_element_by_css_selector('.buttons-csv > span')
    python_button.click()
    time.sleep(5) # Temporizador para que haya tiempo para la descarga
    
    # Liberamos el driver
    driver.quit()
    
    # Movemos el archivo desde el escritorio, a la ubicación en la que se ejecuta el script
    shutil.move(master2018file, localpath)
