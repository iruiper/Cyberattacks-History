"""

"""

from os import path, getcwd

"""
    URLS DOMINIO
"""
URL_SITE_DOMAIN = "https://www.hackmageddon.com/"
URL_SITE_STATICS_TIMELINE = "https://www.hackmageddon.com/category/security/cyber-attacks-timeline/"
URL_SITE_MASTER_TABLE_2017 = "https://www.hackmageddon.com/2017-master-table/"
URL_SITE_MASTER_TABLE_2018 = "https://www.hackmageddon.com/2018-master-table/"

"""
    DRIVER PATHS
"""

CHROME_DRIVER = path.join(getcwd(), '..', 'drivers', 'chromedriver.exe')
FIREFOX_DRIVER = path.join(getcwd(), '..', 'drivers', 'geckodriver.exe')
PHANTOM_JS = path.join(getcwd(), '..', 'drivers', 'phantomjs.exe')

"""
    FORMATOS DOMINIO
"""
HEADERS_REPORTS_FORMAT = "%d-%d %b %Y Cyber Attacks Timeline"

"""
    CAMPOS DATASET
"""
FIELDS_NAME = \
    ["id", "date", "author", "target", "description", "attack", "target_class", "attack_class", "country", "link",
     "tag", 'author_report', 'date_report']
