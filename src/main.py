from extract.scrapper import BeautyScraper

if __name__ == '__main__':
    # Se inicializa un objeto de la clase BeautyScraper para realizar el rasgado web
    sc = BeautyScraper()

    # Con el método start_scrapping, se realiza el rasgado de toda la pagina web: Timeline y master table 2017, 2018.
    # Al no indicar una fecha de inicio ni de fin se realiza, por defecto, el rasgado desde 01/01/2017 - hoy.
    # Para realizar el scrapping se utiliza el driver de google Chrome (puede cambiarse a Firefox).
    #sc.start_scrapping(driver_name='chrome')

    # A continuación, se muestran distintos métodos disponibles, para realizar el rasgado de la página web
    # https://www.hackmageddon.com.

    # Ejemplo 1:
    # Scrapping de TimeLine, Master Table 2018 y Master Table 2017 utilizando el webdriver de Firefox.
    # A partir de las fechas introducidas, la Master Table de 2017 se empieza a escrapear a partir del 15/06/2017.
    # Por otra parte, el Timeline, únicamente se realiza el rasgado des de el 01/01/2019 hasta 20/05/2019.

    # sc.start_scrapping(ini_date='2017-06-15', fin_date='2019-05-20', driver_name='firefox')

    # Ejemplo 2:
    # Cuando se utiliza el método _scrap_timeline, únicamente se realiza el rasgado web de la página:
    # https://www.hackmageddon.com/category/security/cyber-attacks-timeline/. En este rasgado web, por defecto, solo
    # se incluyen periodos de tiempo posteriores a 01/01/2019 y anteriores a la fecha de ejecución del script (fecha
    # actual). Si la fecha de inicio es anterior a 01/01/2019, se corrige automaticamente.
    # En el ejemplo se realiza el rasgado de los reports contenidos en el Timeline des del 01/01/2019 hasta la fecha de
    # ejecución del script.

    # sc._scrap_timeline(start_date='2017-06-15', end_date='2021-01-15', driver_name='firefox')

    # Ejemplo 3:
    # Cuando se utiliza el método _scrap_2018, únicamente se realiza el rasgado web de la página:
    # https://www.hackmageddon.com/2018-master-table/. Este rasgado web, por defecto, sólo incluye periodos de tiempo
    # comprendidos entre 01/01/2018 y 31/12/2018 (ambos incluidos). Si el usuario indica fechas de inicio o de fin
    # fuera de este rango, se corrigen automáticamente. Por otra parte, si el usuario indica fechas de inicio y de fin
    # comprendidas en este periodo de tiempo, se realiza un filtrado de los datos.

    # sc._scrap_2018(start_date='2017-06-15', end_date='2018-11-16', driver_name='firefox')

    # Ejemplo 4:
    # Cuando se utiliza el método _scrap_2017, únicamente se realiza el rasgado web de la página:
    # https://www.hackmageddon.com/2017-master-table/. Este rasgado web, por defecto, sólo incluye periodos de tiempo
    # comprendidos entre 01/01/2017 y 31/12/2017 (ambos días incluidos). Si el usuario indica fechas de inicio o de fin
    # fuera de este rango, se corrigen automáticamente. Por otra parte, si el usuario indica fechas de inicio y de fin
    # comprendidas en este periodo de tiempo, se realiza un filtrado de los datos.

    # sc._scrap_2017(start_date='2016-06-15', end_date='2017-11-16', driver_name='chrome')
