from constants import URL_SITE_DOMAIN, URL_SITE_MASTER_TABLE_2017, URL_SITE_MASTER_TABLE_2018, \
    URL_SITE_STATICS_TIMELINE, FIELDS_NAME, CHROME_DRIVER

from requests import get, HTTPError
from time import time, sleep
from datetime import datetime
from bs4 import BeautifulSoup as BS
from pandas import DataFrame
from numpy import reshape, insert
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = '/usr/bin/google-chrome'
CHROMEDRIVER_PATH = '/usr/bin/chromedriver'

chrome_options = Options()
chrome_options.add_argument("--headless")


def time_exec(f):
    def g(*args, **kwargs):
        start = time()
        func = f(*args, **kwargs)
        print(time() - start)
        return func
    return g


class BeautyScraper:

    def __init__(self, url_site):
        self.url_site = url_site
        self.url_next_site = url_site
        self.ini_date = datetime.now().date()
        self.fin_date = datetime.now().date()
        self.requests_time = [0, 0, 0]
        self.request_mean_time = 0
        self.lambda_time = 0.1
        self.missing_calls = [False, False, False]
        self.df = DataFrame(columns=FIELDS_NAME)
        self.driver = webdriver.Chrome(CHROME_DRIVER, chrome_options=chrome_options)

    def update_df(self, values):
        self.df = self.df.append(other=DataFrame(data=values, columns=FIELDS_NAME), ignore_index=True)

    @time_exec
    def request_url(self, url, wait_time=0):
        try:
            sleep(wait_time)
            request = self.driver.get(url)
            request.raise_for_status()
            return BS(request.content)
        except HTTPError:
            raise HTTPError("error en la peticion http")

    def set_request_time(self, time):
        self.requests_time.pop(0)
        self.requests_time.append(time)
        self.set_request_mean_time()

    def set_request_mean_time(self):
        pass

    def set_lambda_time(self, param):
        self.lambda_time = param

    def _scrap_timeline(self, **kwargs):
        if 'ini_date' in kwargs:
            self.set_ini_date(kwargs['ini_date'])
        if 'fin_date' in kwargs:
            self.set_fin_date(kwargs['fin_date'])

        while self.url_next_site:
            html_bs = self.request_url(self.url_next_site)
            for tags in html_bs.find_all('h2'):
                title = tags.a.text
                link = tags.a.get('href')
                author = None
                report_time = None

                if self.check_header(str_time=self.transform_header(title), frmt_time='%d-%B-%Y'):
                    self._scrap_report(link, author=None, report_date=None)
                else:
                    self.finish_scrapping()

            self.get_next_page(html_bs)

    def _scrap_report(self, url):
        html_bs = self.request_url(url)
        report_date = html_bs.find('time').get('datetime')
        author_name = html_bs.find('a', {'class': 'url fn n'}).text.replace('\t', '')
        n_views = html_bs.find('span', {'class': 'post-views-count'}).text
        return self._scrap_table(html=html_bs, author=author_name, report_date=report_date, views=n_views)

    def _scrap_table(self, html, author=None, report_date=None, views=None):
        raw_data = []
        for tags in html.find_all(['td'], {'style': ""}):
            if not tags.get('class'):
                if tags.a:
                    raw_data.append(tags.a.get('href'))
                else:
                    if tags.text != '':
                        raw_data.append(tags.text)

        reshaped_data = reshape(raw_data, (-1, 11))
        for i, item in enumerate([author, report_date, views], 11):
            reshaped_data = insert(reshaped_data, i, item, axis=1)

        return DataFrame(data=reshaped_data, columns=FIELDS_NAME)

    def get_next_page(self, html):
        self.url_next_site = html.find(class_='previous').a.get('href')

    def transform_header(self, title):
        return "-".join("-".join(title.split(" ")[:3]).split("-")[1:])

    def check_header(self, str_time, frmt_time):
        try:
            flag = self.ini_date <= datetime.strptime(str_time, frmt_time).date() <= self.fin_date
        except ValueError:
            flag = False
        return flag

    def finish_scrapping(self):
        self.url_next_site = None
        # Escribir csv

    def set_ini_date(self, date_frmt):
        try:
            self.ini_date = datetime.strptime(date_frmt, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Error, la fecha de inicio debe tener el formato YYYY-mm-dd")

    def set_fin_date(self, date_frmt):
        try:
            self.fin_date = datetime.strptime(date_frmt, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Error, la fecha de fin debe tener el formato YYYY-mm-dd")
