from scrapper import BeautyScraper
from constants import *

if __name__ == '__main__':
    sc = BeautyScraper(url_site=URL_SITE_STATICS_TIMELINE)
    #sc._scrap_report("https://www.hackmageddon.com/2020/03/30/1-15-march-2020-cyber-attacks-timeline/")
    sc._scrap_report("https://www.hackmageddon.com/2020/01/07/1-15-december-2019-cyber-attacks-timeline/")
    #sc._scrap_timeline(ini_date='2020-01-17')
