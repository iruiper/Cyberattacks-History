# -*- coding: utf-8 -*-
"""
@author: iruizperez & jbustospelegri

Summary: Script principal para llamar a los scrapers de los masters para los años 2017 y 2018
"""
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://www.hackmageddon.com/');

source = driver.page_source
sopa = BeautifulSoup(source)


labels = []
for aes in sopa.find_all('a'):
    hrefs = aes.get('href')
    #print(hrefs)
    #print(str(type(hrefs)))
    if str(type(hrefs)).find('None') == -1:
        if (str(hrefs).find('master-table') != -1) & (str(hrefs).find('update') == -1):
            labels.append(hrefs)

URLs_master = list(set(labels))

driver.quit()
