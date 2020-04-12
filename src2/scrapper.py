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

        # Escritura de los datos a formato csv con separador de campos: punto-coma ';' y, separador decimal: coma ','.
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
        """
        Función que sirve para realizar el scraping de los reports contenidos en el timeline. Los reports rasgados
        estarán contenidos entre las fechas start_date y end_date.

        El rasgado de los reports se hará a partir de la página de inicio del timeline y retrocediendo en el tiempo. Es
        decir, se accede por defecto a https://www.hackmageddon.com/category/security/cyber-attacks-timeline y se va
        retroceciendo hacía las páginas anteriores para obtener la información deseada.

        Para evitar tener una araña infinita, existe el atributo self.missing_calls que sirve para detectar reports
        anteriores a la fecha de inicio. De esta forma, al alcanzar el tercer report anterior a fecha_ini, se para el
        proceso. Este parámetro, por lo tanto, sirve para determinar un profundidad de red variable adaptandonos al
        periodo de tiempo requerido por el usuario.

        :param start_date: fecha de inicio del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: 01/01/2019.
        :param end_date: fecha fin del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: fecha de hoy
        :param driver_name: nombre del driver a utilizar para cargar el contenido JavaScript mediante selenium. Debe
                            contener los valores Firefox o Chrome.
        """

        # Inicialización del driver de selenium
        self.set_driver(driver_name)
        # Validación de las fechas de inicio y de fin introducidas como paráemtros.
        ini_date, fin_date = check_dates(ini_date=start_date, fin_date=end_date)
        url = URL_SITE_STATICS_TIMELINE

        # Si la fecha de inicio es anterior al 01/01/2019, se corrige por defecto y se asigna la fecha 01/01/2019
        # mostrando un mensaje de alerta
        if ini_date.year < 2019:
            print("Warning. El año de la fecha de inicio es anterior a 2019. Se pondrá por defecto el 01/01/2019")
            ini_date = datetime(2019, 1, 1).date()

        try:
            # Se obtiene el html de la página del timeline, sobre este html se parsearán los títulos de los distintos
            # reports sobre los cuales se obtendrá la información. Como no es necesario cargar contenido javascript,
            # se llama la función con el parametro a False.
            html_bs = self.request_url(url, javascript=False)
        except Exception as err:
            # En caso de suceder algún error inesperado, se informa el log de errores y se detiene la ejecución.
            log_info(logger=self.logger, title='TIMELINE', url=url, status='KO', registers=0, time_scrap=0, error=err,
                     req_time=f"{self.time['request_time']:.2f}")
        else:
            while True:
                try:
                    # Los títulos de los distintos reports están contenidos a través de los tags 'h2'.
                    for tags in html_bs.find_all('h2'):

                        # Se inicia el contador que permitirá tener trazabilidad del tiempo de rasgado para cada report
                        start = time()

                        # Los tags h2 tienen como descendiente directo el tag 'a' que contiene como atributos title
                        # (título del report) y href (dirección url del report).
                        # En caso de que no se encuentren dichos tags o atributos, se ponen por defecto los valores No
                        # Title y No URL. Adicionalmente, se informará el log de errores advirtiendo de una posible
                        # modificaciónn en el codigo html.
                        if tags.findChild('a'):
                            title = tags.a.get('title') if tags.a.has_attr('title') else 'No Title'
                            link = tags.a.get('href') if tags.a.has_attr('href') else 'No URL'
                        else:
                            title, link = 'No Title', 'No URL'
                            log_info(logger=self.logger, title='', url=url, status='KO', registers=0, time=0,
                                     info=f'Existe un header en {url} sin un hijo (tag "a"). Posible modificación HTML',
                                     req_time=f"{self.time['request_time']:.2f}")

                        # Una vez obtenido el título del report, se procesará para determinar si el report es válido
                        # comprobando que la fecha esta contenida entre ini_date y fin_date.

                        # En el timeline existen dos tipos de reports. Los quinzenales que presentan un formato de
                        # título "%d_1-%d_2 %b %Y Cyber Attacks Timeline" y los agregados, con un formato distinto.

                        # En nuestro caso, nos interesa obtener la información quinzenal y no agregada. Por este motivo,
                        # se realiza una validación de las títulos encontrados mediante la función check_header. Esta
                        # función, comprueba que el formato de título y la fecha contenida en él, son válidas.

                        # En caso de tener un título válido (formato y fecha), los parámetros read y follow serán True.
                        # En caso de tener un título válido, pero con fecha posterior a la fecha de fin, el parámetro
                        # read sera False y el parámetro follow será True. Ya que, recordemos que se hace un scraping
                        # hacía 'atras en el tiempo' y se debe indicar al proceso de rasgado que continue hasta alcanzar
                        # el primer report válido.
                        # En caso de no tener un título válido en cuanto a formato o fechas, tanto read como follow
                        # serán False.
                        read, follow = check_header(str_time=transform_header(title), frmt_time='%d-%B-%Y',
                                                    start=ini_date, end=fin_date)

                        if read:
                            # Si el título es válido se resetea el contandor de reports fallidos. Este reseteo se
                            # realiza para evitar acumular intentos fallidos producidos por reports mensuales o anuales
                            # (aquellos reports cuya agregación es diferente a la quinzenal).
                            self.missing_calls = [False] * 3
                            try:
                                # Si el título es válido, se realizará el scrapping del report, passando como parámetro
                                # la url contenida en la variable link.
                                report_data, total_entries = self._scrap_report(url=link, title_report=title)
                            except Exception as err:
                                # En caso de suceder algún error durante el rasgado del report, se informa del proceso
                                # en el logging del programa y se continua con el siguiente rerpot a rasgar (en caso de
                                # existir).
                                log_info(logger=self.logger, title=title, url=link, status='KO', registers=0,
                                         time_scrap=f"{time() - start:.2f}", error=err,
                                         req_time=f"{self.time['request_time']:.2f}")
                            else:
                                # En caso de realizarse correctamente el scrapping del report, se añaden los datos
                                # rasgados a los almacenados previamente. Además, se informa del éxito en el logging,
                                # informando del número de registros leídos correctamente.
                                self.df = self.df.append(report_data, ignore_index=False)
                                log_txt = f'Leídas {len(report_data)} de {total_entries}'
                                log_info(logger=self.logger, title=title, url=link, status='OK',
                                         registers=len(report_data), time_scrap=f"{time() - start:.2f}", info=log_txt,
                                         req_time=f"{self.time['request_time']:.2f}")
                        else:
                            # En caso de que el título no sea válido y, además no se deba continuar, se actualiza el
                            # contador de 'reports fallidos'.
                            if not follow:
                                self.missing_calls.pop(0)
                                self.missing_calls.append(True)

                            # Se informa al usuario de la exclusión del título. De esta forma se puede tener un control
                            # y detectar si se han producido cambios en el formato de los títulos.
                            log_info(logger=self.logger, title=title, url=link, status='INFO', registers=0,
                                     time_scrap=f"{time() - start:.2f}", info=f'Report {title} en {url} excluido',
                                     req_time=f"{self.time['request_time']:.2f}")

                            # En caso de alcanzar el máximo número de reports no válidos, se finaliza el scrapping
                            # del timeline.
                            assert not all(self.missing_calls), "No existen más reports para el periodo seleccionado"

                    # Una vez se han scrapeado todas las cabeceras, se debe navegar hacía la siguiente página del
                    # timeline, es decir, la página prévia.
                    # Para ello, es necesario obtener su dirección URL. Esta, se encuentra en el tag cuyo atributo es
                    # class=previous. Este tag, tiene un tag hijo del tipo 'a' que contiene el atributo 'href' cuyo
                    # valor es la dirección URL deseada.

                    # A continuación se realizan validaciones para obtener dicho tag. En caso de no encontrarse,
                    # se lanza un error y se avisa al usuario de una posible modificación del HTML.
                    txt_error = "No existen más tags '{name}' para continuar con el scrapping. " \
                                "Posible modificación del HTML"
                    assert html_bs.find(class_='previous'), txt_error.format(name='<class=previous>')
                    assert html_bs.find(class_='previous').find_next('a'), txt_error.format(name='<class=previous> <a>')
                    assert html_bs.find(class_='previous').find_next('a').has_attr('href'), \
                        txt_error.format(name='<class=previous> <a, href>')

                    # En caso de existir dicho tag, se realiza la petición html y se sigue con el scraping en la
                    # siguiente página.
                    url = html_bs.find(class_='previous').find_next('a').get('href')
                    html_bs = self.request_url(url=url, javascript=False)

                except Exception as err:
                    # En caso de existir algún error inesperado, se finaliza el scrapping del timeline y se
                    # informa al usuario.
                    log_info(logger=self.logger, title='TIMELINE', url=url, status='KO', registers=0, time_scrap=0,
                             error=err, req_time=f"{self.time['request_time']:.2f}")
                    break

            # Una vez finalizado el rasgado del time_line, se almacenan los resultados mediante finish_scrapping
            self.finish_scrapping(file_name=TIMELINE_PATH_FILE)

        # Se cierra el driver de selenium
        self.close_driver()

    def _scrap_report(self, url, title_report):
        """
        Función que sirve para rasgar la información de los reports quinzenales. Para conseguir tal objetivo, es
        necesario interaccionar con los elementos javascript presentes en la web.

        :param url: dirección URL del report a scrapear
        :param title_report: Título del report
        :return: dataframe con la información rasgada
        """

        # Se crea un dataframe vacío que contendrá la información rasgada.
        report_df = DataFrame(columns=FIELDS_NAME)

        # Se realiza la petición http a la dirección web contenida en la variable URL. En este caso, es necesario
        # cargar el contenido javascript de la página.
        # Adicionalmente, es necesario asegurar que se carga el contenido de la pagina necesario. En concreto, los datos
        # contenidos en un objeto BeautifulSoup de la clase 'Table'. Este objeto 'Table' tiene el atributo id="table_1".
        html_bs = self.request_url(url, javascript=True,
                                   wait_contidion=ec.presence_of_element_located((By.XPATH, '//table[@id="table_1"]')))

        # A continuación, antes de realizar el rasgado de la tabla, es necesario obtener la información relacionada
        # con el autor, la fecha de report, el número de visualizaciones del articulo y el número total de registros que
        # almacena la tabla.
        # Este último parámetro, será utilizado para validar los datos leídos ante la datos totales.

        # Primero, se asigna el valor Not Found a las variables. Al asignar como Not Found estos valores, al revisar
        # los datos extraídos por el proceso, se pueden detectar incosistencias y revisar si el contenido HTML ha sido
        # modificado.
        total_data, report_date, author, views = 'Not Found', 'Not Found', 'Not Found', 'Not Found'

        # El número total de registros está almacenado en forma de NavigableString en un objeto BeautifulSoup que tiene
        # el atributo class='dataTable_info'.
        if html_bs.find_all(class_='dataTables_info'):

            # En caso de encontrar tal objeto, se deberá acceder al texto contenido en él. Como el objeto únicamente
            # tiene un único hijo del tipo NavigableString, se pude acceder a él mediante el atributo string.
            total_text = html_bs.find(class_='dataTables_info').string
            if total_text:
                # En caso de existir dicho Navigable String en el tag, se debe realizar un procesado de datos.
                # El formato del Navigable String es, por ejemplo: 'Showing 1 to 10 of 107 entries'. El objetivo, por
                # lo tanto, es obtener el número total de entradas. Para ello, se divide el string a través de los
                # espacios, y se filtran aquellos elementos numéricos, obteniendo una lista formada por 3 numeros.
                # Siguiendo con el ejemplo, la lista obtenida sería: [1, 10, 107].
                total_numbers = [s for s in total_text.split() if s.isdigit()]

                # Una vez obtenida la lista, el siguiente paso es guardar el último elemento validando que la lista
                # tiene longitud 3.
                total_data = total_numbers[-1] if len(total_numbers) == 3 else 'Not Found'
            else:
                # En caso de no encontrar dicho elemento, se asigna por defecto el valor Not Found.
                total_data = 'Not Found'

        # Para obtener el número total de visualizaciones, es necesario acceder al atributo 'datetime' del tag 'time'.
        if html_bs.find('time'):
            report_date = html_bs.find('time').get('datetime') if html_bs.find('time').has_attr('datetime') \
                else 'Not Found'

        # Para obtener el nombre del autor, se deberá buscar un objeto Navigablestrinc contenido en un tag 'a' y cuyo
        # atributo class sea 'url fn n'.
        if html_bs.find('a', {'class': 'url fn n'}):
            author = html_bs.find('a', {'class': 'url fn n'}).string

        # Para obtener el número de visitas se deberá buscar un objeto Navigablestring contenido en un tag 'span' y cuyo
        # atributo class sea 'post-views-count'.
        if html_bs.find('span', {'class': 'post-views-count'}):
            views = html_bs.find('span', {'class': 'post-views-count'}).string

        # Una vez extraída la información referente al autor, fecha report, visualizaciones y número total de registros,
        # el siguiente paso consistirá en rasgar la información contenida en la tabla. Esta información, se identifica a
        # través del tag tbody.
        while True:
            try:
                # Si no existe el tag tbody, se finaliza el proceso de rasgado de la tabla y se informa al usuario, a
                # través del logging del proceso, de una posible modificación del código html.
                assert html_bs.find('tbody'), 'No existe el tag <tbody> de la tabla. Posible modificación HTML'

                # En caso de existir el tag tbody, se realizará el rasgado de los tags hijos contenidos en él. Estos
                # tags serán únicamente los visibles.
                table_df = self._scrap_table(html=html_bs, author=author, report_date=report_date, views=views)

                # Se actualiza la información rasgada.
                report_df = report_df.append(table_df, ignore_index=True)

                # A continuación, el siguiente paso consiste en interactuar con la tabla para poder mostrar el resto
                # de registros contenidos en ella.

                # Para ello, es necesario clicar sobre el botón 'siguiente' representado por el simbolo '>'. Para
                # simular este proceso, se buscará el elemento Beautifulsoup cuya atributto class es 'paginate_button
                # current¡. Este elemento, contiene un NavigableString con información de la página actual.

                # Se comprueba que existe dicho elemento NavigableString y se accede a él. En caso de no existir,
                # se interrumple el rasgado del report y se informa al usuario de una posible modificación en el html.
                txt_error = "No existen el tag '%s'. Posible modificación del HTML"
                assert html_bs.find(class_='paginate_button current'), txt_error % '<class=paginate_button current'

                # Se comprueba que el texto obtenido en el elemento NavigableString es numérico.
                current_page_number = html_bs.find(class_='paginate_button current').string
                assert current_page_number.isdigit(), "El tag '%s' no contiene un número de página correcto."

                # Una vez encontrado el objeto, se interaccionará con él. Para asegurar que el contenido javascript se
                # ha cargado correctamente y se ha modificado el contenido visualizado en la tabla, y por lo tanto, se
                # puede continuar con el rasgado web, se pasa a la función una condición de espera.
                # Está condición bloquea el programa hasta leer la página siguiente en el objeto Beautifulsoup con
                # atributo class=paginate_button current.
                next_page = str(int(current_page_number) + 1)
                html_bs = \
                    self.next_page(xpath_exp='//a[@class="paginate_button next"]',
                                   wait_contidion=ec.text_to_be_present_in_element(
                                       (By.XPATH, '//a[@class="paginate_button current"]'), next_page))

            # Excepción que servirá para controlar los errores producidos por validaciones de contenido html.
            # La funcionalidad de esta excepción consiste en informar al usuario a través del logging y finalizar el
            # scrapping del report.
            except AssertionError as err:
                log_info(logger=self.logger, title=title_report, url=url, status='KO', registers=0, time_scrap=0,
                         error=err, req_time=f"{self.time['request_time']:.2f}")
                break

            # Las siguiente excepción se utiliza para controlar los errores producidos al interactuar con el
            # contenido JavaScript. En concreto, cuando un elemento deja de ser interaccionable, caso que sucede
            # cuando se ha alcanzado el número máximo de elementos visualizados en la tabla. El botón '>' queda
            # desactivado.
            except ElementClickInterceptedException:
                break
            # Esta excepción controla que el elemento seleccionado sobre el cual realizar la interacción exista.
            except NoSuchElementException:
                break
        return report_df, total_data

    @staticmethod
    def _scrap_table(html, author=None, report_date=None, views=None):
        """
        Función que sirve para escrapear los datos contenidos en la tabla de cada report individual.

        :param html: Código html del report a rasgar
        :param author: autor que ha publicado el report
        :param report_date: fecha de publicación del report
        :param views: número de visualizaciones del report
        :return: dataframe con los datos rasgados
        """

        # Se crea un diccionario que contendrá la información rasgada
        raw_data = {f: [] for f in FIELDS_NAME}

        # Los datos a rasgar se encuentran distribuidos a lo largo de una tabla. Para ello, primero se accede al tag
        # padre 'tbody' y se itera sobre todos los hijos 'tr' que contienen el atributo 'role'='row'.
        for row in html.find('tbody').find_all(['tr'], {'role': 'row'}):

            # Para cada hilera recorrida, se añade la información de autor, fecha del report y visitas.
            raw_data['author_report'] = author
            raw_data['date_report'] = report_date
            raw_data['views'] = views

            # La información a rasgar se encuentra en forma de NavigableString en los tags cuyo atributo class
            # tiene el formato 'columna-nombre del campo a rasgar'. Esta información es válida para los campos:
            # "id", "date", "author", "target", "description", "attack", "target_class", "attack_class", "country".
            # En caso de no encontrar dicho elemento, se pondrá por defecto Not Found.
            for col in FIELDS_NAME[:-4]:
                texto = row.find(['td'], {'class': f'column-{col.replace("_", "-")}'})
                raw_data[col].append(texto.text if texto else 'Not Found')

            # Para rasgar la información del link, primero se debe obtener aquella hilera cuyco atributo class='column-
            # link'. A continuación, se deberá acceder al atributo href del tag hijo 'a'.
            # En caso de no encontrar dicho elemento, se informará por defecto el valor 'not found'
            tag_link = row.find(['td'], {'class': f'column-link'})
            if tag_link.find('a'):
                raw_data['link'] = tag_link.a.get('href') if tag_link.a.has_attr('href') else 'Not Found'
            else:
                raw_data['link'] = 'Not Found'

        # A través del método from_dict, se transforma el diccionario a dataframe.
        return DataFrame.from_dict(raw_data)

    def _scrap_2017(self, start_date=datetime(2017, 1, 1).date(), end_date=datetime(2017, 12, 31).date(),
                    driver_name='chrome'):
        """
        Función que permite realizar la descarga y filtrado de la información contenida en el Master Table 2017

        :param start_date: fecha de inicio del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: 01/01/2017.
        :param start_date: fecha de finalización del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: 31/12/2017
        :param driver_name: nombre del driver a utilizar para cargar el contenido JavaScript mediante selenium. Debe
                            contener los valores Firefox o Chrome.
        """
        # Se asigna la variable que contiene la dirección URL de la web Master Table 2017.
        url_master = URL_SITE_MASTER_TABLE_2017

        # Se validan las fechas introducidas. En caso de que el año de finalización de los datos sean anteriores al
        # 01/01/2017, se finaliza el proceso de rasgado informando el error.
        ini_date, fin_date = check_dates(ini_date=start_date, fin_date=end_date)
        assert fin_date.year <= 2017, "Error el año de la fecha de fin del rasgado es anterior a 2017"

        # Si el año de inicio del rasgado es anterior a 2016, se corrige a la fecha 01/01/2017 y se avisa al usuario.
        if ini_date.year < 2016:
            print("Warning. El año de la fecha de inicio es anterior a 2017. Se pondrá por defecto el 01/01/2017")
            ini_date = datetime(2017, 1, 1).date()

        # Si el año de finalización del rasgado es posterior a 2017, se corrige a la fecha 31/12/2017 y se avisa al
        # usuario.
        else:
            if fin_date.year > 2017:
                print("Warning. El año de la fecha de fin es posterior a 2017. Se pondrá por defecto el 31/12/2017")
                fin_date = datetime(2017, 12, 31)

        # Se declara una variable de tiempo para obtener trazabilidad del tiempo necesario para realizar el rasgado.
        start = time()

        try:
            # Inicialización del driver
            self.set_driver(driver_name)

            # Se realiza la petición html sin necesidad de cargar el contenido JavaScript, ya que la finalidad es
            # encontrar el link a Google Sheets que contendrá la información a descargar.
            bs = self.request_url(url=url_master, javascript=False)

            # Para obtener el link de descarga se debe acceder a un objeto BeautifulSoup cuyo texto sea 'Google Sheet'.
            # En caso de no encontrar el elemento, se avisa al usuario de una posible modificación del html.
            assert bs.find(text='Google Sheet'), 'No se ha encontrado texto: "Google Sheet". Posible modificación HTML'

            # Una vez localizado el elemento, será necesario obtener el valor del atributo href, el cual contiene la
            # dirección url.
            tag_download_url = bs.find(text='Google Sheet').parent
            download_url = tag_download_url.get('href') if tag_download_url.has_attr('href') else ''

            # El siguiente paso consistirá en cargar la dirección URL mediante selenium, ya que será necesario realizar
            # una descarga de archivos. Para ello, se irá interaccionando a través del contenido HTML mediante clicks
            # realizados por la librería selenium hasta llegar a realizar la descarga del archivo. Cada uno de estos
            # clicks, contendrá una condición de pausa hasta que el siguiente elemento sea interaccionable.

            # Se abre google Sheets.
            self.request_url(url=download_url, javascript=True,
                             wait_contidion=ec.element_to_be_clickable((By.XPATH, "//div[@id='docs-file-menu']")))
            # Acceso al elemento 'Achivo' de Google Sheets
            self.next_page(xpath_exp="//div[@id='docs-file-menu']",
                           wait_contidion=ec.element_to_be_clickable((By.XPATH, "//div[@id=':2z']")))
            # Acceso al elemento 'Descarga' la ventana 'Archivo'
            self.next_page(xpath_exp="//div[@id=':2z']",
                           wait_contidion=ec.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'.csv')]]")))
            # Acceso al elemento 'Descarga en formato csv'
            self.next_page(xpath_exp="//*[text()[contains(.,'.csv')]]")

            # Una vez realizadas las interacciones se comprueba que el archivo se ha descargado correctamente.
            new_file = check_download(searh_file='2017 Master *.csv', file_size=300000)
            # En caso afirmativo, se procesa el archivo y se almacena en formato csv.
            self.writer_download(input_=new_file, output=MASTER_2017_PATH_FILE, start_date=ini_date, end_date=fin_date)
            # Se infora del exito del proceso
            log_info(logger=self.logger, title='MASTER TABLE 2017', url=URL_SITE_MASTER_TABLE_2017, status='OK',
                     registers=len(self.df), time_scrap=f"{time() - start:.2f}", info=f'Carga Completa',
                     req_time=f"{self.time['request_time']:.2f}")

        # En caso de suceder algún error inesperado se informa al usuario
        except AssertionError as err:
            log_info(logger=self.logger, title='MASTER TABLE 2017', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")

        except Exception as err:
            print('Ha ocurrido un error inesperado')
            log_info(logger=self.logger, title='MASTER TABLE 2017', url=URL_SITE_MASTER_TABLE_2017, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")

        # Se cierra el driver de selenium inicializado.
        self.close_driver()

    def _scrap_2018(self, start_date=datetime(2018, 1, 1).date(), end_date=datetime(2018, 12, 31).date(),
                    driver_name='chrome'):
        """
        Función que permite realizar la descarga y filtrado de la información contenida en el Master Table 2018

        :param start_date: fecha de inicio del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: 01/01/2018.
        :param start_date: fecha de finalización del scraping. Debe estar en formato YYYY-mm-dd. Por defecto: 31/12/2018
        :param driver_name: nombre del driver a utilizar para cargar el contenido JavaScript mediante selenium. Debe
                            contener los valores Firefox o Chrome.
        """
        # Se asigna la variable que contiene la dirección URL de la web Master Table 2018.
        url_master = URL_SITE_MASTER_TABLE_2018

        # Se validan las fechas introducidas. En caso de que el año de finalización de los datos sean anteriores al
        # 01/01/2018, se finaliza el proceso de rasgado informando el error.
        ini_date, fin_date = check_dates(ini_date=start_date, fin_date=end_date)
        assert fin_date.year <= 2018,  "Error el año de la fecha de fin del rasgado es anterior a 2018"

        # Si el año de inicio del rasgado es anterior a 2018, se corrige a la fecha 01/01/2018 y se avisa al usuario.
        if ini_date.year < 2018:
            print("Warning. El año de la fecha de inicio es anterior a 2018. Se pondrá por defecto el 01/01/2018")
            ini_date = datetime(2018, 1, 1).date()

        # Si el año de finalización del rasgado es posterior a 2018, se corrige a la fecha 31/12/2018 y se avisa al
        # usuario.
        else:
            if fin_date.year > 2018:
                print("Warning. El año de la fecha de fin es posterior a 2018. Se pondrá por defecto el 31/12/2018")
                fin_date = datetime(2018, 12, 31).date()

        # Se declara una variable de tiempo para obtener trazabilidad del tiempo necesario para realizar el rasgado.
        start = time()

        try:
            # Inicialización del driver
            self.set_driver(driver_name)

            # Se realiza la petición html para realizar la descarga del archivo. Para iniciar dicha descarga, es
            # necesario interactuar con un elemento haciendo click en él. Por ello, la petición se realiza mediante
            # selenium deteniendo el proceso hasta que el elemnto necesario para realizar la descarga es interaccionable

            # En concreto, el elemto a pulsar se encuentra en un 'span' cuyo contenido es 'CSV'.
            self.request_url(url_master, javascript=True,
                             wait_contidion=ec.element_to_be_clickable((By.XPATH, "//span[contains(., 'CSV')]")))

            # Una vez cargada la página web, se interacciona con el elemento para realizar la descarga
            self.next_page(xpath_exp="//span[contains(., 'CSV')]")

            # Una vez realizadas las interacciones se comprueba que el archivo se ha descargado correctamente.
            new_file = check_download(searh_file='2018 Master *.csv', file_size=300000)
            # En caso afirmativo, se procesa el archivo y se almacena en formato csv.
            self.writer_download(input_=new_file, output=MASTER_2018_PATH_FILE, start_date=ini_date, end_date=fin_date)
            # Se infora del exito del proceso
            log_info(logger=self.logger, title='MASTER TABLE 2018', url=URL_SITE_MASTER_TABLE_2018, status='OK',
                     registers=len(self.df), time_scrap=f"{time() - start:.2f}", info=f'Carga Completa',
                     req_time=f"{self.time['request_time']:.2f}")

        # En caso de suceder algún error inesperado se informa al usuario
        except AssertionError as err:
            log_info(logger=self.logger, title='MASTER TABLE 2018', url=URL_SITE_MASTER_TABLE_2018, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")

        except Exception as err:
            print('Ha ocurrido un error inesperado')
            log_info(logger=self.logger, title='MASTER TABLE 2018', url=URL_SITE_MASTER_TABLE_2018, status='KO',
                     registers=0, time_scrap=f"{time() - start:.2f}", error=err,
                     req_time=f"{self.time['request_time']:.2f}")
        # Se cierra el driver de selenium inicializado.
        self.close_driver()
