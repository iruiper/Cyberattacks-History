import os
import pygogo
import sys
import glob
from constants import DESKTOP_PATH
from time import time, sleep
from datetime import datetime


def time_exec(f):
    """

    Decorador utilizado para medir, controlar y actualizar los tiempos entre peticiones.
    Este decorador, mediante sleep(self.time['wait_time']), esperará X tiempo en realizar la petición. Al pasar este
    tiempo de espera, se realizará la petición mediante la función encapsulda en f() y se medirá el tiempo necesario
    para completarse.
    Mediante self.set_request_time(), se actualizará el tiempo medio de espera entre peticiones.

    :param f: función encapsuladora
    :return: función decorada
    """
    def g(self, *args, **kwargs):
        sleep(self.time['wait_time'])
        start = time()
        func = f(self, *args, **kwargs)
        self.set_request_time(time() - start)
        return func
    return g


def get_ini_date(date):
    """
    Función que convierte un string a tipo date. Para realizar la conversión, el parámetro date debe presentar un
    formato YYYY-MM-DD

    :param date: fecha con tipo de datos string
    :return: fecha con tipo de datos date
    """
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Error, la fecha de inicio debe tener el formato YYYY-mm-dd")


def get_fin_date(date):
    """
    Función que convierte un string a tipo date. Para realizar la conversión, el parámetro date debe presentar un
    formato YYYY-MM-DD

    :param date: fecha con tipo de datos string
    :return: fecha con tipo de datos date
    """
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Error, la fecha de fin debe tener el formato YYYY-mm-dd")


def check_dates(ini_date, fin_date):
    """
    Función que comprueba si las fechas de inicio y fin son correctas. Para ello, primero transforma el tipo
    de datos (si es necesario) y, posteriormente, comprueba que la fecha de fin es superior a la fecha de inicio.

    :param ini_date: fecha de inicio del scrapping. Tipo de datos string y con formato YYYY-mm-dd
    :param fin_date: fecha de fin del scrapping. Tipo de datos string y con formato YYYY-mm-dd.
    :return: fecha_inicio, fecha_fin con el tipo de dato transformado.
    """
    ini_date = get_ini_date(date=ini_date) if isinstance(ini_date, str) else ini_date
    fin_date = get_fin_date(date=fin_date) if isinstance(fin_date, str) else fin_date
    assert ini_date < fin_date, f"{ini_date} es superior a {fin_date}"
    return ini_date, fin_date


def transform_header(title):
    """
    Función que procesa el título de los reports extrayendo la fecha contenida en ellos. Todos los reports del
    Timeline tienen el formato 'dd_1-dd_2 bb YYYY Cyber Attacks Timeline' siendo bb el nombre del mes en ingles y
    dd_1 y dd_2 el primer y último día de la quinzena.

    Para realizar el procesado, primero se separa el string por spacios y se guardan los tres primeros elementos de
    la lista. De esta forma, se obtiene una lista con [dd_1-dd_2, bb, YYYY].

    Posteriormente, esta lista se convierte en un string, con el símbolo '-' como unión entre elementos, obteniendo el
    string: dd_1-dd_2-bb-YYYY. A continuación, se separa otra vez el string resultante, mediante el carácter '-',
    obteniendo una lista [dd_1, dd_2, bb, YYYY].

    El último paso, consiste en guardar los 3 últimos elementos de la lista y formar el string dd_2-bb-YYYY.

    En el caso de que no se pueda realizar dicho procesado, se devuelve el valor Not Match Title.

    :param title: Título del report a procesar
    :return: Título procesado devolviendo la fecha contenida en él.
    """
    try:
        return "-".join("-".join(title.split(" ")[:3]).split("-")[1:])
    except IndexError:
        return 'Not Match Title'


def check_header(str_time, frmt_time, start, end):
    """
    Dadas una fecha de inicio y una fecha de fin, se comprueba que el valor contenido en str_time cumpla los siguientes
    requisitos.
        1-  Esté comprendido entre la fecha de inicio y la fecha de fin.
        2 - Sea posterior a la fecha de fin

    Esta función tiene el objetivo de validar si el título del report debe rasgarse (parámetro read) o si se debe
    ignorar. El parámetro follow sirve para indicar al programa que, en el caso de que un report no deba rasgarse,
    continue con el proceso de rasgado.

    :param str_time: fecha a transformar.
    :param frmt_time: formato de texto de frmt_time, para realizar la conversión a tipo date.
    :param start: fecha de inicio.
    :param end: fecha de fin.
    :return: read: boleano para realizar el scrapping.
             follow: boleano para continuar el scrapping.
    """
    try:
        read = start <= datetime.strptime(str_time, frmt_time).date() <= end
        follow = end < datetime.strptime(str_time, frmt_time).date()
    except ValueError:
        read, follow = False, False
    return read, follow


def create_file_formatter(uri_log):
    """
    Función que creará, en caso de no existir, el archivo de logging del proceso de scrapping

    :param uri_log: ruta y nombre del fichero
    :return: filehandler para realizar la escritura
    """

    # El archivo de logging contendrá las siguientes cabeceras
    log_headers = ['Fecha', 'Title', 'URL', 'Status', 'Registers', 'Scrapping Time', 'Request Time', 'Info']

    # Se comprueba que existe la carpeta que contendrá el archivo de logging. En caso negativo, se creará la carpeta.
    if "/" in uri_log:
        path = "/".join(uri_log.split("/")[:-1])
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

    # Se comprueba que existe el archivo de logging 'uri_log'. En caso contrario se creará un archivo nuevo con las
    # cabeceras. El separador de campos del archivo será ;.
    if not os.path.isfile(uri_log):
        with open(uri_log, mode="w") as file:
            file.write("; ".join(log_headers))
            file.write("\n")

    return pygogo.logging.FileHandler(uri_log)


def create_logger(file_path):
    """
    Función que crea un logger para realizar las funciones de logging del proceso. La librería utilizada es Pygogo.

    :param file_path: ruta del fichero sobre el cual realizar el logging-
    :return: objeto logger.
    """

    # Se especifica el formato que tendrá el logging.
    logging_fmt = '%(asctime)s;%(message)s'
    formatter = pygogo.logging.Formatter(logging_fmt, datefmt=pygogo.formatters.DATEFMT)
    # Se especifica el archivo que contendrá el logging
    fhdlr = create_file_formatter(file_path)

    # Se crea el logger. No se realiza ninguna distinción entre los diferentes niveles de aviso (INFO, WARNING, etc).
    # Por ello, se especifica el mismo file handler para el nivel bajo y alto de las alertas.
    return pygogo.Gogo(name='', low_hdlr=fhdlr, low_formatter=formatter, high_hdlr=fhdlr, high_formatter=formatter,
                       monolog=True).get_logger()


def log_info(logger, **kwargs_msg):
    """
    Función que escribe en el log de errores, la información contenida en **kwargs_msg

    :param logger: objeto de la clase logger que contiene la ruta y el filehandler sobre el que se escribirá el logging
    :param kwargs_msg: por ahora, las keys admitidas son:
            'title': título del report sobre el que se hace el scrapping
            'url': dirección url de scrapping
            'status': información sobre el estado de scrapping. Valores posibles: OK, KO o INFO.
            'registers': número de registros scrapeados
            'time_scrap': tiempo necesario para realizar el rasgado
            'info': información detallada para aquellos procesos con status OK o INFO.
            'req_time': tiempo de petición HTTP.
            'error': información detallada para aquellos procesos con status KO.
    """

    # En caso de que se pase el parámetro de error en kwargs_msg, se procesa dicho mensaje para obtener la descripción
    # y la línea en la que se ha producido el error.
    if "error" in kwargs_msg.keys():
        kwargs_msg["info"] = str(kwargs_msg["error"]).replace("\n", " | ").replace(";", ":") + \
                             f' ({sys.exc_info()[-1].tb_lineno})'

    # Se escribe el logging.
    logger.info("{title};{url};{status};{registers};{time_scrap};{req_time};{info}".format(**kwargs_msg))
    # Se printea por pantalla el logging.
    print("{title}\t{url}\t{status}\t{registers}\t{time_scrap}\t{req_time}\t{info}".format(**kwargs_msg))


def check_download(searh_file, file_size):
    """
    Función que comprueba que un fichero se ha descargado correctamente. Para ello, se valida que el fichero
    contiene un tamaño mínimo determinado por file_size.

    Esta función supone que no existe ningún fichero previo que cumpla con las condiciones de search_file. En caso de
    existir, devolverá el fichero ya existente

    :param searh_file: ruta del fichero a buscar
    :param file_size:  tamaño mínimo del fichero expresado en KB
    :return: ruta completa del fichero. En caso de no encontrarse dicho fichero, se lanza una excepción.
    """

    files_on_desktop = []

    timer = 0
    # Se inicia un bucle de búsqueda del fichero en la ruta especificada en search_file. Este bucle finaliza cuando
    # se encuentre el fichero o, hayan trancurrido 10 segundos.
    while len(files_on_desktop) == 0 and timer < 10:
        files_on_desktop = glob.glob(os.path.join(DESKTOP_PATH, searh_file))
        sleep(1)
        timer += 1
    assert len(files_on_desktop) != 0, "No se ha descargado el archivo"

    timer = 0
    # Se inicia un bucle que comprueba que el tamaño del fichero cumple con los requisitos mínimos. Este bucle finaliza
    # cuando se cumpla con el tamaño mínimo del fichero o, hayan trancurrido 10 segundos. La utilidad de este bucle,
    # es evitar devolver la ruta de un achivo vacío (se ha creado el archivo, pero aún no se ha volcado la información
    # en él).
    while os.stat(files_on_desktop[0]).st_size < file_size and timer < 10:
        sleep(1)
        timer += 1
    assert os.stat(files_on_desktop[0]).st_size >= file_size, "Descarga incompleta"
    return files_on_desktop[0]
