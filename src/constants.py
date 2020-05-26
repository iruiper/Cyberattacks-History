from os import path, getcwd, environ
from datetime import datetime

"""
    URLS DOMINIO
"""
# URL destino sobre las que se realizarán las tareas de web scrapping.
URL_SITE_STATICS_TIMELINE = "https://www.hackmageddon.com/category/security/cyber-attacks-timeline/"
URL_SITE_MASTER_TABLE_2017 = "https://www.hackmageddon.com/2017-master-table/"
URL_SITE_MASTER_TABLE_2018 = "https://www.hackmageddon.com/2018-master-table/"

"""
    DIRECTORIOS
"""
# Constantes que contienen las rutas utilizadas por el programa. Para ser robustos ante distintos sistemas operativos,
# se utiliza el método path.join. Adicionalmente, se utilizan directorios relativos en vez de directorios absolutos.
DRIVERS_PATH = path.join(getcwd(), '..', 'drivers')
RAW_DATA_PATH = path.join(getcwd(), '..', 'data', '00_raw')
CLEAN_DATA_PATH = path.join(getcwd(), '..', 'data', '01_clean')
ADDITIONAL_DATA_PATH = path.join(getcwd(), '..', 'data', '99_aditional')
LOGGING_DATA_PATH = path.join(getcwd(), '..', 'logging')
DESKTOP_PATH = path.join("C:", environ['HOMEPATH'], "Desktop")


"""
    ARCHIVOS
"""
# Nombre y ruta de los archivos de salida.
TIMELINE_PATH_FILE = path.join(RAW_DATA_PATH, f'scrapping {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')
MASTER_2018_PATH_FILE = path.join(RAW_DATA_PATH, f'Master Data 2018 {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')
MASTER_2017_PATH_FILE = path.join(RAW_DATA_PATH, f'Master Data 2017 {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')
LOGGING_PATH_FILE = path.join(LOGGING_DATA_PATH, f'scrapping {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')

"""
    DRIVER CONSTANTS
"""
# Ruta del webdriver de FireFox
FIREFOX_DRIVER_EXE = path.join(DRIVERS_PATH, 'geckodriver.exe')

# Ruta del webdriver de Google
CHROME_DRIVER_EXE = path.join(DRIVERS_PATH, 'chromedriver.exe')

"""
    PETICIONES HTTP
"""
# Constante que contiene el USER AGENT del navegador web para simular que la petición es realizada por un humano y no
# un script.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/80.0.3987.163 Safari/537.36"

"""
    FORMATOS DOMINIO
"""
# Constante utilizada para parsear los títulos de los reports del Timeline
HEADERS_REPORTS_FORMAT = "%d-%d %b %Y Cyber Attacks Timeline"

"""
    CAMPOS DATASET
"""
# Campos que contiene el dataset
FIELDS_NAME = \
    ["id", "date", "author", "target", "description", "attack", "target_class", "attack_class", "country", "link",
     'author_report', 'date_report', 'views']
