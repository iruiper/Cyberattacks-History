import os
import pygogo
import sys
from time import time, sleep
from datetime import datetime


def time_exec(f):
    def g(self, *args, **kwargs):
        sleep(self.time['wait_time'])
        start = time()
        func = f(self, *args, **kwargs)
        self.set_request_time(time() - start)
        return func
    return g


def get_ini_date(date):
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Error, la fecha de fin debe tener el formato YYYY-mm-dd")


def get_fin_date(date):
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Error, la fecha de fin debe tener el formato YYYY-mm-dd")


def transform_header(title):
    return "-".join("-".join(title.split(" ")[:3]).split("-")[1:])


def check_header(str_time, frmt_time, start, end):
    try:
        read = start <= datetime.strptime(str_time, frmt_time).date() <= end
        follow = end <= datetime.strptime(str_time, frmt_time).date()
    except ValueError:
        read, follow = False, False
    return read, follow


def create_file_formatter(uri_log):
    """
        Creates a csv file for log with the headers
    """
    # To get path exclude file name
    if "/" in uri_log:
        path = "/".join(uri_log.split("/")[:-1])
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

    # If log don't exist create headers
    if not os.path.isfile(uri_log):
        with open(uri_log, mode="w") as file:
            file.write("; ".join(['Fecha', 'Title', 'URL', 'Status', 'Registers', 'Scrapping Time',' Info']))
            file.write("\n")

    return pygogo.logging.FileHandler(uri_log)


def create_logger(file_path):
    logging_fmt = '%(asctime)s;%(message)s'
    formatter = pygogo.logging.Formatter(logging_fmt, datefmt=pygogo.formatters.DATEFMT)
    fhdlr = create_file_formatter(file_path)

    return  pygogo.Gogo(name='', low_hdlr=fhdlr, low_formatter=formatter, high_hdlr=fhdlr, high_formatter=formatter,
                        monolog=True).get_logger()


def log_info(logger, **kwargs_msg):
    """
    Función que genera un log de errores.

    :param module: nombre del script y modulo que genera el error
    :param file_path: ruta dónde se generará el archivo de errores
    :param kwargs_msg:
            'error': excepción generada
            'description': narrativa escrita por el usuario para tener mejor comprensión del error del programa.
    """

    if "error" in kwargs_msg.keys():
        kwargs_msg["info"] = str(kwargs_msg["error"]).replace("\n", " | ").replace(";", ":") + \
                             f' ({sys.exc_info()[-1].tb_lineno})'
    logger.info("{title};{url};{status};{registers};{time_scrap};{info}".format(**kwargs_msg))
    print("{title}\t{url}\t{status}\t{registers}\t{time_scrap}\t{info}".format(**kwargs_msg))
