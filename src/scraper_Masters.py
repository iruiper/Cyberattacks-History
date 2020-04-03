# -*- coding: utf-8 -*-
"""
@author: iruizperez & jbustospelegri

Summary: Script principal para llamar a los scrapers de los masters para los años 2017 y 2018
"""
from bs4 import BeautifulSoup
from selenium import webdriver
import scraper_Master2017
import scraper_Master2018

# Comenzamos el proceso de scraping desde la raiz del site www.hackmageddon.com
driver = webdriver.Firefox()
driver.get('https://www.hackmageddon.com/');

# Descargamos el código fuente para rastrear los enlaces que nos llevarán a las URLs con datos anuales
source = driver.page_source
sopa = BeautifulSoup(source)

# Creamos una lista en la que añadiremos los hipervínculos que apunten a las URLs con datos anuales
labels = []
for aes in sopa.find_all('a'):
    hrefs = aes.get('href')
    # Las siguientes líneas servían como puntos de control para comprabar que se sacan bien las "hrefs" de los tags "a"
    #print(hrefs)
    #print(str(type(hrefs)))
    
    # En primer lugar descartamos los tags "a" que no tienen referencia "href"
    if str(type(hrefs)).find('None') == -1:
        # Sobre los "hrefs" nos quedamos con los que hacen referencia a "master-table", pero excluyendo las actualizaciones
        # porque hemos comprobado que esas URLs no continen los listados que queremos descargar
        if (str(hrefs).find('master-table') != -1) & (str(hrefs).find('update') == -1):
            labels.append(hrefs)

# Nos quedamos con la lista única de valores de URLs que queremos someter a scraping
URLs_master = list(set(labels))

# Liberamos el driver
driver.quit()

# Como hemos identificado estructuras distintas para 2017 y 2018, ejecutamos el script que corresponda en función de la URL
for i in URLs_master:
    if "2017" in i:
        print("\nURL con con Master 2017")
        scraper_Master2017.run(i)
    elif "2018" in i:
        print("\nURL con con Master 2018")
        scraper_Master2018.run(i)
    else:
        next
