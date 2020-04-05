from scrapper import BeautyScraper

if __name__ == '__main__':
    # Scrapping de toda la pagina web (Timeline, master 2018, master 2017). Utilizando chrome
    sc = BeautyScraper()
    sc.start_scrapping(driver_name='chrome')

    # Scrapping de toda la pagina web (Timeline, master 2018, master 2017 adaptandose a las fechas). Utilizando Firefox y acotando fechas.
    # sc.start_scrapping(ini_date='2017-06-15', fin_date='2019-05-20', driver_name='firefox')

    # Scrapping de solo el timeline indicando fechas. El usuario introduce fechas erroneas de inicio. Utilizando Chrome
    # sc._scrap_timeline(start_date='2017-06-15', end_date='2021-01-15', driver_name='chrome')

    # Scrapping de solo el timeline indicando fechas. El usuario introduce fecha de inicio posterior a fin --> no se debe ejecutar
    # sc._scrap_timeline(start_date='2027-06-15', end_date='2021-01-15')

    # Scrapping de master table 2018. El usuario introduce fecha de inicio fuera del terminio (anterior). Utilizando Firefox --> ejecuta a partir del 01/01/2018
    # sc._scrap_2018(start_date='2017-06-15', end_date='2018-11-16', driver_name='firefox')

    # Scrapping de master table 2018. Se introducie fecha inicio posterior a 2018 --> no se debería ejecutar
    # sc._scrap_2018(start_date='2019-06-15', end_date='2020-11-16', driver_name='firefox')

    # Scrapping de master table 2018. Se introducie fecha fin posterior a 2018 --> se ejecuta con fecha ini hasta 31/12/2018
    # sc._scrap_2018(start_date='2018-06-15', end_date='2020-11-16')

    # Scrapping de master table 2017. El usuario introduce fecha de inicio fuera del terminio (anterior). Utilizando Firefox --> ejecuta a partir del 01/01/2017
    # sc._scrap_2017(start_date='2016-06-15', end_date='2017-11-16', driver_name='firefox')

    # Scrapping de master table 2017. Se introducie fecha inicio posterior a 2017 --> no se debería ejecutar
    # sc._scrap_2017(start_date='2019-06-15', end_date='2020-11-16')

    # Scrapping de master table 2017. Se introducie fecha fin posterior a 2017 --> se ejecuta con fecha ini hasta 31/12/2017
    # sc._scrap_2017(start_date='2017-06-15', end_date='2020-11-16', driver_name='chrome')
