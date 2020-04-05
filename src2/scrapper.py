from constants import FIELDS_NAME, URL_SITE_STATICS_TIMELINE, LOGGING_DATA_PATH, DESKTOP_PATH, RAW_DATA_PATH,\
    TIMELINE_PATH_FILE, URL_SITE_MASTER_TABLE_2018, URL_SITE_MASTER_TABLE_2017, FIREFOX_DRIVER_EXE,\
    FIREFOX_PROFILE, FIREFOX_OPTIONS, CHROME_DRIVER_EXE, CHROME_OPTIONS, MASTER_2017_PATH_FILE, MASTER_2018_PATH_FILE

import os
import glob
import shutil
from time import sleep, time
from datetime import datetime
from bs4 import BeautifulSoup
from pandas import DataFrame, read_csv, to_datetime

from selenium.webdriver import Firefox, Chrome
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from requests import get, HTTPError
from requests.exceptions import MissingSchema
from scrapper_utils import time_exec, log_info, get_fin_date, get_ini_date, check_header, transform_header, \
    create_logger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class BeautyScraper:

    def __init__(self):
        self.time = {'last_calls': [0, 0, 0], 'mean_time': 0, 'lambda': 0, 'wait_time': 0}
        self.missing_calls = [False, False, False]
        self.df = DataFrame(columns=FIELDS_NAME)
        self.request = None
        self.logger = create_logger(
            os.path.join(LOGGING_DATA_PATH, f'scrapping {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.csv'))
        self.set_driver('chrome')

    @time_exec
    def request_url(self, url, javascript=True):
        if javascript:
            self.driver.get(url)
            sleep(self.time['wait_time'])
            return BeautifulSoup(self.driver.page_source, 'html.parser')
        else:
            self.request = get(url)
            self.request.raise_for_status()
            return BeautifulSoup(self.request.content, 'html.parser')

    @time_exec
    def next_page(self, xpath_exp, **wait_kwargs):
        try:
            self.driver.find_element_by_xpath(xpath_exp).click()
            wait = WebDriverWait(self.driver, 30)
            if 'wait_contidion' in wait_kwargs:
                wait.until(wait_kwargs['wait_contidion'])
            return BeautifulSoup(self.driver.page_source, 'html.parser')
        except NoSuchElementException:
            raise NoSuchElementException
        except ElementClickInterceptedException:
            raise ElementClickInterceptedException

    def set_driver(self, driver):
        if str(driver).lower() == 'chrome':
            self.driver = Chrome(executable_path=CHROME_DRIVER_EXE, chrome_options=CHROME_OPTIONS)
        elif str(driver).lower() == 'firefox':
            self.driver = Firefox(firefox_profile=FIREFOX_PROFILE, executable_path=FIREFOX_DRIVER_EXE,
                                  options=FIREFOX_OPTIONS)
        else:
            print(f'{driver} no se corresponde con uno de los siguientes drivers: chrome o firefox.')

    def set_request_time(self, time_call):
        self.time['last_calls'].pop(0)
        self.time['last_calls'].append(time_call)
        self.set_request_mean_time()

    def set_request_mean_time(self):
        pass

    def set_lambda_time(self, param):
        self.time['lamda'] = param

    def finish_scrapping(self, file_name):
        self.df.to_csv(file_name, index=False, decimal=',', sep=";")
        print('SCRAPPING FINALIZADO')

    def start_scrapping(self, ini_date=datetime(2017, 1, 1).date(), fin_date=datetime.now().date(),
                        driver_name='chrome'):
        try:
            ini_date = get_ini_date(date=ini_date) if isinstance(ini_date, str) else ini_date
            fin_date = get_fin_date(date=fin_date) if isinstance(fin_date, str) else fin_date
            assert ini_date < fin_date, f"{ini_date} es superior a {fin_date}"

            if ini_date.year > 2018:
                self._scrap_timeline(start_date=ini_date, end_date=fin_date, driver_name=driver_name)

            elif 2017 < ini_date.year <= 2018:
                if fin_date.year > 2018:
                    self._scrap_timeline(start_date=datetime(2019, 1, 1).date(), end_date=fin_date,
                                         driver_name=driver_name)
                    self._scrap_2018(start_date=ini_date, driver_name=driver_name)
                else:
                    self._scrap_2018(start_date=ini_date, end_date=fin_date, driver_name=driver_name)

            elif 2016 < ini_date.year <= 2017:
                if fin_date.year > 2018:
                    self._scrap_timeline(start_date=datetime(2019, 1, 1).date(), end_date=datetime.now().date(),
                                         driver_name=driver_name)
                    self._scrap_2018(driver_name=driver_name)
                    self._scrap_2017(start_date=ini_date, driver_name=driver_name)
                elif fin_date.year > 2017:
                    self._scrap_2018(end_date=fin_date, driver_name=driver_name)
                    self._scrap_2017(start_date=ini_date, driver_name=driver_name)
                else:
                    self._scrap_2017(start_date=ini_date, end_date=fin_date, driver_name=driver_name)

            elif ini_date.year <= 2016:
                if fin_date.year > 2018:
                    self._scrap_timeline(start_date=datetime(2019, 1, 1).date(), end_date=datetime.now().date(),
                                         driver_name=driver_name)
                    self._scrap_2018(driver_name=driver_name)
                    self._scrap_2017(driver_name=driver_name)
                elif fin_date.year > 2017:
                    self._scrap_2018(end_date=fin_date, driver_name=driver_name)
                    self._scrap_2017(driver_name=driver_name)
                elif fin_date.year > 2016:
                    self._scrap_2017(end_date=fin_date, driver_name=driver_name)
                else:
                    print('no se puede generar el scrapping para fechas anteriores al 2016')

        except Exception as err:
            print(err)

    def _scrap_timeline(self, url=URL_SITE_STATICS_TIMELINE, start_date=datetime(2019, 1, 1).date(),
                        end_date=datetime.now().date(), driver_name='chrome'):

        self.set_driver(driver_name)
        ini_date = get_ini_date(date=start_date) if isinstance(start_date, str) else start_date
        fin_date = get_fin_date(date=end_date) if isinstance(end_date, str) else end_date
        assert ini_date < fin_date, f"{ini_date} es superior a {fin_date}"

        if ini_date.year < 2019:
            print("Warning. El año de la fecha de inicio es anterior a 2019. Se pondrá por defecto el 01/01/2019")
            ini_date = datetime(2019, 1, 1).date()

        html_bs = self.request_url(url, javascript=False)
        link, next_page_link = url, url
        title = ''
        while True:
            try:
                for tags in html_bs.find_all('h2'):
                    start = time()
                    title = tags.a.text
                    link = tags.a.get('href')
                    read, follow = check_header(str_time=transform_header(title), frmt_time='%d-%B-%Y',
                                                start=start_date, end=end_date)
                    if read:
                        report_data, total_entries = self._scrap_report(link)
                        self.df = self.df.append(report_data, ignore_index=False)
                        log_txt = f'leídas {len(report_data)} de {total_entries}'
                        log_info(logger=self.logger, title=title, url=link, status='OK', registers=len(report_data),
                                 time_scrap=time() - start, info=log_txt)
                    else:
                        if not follow:
                            self.missing_calls.pop(0)
                            self.missing_calls.append(True)
                            log_txt = f'No leído, report no contenido en las fechas {ini_date} y {fin_date}'
                            log_info(logger=self.logger, title=title, url=link, status='INFO', registers=0,
                                     time_scrap=time() - start, info=log_txt)

                        log_txt = f'No leído, report no contenido en las fechas {ini_date} y {fin_date}'
                        log_info(logger=self.logger, title=title, url=link, status='INFO', registers=0,
                                 time_scrap=time() - start, info=log_txt)
                        assert not all(self.missing_calls), "No existen más reports para el periodo seleccionado"

                next_page_link = html_bs.find(class_='previous').find('a')
                assert next_page_link, "No existen más reports en el timeline."
                html_bs = self.request_url(next_page_link.get('href'), javascript=False)
            except HTTPError:
                log_info(logger=self.logger, title=title, url=next_page_link, status='KO', registers=0,
                         time_scrap=time() - start, info='Error de conexión ')
            except MissingSchema:
                log_info(logger=self.logger, title=title, url=next_page_link, status='KO', registers=0,
                         time_scrap=time() - start, info='Error de conexión ')
            except AssertionError as err:
                log_info(logger=self.logger, title=title, url=link, status='KO', registers=0,
                         time_scrap=time() - start, error=err)
                break
            except Exception as err:
                log_info(logger=self.logger, title=title, url=link, status='KO', registers=0,
                         time_scrap=time() - start, error=err)
                break

        self.finish_scrapping(file_name=TIMELINE_PATH_FILE)
        self.driver.close()

    def _scrap_report(self, url):
        report_df = DataFrame(columns=FIELDS_NAME)
        html_bs = self.request_url(url, javascript=True)
        try:
            total_data = html_bs.find(class_='dataTables_info').text.split(' ')[-2]
        except Exception:
            total_data = 'nan'

        extra_data = {
            'report_date': html_bs.find('time').get('datetime') if html_bs.find('time') else 'Not Found',
            'author': html_bs.find('a', {'class': 'url fn n'}).text.replace('\t', '') or 'Not Found',
            'views': html_bs.find('span', {'class': 'post-views-count'}).text or 'Not Found'
        }

        while True:
            try:
                next_page = str(int(html_bs.find(class_='paginate_button current').text) + 1)
                report_df = report_df.append(self._scrap_table(html=html_bs, **extra_data), ignore_index=True)
                html_bs = \
                    self.next_page(xpath_exp='//a[@class="paginate_button next"]',
                                   wait_contidion=EC.text_to_be_present_in_element(
                                       (By.XPATH, '//a[@class="paginate_button current"]'), next_page))

            except NoSuchElementException:
                break
            except ElementClickInterceptedException:
                break

        return report_df, total_data

    @staticmethod
    def _scrap_table(html, author=None, report_date=None, views=None):
        raw_data = {}
        row_count = len(html.find('tbody').find_all(['tr'], {'role': 'row'})) or 0

        for col in FIELDS_NAME[:-4]:
            tags = ['Not Found'] * row_count
            for i, tag in enumerate(html.find_all(['td'], {'class': f'column-{col.replace("_", "-")}'})):
                if 'wdtheader' not in tag.get('class'):
                    tags[i] = tag.text if tag.text else 'Not Found'
            raw_data[col] = tags

        raw_data['link'] = ['Not Found'] * row_count
        for i, tag in enumerate(html.find_all(['td'], {'class': f'column-link'})):
            if 'wdtheader' not in tag.get('class'):
                raw_data['link'][i] = tag.a.get('href') if tag.a else 'Not Found'

        raw_data['author_report'] = [author] * row_count
        raw_data['date_report'] = [report_date] * row_count
        raw_data['views'] = [views] * row_count
        return DataFrame.from_dict(raw_data)

    def _scrap_2017(self, url_master=URL_SITE_MASTER_TABLE_2017, driver_name='chrome',
                    start_date=datetime(2017, 1, 1).date(), end_date=datetime(2017, 12, 31).date()):

        self.set_driver(driver_name)
        if driver_name == 'chrome':
            self.driver.command_executor._commands["send_command"] = \
                ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': DESKTOP_PATH}}
            self.driver.execute("send_command", params)

        ini_date = get_ini_date(date=start_date) if isinstance(start_date, str) else start_date
        fin_date = get_fin_date(date=end_date) if isinstance(end_date, str) else end_date
        assert ini_date < fin_date, f"{ini_date} es superior a {fin_date}"
        assert ini_date.year == 2017, "Error el año de la fecha de inicio es superior a 2017"

        if ini_date.year < 2016:
            print("Warning. El año de la fecha de inicio es anterior a 2017. Se pondrá por defecto el 01/01/2017")
            ini_date = datetime(2017, 1, 1).date()
        else:
            if fin_date.year > 2017:
                print("Warning. El año de la fecha de fin es posterior a 2017. Se pondrá por defecto el 31/12/2017")
                fin_date = datetime(2017, 12, 31)

        # get desktop elements with name..
        files_on_desktop = glob.glob(os.path.join(DESKTOP_PATH, '2017 Master *.csv'))

        start = time()
        try:
            bs = self.request_url(url=url_master, javascript=False)
            download_url = bs.find(text='Google Sheet').parent.get('href')
            self.request_url(url=download_url, javascript=True)
            self.next_page(xpath_exp="//div[@id='docs-file-menu']")
            self.next_page(xpath_exp="//div[@id=':2z']")
            self.next_page(xpath_exp="//*[text()[contains(.,'.csv')]]")

            new_files_on_desktop = glob.glob(os.path.join(DESKTOP_PATH, '2017 Master *.csv'))
            timer = 0

            while len(files_on_desktop) == len(new_files_on_desktop) and timer < 10:
                new_files_on_desktop = glob.glob(os.path.join(DESKTOP_PATH, '2017 Master *.csv'))
                sleep(1)
                timer += 1
            self.driver.close()

            assert len(files_on_desktop) < len(new_files_on_desktop), "No se ha descargado el archivo"

            new_file = [f for f in new_files_on_desktop if f not in files_on_desktop][0]

            try:
                df = read_csv(new_file)
                df.loc[:, 'Date'] = to_datetime(df['Date'], format="%d/%m/%Y")
                self.df = df.loc[df["Date"].between(ini_date, fin_date), :]
                self.finish_scrapping(MASTER_2017_PATH_FILE)
                os.remove(new_file)
                log_info(logger=self.logger, title='MASTER TABLE', url=URL_SITE_MASTER_TABLE_2017, status='OK',
                         registers=0, time_scrap=time() - start, info=f'Leídos {len(self.df)} Registros')
            except Exception as err:
                shutil.move(new_file, RAW_DATA_PATH)
                print('El fichero de Master Table 2017 se ha leído pero no se ha podido filtrar. '
                      f'Se copiará directamente en {RAW_DATA_PATH}')
                log_info(logger=self.logger, title='MASTER TABLE', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                         registers=0, time_scrap=time() - start, error=err)
        except AttributeError:
            print('No se ha encontrado el link de descarga para Master Table 2017')
        except Exception as err:
            print('Ha ocurrido un error inesperado')
            log_info(logger=self.logger, title='MASTER TABLE 2017', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                     registers=0, time_scrap=time() - start, error=err)

    def _scrap_2018(self, url_master=URL_SITE_MASTER_TABLE_2018, driver_name='chrome', start_date=datetime(2018, 1, 1),
                    end_date=datetime(2018, 12, 31)):
        start = time()
        self.set_driver(driver_name)
        if driver_name == 'chrome':
            self.driver.command_executor._commands["send_command"] = \
                ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': DESKTOP_PATH}}
            self.driver.execute("send_command", params)

        ini_date = get_ini_date(date=start_date) if isinstance(start_date, str) else start_date
        fin_date = get_fin_date(date=end_date) if isinstance(end_date, str) else end_date
        assert ini_date < fin_date, f"{ini_date} es superior a {fin_date}"

        if ini_date.year > 2018:
            print("Error el año de la fecha de inicio es superior a 2018")
            self._scrap_timeline(start_date=ini_date, end_date=fin_date)
        else:
            if ini_date.year < 2017:
                print("Warning. El año de la fecha de inicio es anterior a 2017. Se pondrá por defecto el 01/01/2018")
                ini_date = datetime(2018, 1, 1).date()
            else:
                if fin_date.year > 2018:
                    print("Warning. El año de la fecha de fin es posterior a 2018. Se pondrá por defecto el 31/12/2018")
                    fin_date = datetime(2018, 12, 31)

        files_on_desktop = glob.glob(os.path.join(DESKTOP_PATH, '2018 Master *.csv'))
        try:
            # Asignamos el perfil al driver de Selenium que manejará la navegación por la URL
            self.request_url(url_master, javascript=True)
            # Averiguamos la secuencia de clicks necesarios para descargar el archivo a través del elemento dinámico
            self.next_page(xpath_exp="//span[contains(., 'CSV')]")

            new_files_on_desktop = glob.glob(os.path.join(DESKTOP_PATH, '2018 Master *.csv'))
            timer = 0

            while len(files_on_desktop) == len(new_files_on_desktop) and timer < 10:
                new_files_on_desktop = glob.glob(os.path.join(DESKTOP_PATH, '2018 Master *.csv'))
                sleep(1)
                timer += 1
            self.driver.close()

            assert len(files_on_desktop) < len(new_files_on_desktop), "No se ha descargado el archivo"

            new_file = [f for f in new_files_on_desktop if f not in files_on_desktop][0]
            try:
                df = read_csv(new_file)
                df.loc[:, 'Date'] = to_datetime(df['Date'], format="%d/%m/%Y")
                self.df = df.loc[df["Date"].between(ini_date, fin_date, inclusive=True), :]
                self.finish_scrapping(MASTER_2018_PATH_FILE)
                os.remove(new_file)
                log_info(logger=self.logger, title='MASTER TABLE', url=URL_SITE_MASTER_TABLE_2018, status='OK',
                         registers=0, time_scrap=time() - start, info=f'Leídos {len(self.df)} Registros')
            except Exception as err:
                shutil.move(new_file, RAW_DATA_PATH)
                print('El fichero de Master Table 2018 se ha leído pero no se ha podido filtrar. '
                      f'Se copiará directamente en {RAW_DATA_PATH}')
                log_info(logger=self.logger, title='MASTER TABLE', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                         registers=0, time_scrap=time() - start, error=err)

        except AttributeError:
            print('No se ha encontrado el link de descarga para Master Table 2018')
        except Exception as err:
            print('Ha ocurrido un error inesperado')
            log_info(logger=self.logger, title='MASTER TABLE 2018', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                     registers=0, time_scrap=time() - start, error=err)
