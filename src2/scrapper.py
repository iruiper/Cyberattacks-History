import os
import shutil

from time import sleep, time
from datetime import datetime
from bs4 import BeautifulSoup
from pandas import DataFrame, read_csv, to_datetime
from numpy import log

from requests import get, HTTPError
from requests.exceptions import Timeout, ConnectionError
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import Firefox, Chrome, FirefoxProfile
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.firefox.options import Options as Firefox_Options


from scrapper_utils import time_exec, log_info, check_header, transform_header, create_logger, check_dates, \
    check_download
from constants import FIELDS_NAME, URL_SITE_STATICS_TIMELINE, LOGGING_PATH_FILE, DESKTOP_PATH, RAW_DATA_PATH,\
    TIMELINE_PATH_FILE, URL_SITE_MASTER_TABLE_2018, URL_SITE_MASTER_TABLE_2017, USER_AGENT, FIREFOX_DRIVER_EXE,\
    CHROME_DRIVER_EXE, MASTER_2017_PATH_FILE, MASTER_2018_PATH_FILE


class BeautyScraper:

    def __init__(self):
        self.time = {'request_time': 0, 'wait_time': 0}
        self.logger = create_logger(LOGGING_PATH_FILE)
        self.df = DataFrame(columns=FIELDS_NAME)
        self.missing_calls = [False, False, False]
        self.request = None
        self.driver = None

    @time_exec
    def request_url(self, url, javascript=True, **wait_kwargs):
        """
        Función que sirve para realizar peticiones http. En función del valor del parámetro javascript, la petición se
        realizará utilizando la librería selenium o la librería requests.

        Se devolverá un objeto BeautifulSoup con el código html de la URL.

        :param url: dirección url sobre la que se realizará la petición
        :param javascript: Si es True, se realizará una petición http a través de la librería selenium, la cual perimte
                           cargar los elemetos javascript de la página web. Si es False, se utilziará la librería
                           requests, que carga el html sin su contenido javascript.
        :param wait_kwargs: Parámetros adicionales utilizados para controlar que el contenido javascript se ha cargado
                            adecuadamente antes de devolver el html.
        :return: objeto BeautifulSoup con el html de la URL.
        """

        # Se inicia un bucle que comprueba el estado de la petición a la página web. El máximo de intentos permitidos
        # son 4.
        connect_atempts = 1
        while connect_atempts < 4:
            try:
                # Se realiza la petición http mediante el método get de la librería requests. Para ello se modifica el
                # user agent para simular que la petició es realizada por un humano y no un script.
                # Como el objetivo es chequear el estado de conexión, no es necesario cargar el JavaScript.
                self.request = get(url, headers={'User-Agent': USER_AGENT})
                # Si la conexión no es exitosa (código <> 2XX) se lanza una excepción HTTPError. En caso contrario,
                # se continua el código y se para el bucle.
                self.request.raise_for_status()
                break
            except Timeout:
                # Si la connexión falla debido a que se ha superado el Timeout por defecto, se incrementa el número de
                # intentos de conexión, se loggea el error y se esperan 5 segundos antes de realizar la siguiente
                # petición.
                info_txt = f'Timeout superado al realizar la petición a {url}.' + \
                       f'Se realizará otra petición en 5 segs. Peticion {connect_atempts} de 3'
                log_info(logger=self.logger, title='', url=url, status='KO', registers=0, time_scrap=0, info=info_txt,
                         req_time=f"{self.time['request_time']:.2f}")
                connect_atempts += 1
                sleep(5)
            except HTTPError:
                # Si la connexión falla debido a un problema de conexión (por ejemplo un error 5XX), se incrementa el
                # número de intentos de conexión, se loggea el error y se esperan 5 segundos antes de realizar la
                # siguiente petición.
                info_txt = f'Error de conexión {self.request.status_code} superado al realizar la petición a {url}.' + \
                           f'Se realizará otra petición en 5 segs. Peticion {connect_atempts} de 3'
                log_info(logger=self.logger, title='', url=url, status='KO', registers=0, time_scrap=0, info=info_txt,
                         req_time=f"{self.time['request_time']:.2f}")
                connect_atempts += 1
                sleep(5)
            except ConnectionError:
                # Si la connexión falla debido a un problema de connectividad a internet (por ejemplo, no existe
                # connexión a internet) se incrementa el número de intentos de conexión, se loggea el error y se
                # esperan 5 segundos antes de realizar la siguiente petición.
                info_txt = f'No se puede establecer una conezión con la {url}.' + \
                           f'Se realizará otra petición en 5 segs. Peticion {connect_atempts} de 3'
                log_info(logger=self.logger, title='', url=url, status='KO', registers=0, time_scrap=0, info=info_txt,
                         req_time=f"{self.time['request_time']:.2f}")
                connect_atempts += 1
                sleep(5)

        # Se comprueba que el motivo de finalización del bucle ha sido una conexión exitosa y no porque se ha llegado
        # al número máximo de intentos fallidos.
        assert connect_atempts < 4, f"Máximo intento de connexiones superado. No se puede acceder a {url}"
        # En caso de conexión exitosa, se realiza la petición en función de si se debe cargar el JavaScript contenido
        # en la URL o no.
        if javascript:
            self.driver.get(url)
            # Si se ha especificado una condición de espera, se detiene el proceso hasta que se cumple. El Tout máximo
            # de espera son 10 segundos. En caso contrario se lanza una exception por Tout superado.
            if 'wait_contidion' in wait_kwargs:
                WebDriverWait(self.driver, 10).until(wait_kwargs['wait_contidion'])
            return BeautifulSoup(self.driver.page_source,  'html.parser')
        else:
            return BeautifulSoup(self.request.content, 'html.parser')

    @time_exec
    def next_page(self, xpath_exp, **wait_kwargs):
        """
        Función que sirve para interactuar con un elemento contenido en una página web mediante la librería selenium.
        La interacción consiste en hacer click en un elemento indicado a través de su xpath

        :param xpath_exp: expressión xpath para identificar el elemento
        :param wait_kwargs: Parámetros adicionales utilizados para controlar que el contenido javascript se ha cargado
                            adecuadamente antes de devolver el contenido html actualizado.
        :return: objeto BeautifulSoup con el html actualizado después de realizar la interacción con el elemento
                especificado en xpath.
        """

        # Se busca el elemento a clicar mediante el xpath
        self.driver.find_element_by_xpath(xpath_exp).click()

        # Si se ha especificado una condición de espera, se detiene el proceso hasta que se cumple. El Tout máximo
        # de espera son 10 segundos. En caso contrario se lanza una exception por Tout superado.
        if 'wait_contidion' in wait_kwargs:
            WebDriverWait(self.driver, 10).until(wait_kwargs['wait_contidion'])
        return BeautifulSoup(self.driver.page_source,  'html.parser')

    def writer_download(self, input_, output, start_date, end_date):
        """
        Función que sirve para procesar el archivo contenido en la ruta input_. El archivo se abre y se filtra
        mediante la columna 'Date', descartando aquellos registros no contenidos en el rango start_date y end_date.
        El fichero procesado se guarda en output. Finalmente, el archivo contenido en input_ se elimina.

        En caso de suceder algún error, se copia y se pega el archivo input a la carepta .\Data\00_RAW.

        Esta función, tiene el objetivo de procesar los archivos Master Table 2018 y Master Table 2017 almacenados
        en el escritorio y guardarlos en la carpeta de Data del proyecto.

        :param input_: Ruta del archivo de origen.
        :param output:  Ruta del archivo de destino
        :param start_date: Fecha mínima contenida en los datos
        :param end_date: Fecha máxmia contenida en los datos
        """
        try:
            # Se lee el fichero a través de la librería pandas. El archivo debe ser .csv
            df = read_csv(input_)
            # Se transforma el tipo de datos de ini_date y fin_date, conviertiendolos a datetime.
            ini_date = datetime(start_date.year, start_date.month, start_date.day)
            fin_date = datetime(end_date.year, end_date.month, end_date.day)
            # Se transforma el tipo de datos de la columna date contenida en el archivo csv
            df.loc[:, 'Date'] = to_datetime(df['Date'], format="%d/%m/%Y")
            # Se realiza el procesado del archivo, filtrando aquellos registros contenidos entre las fechas deseadas.
            self.df = df.loc[df["Date"].between(ini_date, fin_date, inclusive=True), :]
            # Se finaliza el proceso de scrapping
            self.finish_scrapping(output)
            # Se elimina el archivo input_
            os.remove(input_)
        except Exception as err:
            # En caso de suceder un error inesperado, se corta y pega el archivo a la ruta .\Data\00_raw y se
            # informa del error.
            shutil.move(input_, RAW_DATA_PATH)
            raise AssertionError(f"Ha sucedido un error ineseperado. Se copiará {input} en {RAW_DATA_PATH}\n{err}")

    def set_driver(self, driver):
        """
        Función que sirve para iniciar el driver de selenium deseado.

        :param: driver: Indica el driver a iniciar. valores posibles: 'chrome' o 'firefox'.
        """

        # Si ya existe un driver, se finaliza.
        if not self.driver:
            self.close_driver()

        # Si se decide inicializar el driver de google Chrome.
        if str(driver).lower() == 'chrome':
            # Se declaran las opciones del driver para ocultar la ventana de la aplicación, de esta forma, el proceso es
            # 'invisible' para el usuario.
            chrome_options = Chrome_Options()
            chrome_options.add_argument("--headless")
            # En modo de incógnito, google chrome no deja descargar archivos. A través de las siguientes constantes
            # se habilita la descarga de archivos. El directorio de descarga predeterminado será el escritorio.
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {"download.default_directory": DESKTOP_PATH,
                                                             "download.prompt_for_download": False,
                                                             "download.directory_upgrade": True,
                                                             "safebrowsing_for_trusted_sources_enabled": False,
                                                             "safebrowsing.enabled": False})
            # Se crea driver y se inicializa indicando la ruta del ejecutable y las opciones predefinidas anteriormente.
            self.driver = Chrome(executable_path=CHROME_DRIVER_EXE, chrome_options=chrome_options)
            # Se lanza el comando que permite la descarga de archivos en modo de incógnito.
            self.driver.command_executor._commands["send_command"] = \
                ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': DESKTOP_PATH}}
            self.driver.execute("send_command", params)

        # Si se decide inicializar el driver de Firefox.
        elif str(driver).lower() == 'firefox':
            # Se crea un perfil para definir la configuración a seguir durante la conexión
            firefox_profile = FirefoxProfile()
            # Se deshabilita el pop-up emergente preguntando sobre si deseamos guardar el archivo.
            # Válido para csv y documentos txt
            firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
            # Los archivos descargados se almacenan en el escritorio
            firefox_profile.set_preference("browser.download.folderList", 0)
            firefox_profile.set_preference("browser.download.dir", DESKTOP_PATH)
            # Se oculta la ventana de Firefox, de esta forma, el proceso es 'invisible' para el usuario.
            firefox_options = Firefox_Options()
            firefox_options.add_argument('--headless')

            # Se crea driver y se inicializa indicando la ruta del ejecutable y las opciones predefinidas anteriormente.
            self.driver = Firefox(firefox_profile=firefox_profile, executable_path=FIREFOX_DRIVER_EXE,
                                  options=firefox_options)

        # En caso de que el driver no sea 'Chrome' o 'Firefox' se printea un mensaje informativo.
        else:
            print(f'{driver} no se corresponde con uno de los siguientes drivers: chrome o firefox.')

    def close_driver(self):
        # Función que sirve para eliminar, en caso de existir, el driver de selenium iniciado durante el proceso de
        # scrapping

        if self.driver:
            # Se cierra la sesión abierta mediante la librería de selenium eliminando las preferencias definidas.
            self.driver.quit()
            # Se resetea el driver.
            self.driver = None

    def set_request_time(self, time_call):
        """
        Función que almacena el tiempo necesario para realizar una llamada y actualiza el tiempo de espera entre
        peticiones.

        :param time_call: tiempo en segundos requerido para realizar la última petición http.
        """

        # Se almacena el tiempo de petición
        self.time['request_time'] = time_call
        # Se actualiza el tiempo de peticiónes. Se ha decidio utilizar un tiempo de espera proporcional al logarítmo
        # neperiano para reducir el impacto de peticiones que se demoren mucho.
        self.time['wait_time'] = time_call * log(time_call + 1)

    def finish_scrapping(self, file_name):
        """
        Función que sirve para escribir los datos obtenidos durante el proceso de scrapping. Estos datos se almacenan
        en formato csv.

        :param file_name: nombre del archivo de salida
        """

        #Escritura de los datos a formato csv con separador de campos: punto-coma ';' y, separador decimal: coma ','.
        self.df.to_csv(file_name, index=False, decimal=',', sep=";")
        print(f'SCRAPPING {file_name} FINALIZADO')

    def start_scrapping(self, ini_date=datetime(2017, 1, 1).date(), fin_date=datetime.now().date(),
                        driver_name='chrome'):
        """
        Función que sirve para realizar el scrapping de la página web. Dependiendo de las fechas de entrada se llama
        a las funciones extractoras correspondientes para realizar el rasgado del Timeline, Master Table 2017 y Master
        Table 2018 adecuando las fechas para el procesado de estas funciones.

        :param ini_date: fecha de inicio del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: 01/01/2017.
        :param fin_date: fecha de finalización del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: fecha de hoy
        :param driver_name: nombre del driver a utilizar para cargar el contenido JavaScript mediante selenium. Debe
                            contener los valores Firefox o Chrome.
        """

        # Se validan que las fechas de entrada sean válidas.
        ini_date, fin_date = check_dates(ini_date=ini_date, fin_date=fin_date)

        # Si la fecha de inicio es posterior al 31/12/2018, únicamente se realizará el scrapping del timeline entre
        # ini_date y fin_date.
        if ini_date.year > 2018:
            self._scrap_timeline(start_date=ini_date, end_date=fin_date, driver_name=driver_name)

        # Si la fecha de inicio está entre 01/01/2018 al 31/12/2018, se realizará el scrapping de Master Table 2018 y,
        # dependiendo de la fecha de fin, tambien se deberá realizar el scraping del timeline.
        elif 2017 < ini_date.year <= 2018:

            # Si la fecha de fin es superior al 31/12/2018 se debe scrapear Master Table 2018 (fecha ini - 31/12/2018)
            # y el Timeline (01/01/2019 - fecha fin).
            if fin_date.year > 2018:
                self._scrap_timeline(start_date=datetime(2019, 1, 1).date(), end_date=fin_date, driver_name=driver_name)
                self._scrap_2018(start_date=ini_date, driver_name=driver_name)

            # En caso contrario, solo se debe scrapear Master Table 2018 entre las fechas de inicio y fin definidas
            else:
                self._scrap_2018(start_date=ini_date, end_date=fin_date, driver_name=driver_name)

        # Si la fecha de inicio está entre 01/01/2017 al 31/12/2017, se realizará el scrapping de Master Table 2017 y,
        # dependiendo de la fecha de fin, tambien se deberá realizar el scraping de Mater Table 2018 o Timeline o ambos.
        elif 2016 < ini_date.year <= 2017:

            # Si la fecha de fin es superior al 31/12/2018 se debe scrapear Master Table 2017 (fecha_ini - 31/12/2017),
            # Master Table 2018 (01/01/2018 - 31/12/2018) y el Timeline (01/01/2019 - fecha fin).
            if fin_date.year > 2018:
                self._scrap_timeline(start_date=datetime(2019, 1, 1).date(), end_date=fin_date, driver_name=driver_name)
                self._scrap_2018(driver_name=driver_name)
                self._scrap_2017(start_date=ini_date, driver_name=driver_name)

            # Si la fecha de fin es superior al 31/12/2017 se debe scrapear Master Table 2017 (fecha_ini - 31/12/2017) y
            # Master Table 2018 (01/01/2018 - fecha fin).
            elif fin_date.year > 2017:
                self._scrap_2018(end_date=fin_date, driver_name=driver_name)
                self._scrap_2017(start_date=ini_date, driver_name=driver_name)

            # En caso contrario, solo se debe scrapear Master Table 2017 entre las fechas de inicio y fin definidas
            else:
                self._scrap_2017(start_date=ini_date, end_date=fin_date, driver_name=driver_name)

        # Si la fecha de inicio es anterior a 01/01/2017, dependiendo de la fecha de fin, se realizará el scrapping de
        # Master Table 2017, Mater Table 2018 o Timeline o todos.
        elif ini_date.year <= 2016:

            # Si la fecha de fin es superior al 31/12/2018 se debe scrapear Master Table 2017 (01/01/2017 - 31/12/2017),
            # Master Table 2018 (01/01/2018 - 31/12/2018) y el Timeline (01/01/2019 - fecha fin).
            if fin_date.year > 2018:
                self._scrap_timeline(start_date=datetime(2019, 1, 1).date(), end_date=fin_date, driver_name=driver_name)
                self._scrap_2018(driver_name=driver_name)
                self._scrap_2017(driver_name=driver_name)

            # Si la fecha de fin es superior al 31/12/2017 se debe scrapear Master Table 2017 (01/01/2017 - 31/12/2017)
            # y Master Table 2018 (01/01/2018 - fecha fin).
            elif fin_date.year > 2017:
                self._scrap_2018(end_date=fin_date, driver_name=driver_name)
                self._scrap_2017(driver_name=driver_name)

            # Si la fecha de fin es superior al 31/12/2016 se debe scrapear Master Table 2017 (01/01/2017 - fecha fin)
            elif fin_date.year > 2016:
                self._scrap_2017(end_date=fin_date, driver_name=driver_name)

            # Si la fecha de fin es anterior a 01/01/2017 no se realziará ningún scrapeado, ya que no está codificado.
            else:
                print('no se puede generar el scrapping para fechas anteriores al 2016')

    def _scrap_timeline(self, start_date=datetime(2019, 1, 1).date(), end_date=datetime.now().date(),
                        driver_name='chrome'):

        self.set_driver(driver_name)
        ini_date, fin_date = check_dates(ini_date=start_date, fin_date=end_date)
        url = URL_SITE_STATICS_TIMELINE
        url_dict = {}

        if ini_date.year < 2019:
            print("Warning. El año de la fecha de inicio es anterior a 2019. Se pondrá por defecto el 01/01/2019")
            ini_date = datetime(2019, 1, 1).date()

        try:
            html_bs = self.request_url(url, javascript=False)
        except Exception as err:
            log_info(logger=self.logger, title='TIMELINE', url=url, status='KO', registers=0, time_scrap=0, error=err,
                     req_time=f"{self.time['request_time']:.2f}")
        else:
            while True:
                try:
                    url_dict[url] = {}
                    for tags in html_bs.find_all('h2'):
                        start = time()
                        if tags.findChild('a'):
                            title = tags.a.get('title') if tags.a.has_attr('title') else 'No Title'
                            link = tags.a.get('href') if tags.a.has_attr('href') else 'No URL'
                        else:
                            title, link = 'No Title', 'No URL'
                            log_info(logger=self.logger, title='', url=url, status='KO', registers=0, time=0,
                                     info=f'Existe un header en {url} sin un hijo (tag "a"). Posible modificación HTML',
                                     req_time=f"{self.time['request_time']:.2f}")

                        url_dict[url][title] = link
                        read, follow = check_header(str_time=transform_header(title), frmt_time='%d-%B-%Y',
                                                    start=ini_date, end=fin_date)
                        if read:
                            try:
                                report_data, total_entries = self._scrap_report(url=link, title_report=title)
                            except Exception as err:
                                log_info(logger=self.logger, title=title, url=link, status='KO', registers=0,
                                         time_scrap=f"{time() - start:.2f}", error=err,
                                         req_time=f"{self.time['request_time']:.2f}")
                            else:
                                self.df = self.df.append(report_data, ignore_index=False)
                                log_txt = f'Leídas {len(report_data)} de {total_entries}'
                                log_info(logger=self.logger, title=title, url=link, status='OK',
                                         registers=len(report_data), time_scrap=f"{time() - start:.2f}", info=log_txt,
                                         req_time=f"{self.time['request_time']:.2f}")
                        else:
                            if not follow:
                                self.missing_calls.pop(0)
                                self.missing_calls.append(True)

                            log_info(logger=self.logger, title=title, url=link, status='INFO', registers=0,
                                     time_scrap=f"{time() - start:.2f}", info=f'Report {title} en {url} excluido',
                                     req_time=f"{self.time['request_time']:.2f}")
                            assert not all(self.missing_calls), "No existen más reports para el periodo seleccionado"

                    txt_error = "No existen más tags '{name}' para continuar con el scrapping. " \
                                "Posible modificación del HTML"
                    assert html_bs.find(class_='previous'), txt_error.format(name='<class=previous>')
                    assert html_bs.find(class_='previous').find_next('a'), txt_error.format(name='<class=previous> <a>')
                    assert html_bs.find(class_='previous').find_next('a').has_attr('href'), \
                        txt_error.format(name='<class=previous> <a, href>')

                    url = html_bs.find(class_='previous').find_next('a').get('href')
                    html_bs = self.request_url(url=url, javascript=False)

                except Exception as err:
                    log_info(logger=self.logger, title='TIMELINE', url=url, status='KO', registers=0, time_scrap=0,
                             error=err, req_time=f"{self.time['request_time']:.2f}")
                    break

            self.finish_scrapping(file_name=TIMELINE_PATH_FILE)
        self.close_driver()

    def _scrap_report(self, url, title_report):
        report_df = DataFrame(columns=FIELDS_NAME)
        html_bs = self.request_url(url, javascript=True,
                                   wait_contidion=ec.presence_of_element_located((By.XPATH, '//table[@id="table_1"]')))
        total_data, report_date, author, views = 'Not Found', 'Not Found', 'Not Found', 'Not Found'
        if html_bs.find_all(class_='dataTables_info'):
            # Como dataTables info tiene un único hijo del tipo NavigableString, se pude acceder al texto mediante
            # el atributo string
            total_text = html_bs.find(class_='dataTables_info').string
            if total_text:
                total_numbers = [s for s in total_text.split() if s.isdigit()]
                total_data = total_numbers[-1] if len(total_numbers) > 0 else 'Not Found'
            else:
                total_data = 'Not Found'

        if html_bs.find('time'):
            report_date = html_bs.find('time').get('datetime') if html_bs.find('time').has_attr('datetime') \
                else 'Not Found'

        if html_bs.find('a', {'class': 'url fn n'}):
            author = html_bs.find('a', {'class': 'url fn n'}).string

        if html_bs.find('span', {'class': 'post-views-count'}):
            views = html_bs.find('span', {'class': 'post-views-count'}).string

        while True:
            try:
                assert html_bs.find('tbody'), 'No existe el tag <tbody> de la tabla. Posible modificación HTML'
                table_df = self._scrap_table(html=html_bs, author=author, report_date=report_date, views=views)
                report_df = report_df.append(table_df, ignore_index=True)

                txt_error = "No existen el tag '%s'. Posible modificación del HTML"
                assert html_bs.find(class_='paginate_button current'), txt_error % '<class=paginate_button current'
                current_page_number = html_bs.find(class_='paginate_button current').string
                assert current_page_number.isdigit(), "El tag '%s' no contiene un número de página correcto."
                next_page = str(int(current_page_number) + 1)
                html_bs = \
                    self.next_page(xpath_exp='//a[@class="paginate_button next"]',
                                   wait_contidion=ec.text_to_be_present_in_element(
                                       (By.XPATH, '//a[@class="paginate_button current"]'), next_page))
            except AssertionError as err:
                log_info(logger=self.logger, title=title_report, url=url, status='KO', registers=0, time_scrap=0,
                         error=err, req_time=f"{self.time['request_time']:.2f}")
                break
            except NoSuchElementException:
                break
            except ElementClickInterceptedException:
                break

        return report_df, total_data

    @staticmethod
    def _scrap_table(html, author=None, report_date=None, views=None):
        raw_data = {f: [] for f in FIELDS_NAME}

        for row in html.find('tbody').find_all(['tr'], {'role': 'row'}):
            raw_data['author_report'] = author
            raw_data['date_report'] = report_date
            raw_data['views'] = views

            for col in FIELDS_NAME[:-4]:
                texto = row.find(['td'], {'class': f'column-{col.replace("_", "-")}'})
                raw_data[col].append(texto.text if texto else 'Not Found')

            tag_link = row.find(['td'], {'class': f'column-link'})
            if tag_link.find('a'):
                raw_data['link'] = tag_link.a.get('href') if tag_link.a.has_attr('href') else 'Not Found'
            else:
                raw_data['link'] = 'Not Found'
        return DataFrame.from_dict(raw_data)

    def _scrap_2017(self, url_master=URL_SITE_MASTER_TABLE_2017, driver_name='chrome',
                    start_date=datetime(2017, 1, 1).date(), end_date=datetime(2017, 12, 31).date()):

        ini_date, fin_date = check_dates(ini_date=start_date, fin_date=end_date)
        assert ini_date.year <= 2017, "Error el año de la fecha de inicio es superior a 2017"

        if ini_date.year < 2016:
            print("Warning. El año de la fecha de inicio es anterior a 2017. Se pondrá por defecto el 01/01/2017")
            ini_date = datetime(2017, 1, 1).date()
        else:
            if fin_date.year > 2017:
                print("Warning. El año de la fecha de fin es posterior a 2017. Se pondrá por defecto el 31/12/2017")
                fin_date = datetime(2017, 12, 31)

        start = time()
        try:
            self.set_driver(driver_name)
            bs = self.request_url(url=url_master, javascript=False)
            assert bs.find(text='Google Sheet'), 'No se ha encontrado texto: "Google Sheet". Posible modificación HTML'
            tag_download_url = bs.find(text='Google Sheet').parent
            download_url = tag_download_url.get('href') if tag_download_url.has_attr('href') else ''
            self.request_url(url=download_url, javascript=True,
                             wait_contidion=ec.element_to_be_clickable((By.XPATH, "//div[@id='docs-file-menu']")))
            self.next_page(xpath_exp="//div[@id='docs-file-menu']",
                           wait_contidion=ec.element_to_be_clickable((By.XPATH, "//div[@id=':2z']")))
            self.next_page(xpath_exp="//div[@id=':2z']",
                           wait_contidion=ec.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'.csv')]]")))
            self.next_page(xpath_exp="//*[text()[contains(.,'.csv')]]")

            new_file = check_download(searh_file='2017 Master *.csv', file_size=300000)
            self.writer_download(input_=new_file, output=MASTER_2017_PATH_FILE, start_date=ini_date, end_date=fin_date)
            log_info(logger=self.logger, title='MASTER TABLE 2017', url=URL_SITE_MASTER_TABLE_2017, status='OK',
                     registers=len(self.df), time_scrap=f"{time() - start:.2f}", info=f'Carga Completa',
                     req_time=f"{self.time['request_time']:.2f}")

        except AssertionError as err:
            log_info(logger=self.logger, title='MASTER TABLE 2017', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")
        except Exception as err:
            print('Ha ocurrido un error inesperado')
            log_info(logger=self.logger, title='MASTER TABLE 2017', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")
        self.close_driver()

    def _scrap_2018(self, url_master=URL_SITE_MASTER_TABLE_2018, driver_name='chrome',
                    start_date=datetime(2018, 1, 1).date(), end_date=datetime(2018, 12, 31).date()):

        start = time()
        ini_date, fin_date = check_dates(ini_date=start_date, fin_date=end_date)

        assert ini_date.year <= 2018,  "Error el año de la fecha de inicio es superior a 2018"

        if ini_date.year < 2018:
            print("Warning. El año de la fecha de inicio es anterior a 2018. Se pondrá por defecto el 01/01/2018")
            ini_date = datetime(2018, 1, 1).date()
        else:
            if fin_date.year > 2018:
                print("Warning. El año de la fecha de fin es posterior a 2018. Se pondrá por defecto el 31/12/2018")
                fin_date = datetime(2018, 12, 31).date()

        try:
            self.set_driver(driver_name)
            # Asignamos el perfil al driver de Selenium que manejará la navegación por la URL
            self.request_url(url_master, javascript=True,
                             wait_contidion=ec.element_to_be_clickable((By.XPATH, "//span[contains(., 'CSV')]")))
            # Averiguamos la secuencia de clicks necesarios para descargar el archivo a través del elemento dinámico
            self.next_page(xpath_exp="//span[contains(., 'CSV')]")

            new_file = check_download(searh_file='2018 Master *.csv', file_size=300000)
            self.writer_download(input_=new_file, output=MASTER_2018_PATH_FILE, start_date=ini_date, end_date=fin_date)
            log_info(logger=self.logger, title='MASTER TABLE 2018', url=URL_SITE_MASTER_TABLE_2018, status='OK',
                     registers=len(self.df), time_scrap=f"{time() - start:.2f}", info=f'Carga Completa',
                     req_time=f"{self.time['request_time']:.2f}")

        except AssertionError as err:
            log_info(logger=self.logger, title='MASTER TABLE 2018', url=URL_SITE_MASTER_TABLE_2018, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")

        except Exception as err:
            print('Ha ocurrido un error inesperado')
            log_info(logger=self.logger, title='MASTER TABLE 2018', url=URL_SITE_MASTER_TABLE_2018, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")
        self.close_driver()
