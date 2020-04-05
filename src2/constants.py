"""

"""

from os import path, getcwd, environ
from datetime import datetime
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver import FirefoxProfile

"""
    URLS DOMINIO
"""
URL_SITE_STATICS_TIMELINE = "https://www.hackmageddon.com/category/security/cyber-attacks-timeline/"
URL_SITE_MASTER_TABLE_2017 = "https://www.hackmageddon.com/2017-master-table/"
URL_SITE_MASTER_TABLE_2018 = "https://www.hackmageddon.com/2018-master-table/"

"""
    DIRECTORIOS
"""
DRIVERS_PATH = path.join(getcwd(), '..', 'drivers')
RAW_DATA_PATH = path.join(getcwd(), '..', 'data', '00_raw')
CLEAN_DATA_PATH = path.join(getcwd(), '..', 'data', '01_clean')
LOGGING_DATA_PATH = path.join(getcwd(), '..', 'logging')
DESKTOP_PATH = path.join("C:", environ['HOMEPATH'], "Desktop")

"""
    ARCHIVOS
"""
TIMELINE_PATH_FILE = path.join(RAW_DATA_PATH, f'scrapping {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')
MASTER_2018_PATH_FILE = path.join(RAW_DATA_PATH, f'Master Data 2018 {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')
MASTER_2017_PATH_FILE = path.join(RAW_DATA_PATH, f'Master Data 2017 {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')
LOGGING_PATH_FILE = path.join(LOGGING_DATA_PATH, f'scrapping {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv')

"""
    DRIVER CONSTANTS
"""

FIREFOX_DRIVER_EXE = path.join(DRIVERS_PATH, 'geckodriver.exe')
FIREFOX_PROFILE = FirefoxProfile()
FIREFOX_PROFILE.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
FIREFOX_PROFILE.set_preference("browser.download.dir", RAW_DATA_PATH)
FIREFOX_PROFILE.set_preference("browser.download.folderList", 0)

FIREFOX_OPTIONS = Firefox_Options()
FIREFOX_OPTIONS.add_argument('--headless')

CHROME_DRIVER_EXE = path.join(DRIVERS_PATH, 'chromedriver.exe')
CHROME_OPTIONS = Chrome_Options()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])
CHROME_OPTIONS.add_experimental_option('useAutomationExtension', False)
CHROME_OPTIONS.add_experimental_option("prefs", {"download.default_directory": DESKTOP_PATH,
                                                 "download.prompt_for_download": False,
                                                 "download.directory_upgrade": True,
                                                 "safebrowsing_for_trusted_sources_enabled": False,
                                                 "safebrowsing.enabled": False})

"""
    FORMATOS DOMINIO
"""
HEADERS_REPORTS_FORMAT = "%d-%d %b %Y Cyber Attacks Timeline"

"""
    CAMPOS DATASET
"""
FIELDS_NAME = \
    ["id", "date", "author", "target", "description", "attack", "target_class", "attack_class", "country", "link",
     'author_report', 'date_report', 'views']
