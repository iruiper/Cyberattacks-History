import pandas as pd
import numpy as np

from os import path, listdir

from constants import CLEAN_DATA_PATH, RAW_DATA_PATH, ADDITIONAL_DATA_PATH


def get_data(pattern):
    """
    Función que lee el fichero determinado por la variable pattern. Esta función, buscará por defecto el documento
    más reciente (ordenado por nombre) y lo leerá para devolver sus datos en forma de dataframe.

    :param pattern: Cadena de carácteres que debe contener el fichero en función
    :return: dataframe leido
    """

    # Se obtienen todos los ficheros que tengan el patron 'pattern' en RAW_DATA_PATH. A continuación, se ordena de forma
    # descendente la lista para obtener el archivo más reciente en la posición 0.
    source_path = sorted([path.join(RAW_DATA_PATH, f) for f in listdir(RAW_DATA_PATH) if pattern in f], reverse=True)[0]

    # Lectura del dataframe
    df = pd.read_csv(source_path, decimal=',', sep=';')

    return df


def filter_master(data_raw, year_master, subset):
    """
    Función destinada a filtrar los ficheros de entrada master 2017 y master 2017
    :param data_raw: Fichero csv con la información del master
    :param year_master: Año del report
    :param subset: Columnas seleccionadas del archivo de entrada.
    :return: Master filtrado, eliminando los errores por fechas de reporte y con los campos contenidos en subset
    """
    # Selección de columnas de interes
    data_filter_cols = data_raw.copy()

    # Se convierte la columna date a formato fecha
    data_filter_cols.Date = pd.to_datetime(data_filter_cols.Date, errors='coerce', format='%Y-%m-%d', utc=True)

    # Se eliminan aquellos registros que estén fuera del 2017
    data_filtered = data_filter_cols.loc[data_filter_cols.Date.dt.year == year_master, subset]

    return data_filtered


def filter_timeline(data_raw, subset):
    """
    Función destinada a filtrar los ficheros de entrada timeline y errores
    :param data_raw: Ficheros csv con la información de los ataques
    :param subset: Columnas seleccionadas del archivo de entrada
    :return: Dataframe filtrado eliminando aquellos errores de reporte por fechas y con los campos contenidos en subset
    """

    # Se crea un diccionario que permitira homogenizar las diferencias de nomenclaturas entre las columnas de Master y
    # Timeline
    rename_col = {
        'id': 'ID',
        'date': 'Date',
        'author': 'Author',
        'target': 'Target',
        'description': 'Description',
        'attack': 'Attack',
        'target_class': 'Target Class',
        'attack_class': 'Attack Class',
        'country': 'Country',
        'link': 'Link',
        'author_report': 'author_report',
        'date_report': 'date_report',
        'views': 'views',
    }

    # Convertimos los campos Date y Date Report a formato fecha para poderlos tratar adecuadamente
    data_raw.date = pd.to_datetime(data_raw.date, errors='coerce', format='%d/%m/%Y', utc=True)
    data_raw.date_report = pd.to_datetime(data_raw.date_report, errors='coerce', utc=True)

    # Eliminamos aquellos registros erroneos.
    data_raw.drop(index=data_raw[data_raw.date > data_raw.date_report].index, inplace=True)
    data_raw.drop(index=data_raw[data_raw.date.dt.year < 2019].index, inplace=True)

    # Homogenización de las columnas
    data_raw.rename(columns=rename_col, inplace=True)

    # Selección de atributos
    data_filtered = data_raw.loc[:, subset]

    return data_filtered


def get_attack(data):
    """
    Función que procesará el campo attack class
    :param data: Dataframe de entrada con la información unificada de todas las fuentes
    :return: dataframe con el campo attack class procesado. Se crearán las variables code attack class, desc attack
             class y problemas QC
    """

    # Procesado campo Attack. Este campo se homogenarizará a partir de los siguientes datos:
    attack_class_dict = {
        'CE': 'Cyber Espionage',
        'CW': 'Cyber Warfare',
        'CC': 'Cyber Crime',
        'H': 'Hacktivism',
        '>1': 'Multiple',
        'UK': 'Unknown'
    }

    # Se normalizan todos los datos a minúscula para la descripción del ataque
    data['Attack'] = data['Attack'].str.lower()

    # Se categorizan los datos perdidos. Estos son los que contienen Not Found, ? o isnull()
    data['Attack Class'] = np.where((data['Attack Class'].str.contains('Not Found', case=False)) |
                                    (data['Attack Class'].str.contains('\?', case=False)) |
                                    (data['Attack Class'].isnull()),
                                    'UK', data['Attack Class'].str.lstrip())

    # Se homogenizan los datos a través del diccionario attack_class_dict
    data.loc[:, 'Desc_attack_class'] = np.where(data['Attack Class'].map(attack_class_dict).isnull(),
                                                data['Attack Class'],
                                                data['Attack Class'].map(attack_class_dict))

    # Ahora se intentarán informar los datos perdidos a partir del campo 'Ataque'. Para ello, primero
    # se obtiene la información de aquellos campos informados correctamente. Aquellos que no son conocodios.
    data_known = data[data.Desc_attack_class != 'Unknown']

    # El metodo de llenar los missing values, será a partir del elemento que presente máxima frecuencia entre
    # la variable categorica Attack
    map_atk = data_known.groupby(['Attack', 'Desc_attack_class']).count().max(level=[0, 1])\
        .reset_index(1)['Desc_attack_class'].to_dict()

    # Se informa el campo mediante el mapping obtenido
    data.loc[data.Desc_attack_class == 'Unknown', 'Ffill_Desc_attack_class'] = \
        data.loc[data.Desc_attack_class == 'Unknown', 'Attack'].map(map_atk)

    # En caso de que no se haya conseguido informar el valor perdido a partir de la imputación por medida de tendencia
    # cenrtal, se asigna la cte Unknown utilizada para informar los valores perdidos
    data.loc[:, 'Desc_attack_class'] = data['Desc_attack_class'].where(data['Ffill_Desc_attack_class'].isnull(),
                                                                       data['Ffill_Desc_attack_class'])

    # Se crea la variable problemasQC a partir del campo de procesado de los valores perdidos
    data.loc[:, 'ProblemasQC'] = np.where(data.Ffill_Desc_attack_class.isnull(), False, True)

    # Homgenización del código a partir de la descripción.
    data.loc[:, 'Code_attack_class'] = data.Desc_attack_class.map({k: i for i, k in attack_class_dict.items()})

    return data[['Code_attack_class', 'ProblemasQC']]


def get_author(data):
    """
    Función que procesará el campo author
    :param data: Dataframe de entrada con la información unificada de todas las fuentes
    :return: dataframe con el campo author procesado.
    """

    # Se procesa la columna Author, para ello se categorizar en los valores 'Conocido, Desconocido'.
    # Para que un autor sea desconocido, debe contener los carácteres '?', '>1' o las palabras unknown, anonymous.
    data.loc[:, 'Author_processed'] = np.where((data.Author.str.contains('unknown', case=False)) |
                                               (data.Author.str.contains('\?', case=False)) |
                                               (data.Author.str.contains('anonymous', case=False)) |
                                               (data.Author.str.contains('>1', case=False)),
                                               'Desconocido', 'Conocido')
    return pd.Series(data.Author_processed)


def get_country(data):
    """
    Función que procesará el campo country
    :param data: Dataframe de entrada con la información unificada de todas las fuentes
    :return: dataframe con el campo country procesado. Se crearán las variables country_name y continent.
    """

    # Lectura del fichero externo utilizado para realizar la discretización de valroes
    df_continent = pd.read_excel(f'{ADDITIONAL_DATA_PATH}\continent_country.xlsx', index_col=0)

    # Procesado Country. Se asigna la cte Unkown a los valores vacíos. Adicionalmente se separan aquellos registros
    # que contienen distintos paises separados por saltos de línea.
    df_country = \
        pd.merge(left=data,
                 right=data.Country.fillna('Unknown').str.replace('\n', ' ').str.split(' ').explode(),
                 right_index=True,
                 left_index=True)[['ID', 'Country_y']]

    df_country.reset_index(drop=True, inplace=True)
    df_country.drop(df_country[df_country.Country_y == ''].index, inplace=True)
    df_country.set_index('ID', drop=False, inplace=True)
    df_country.loc[:, 'recuento'] = df_country.groupby(level='ID').nunique()['Country_y']

    # Una vez procesados los países por saltos de línea, se les asigna la variable > 1
    df_country.loc[:, 'Country_processed'] = df_country.Country_y.where(df_country.recuento == 1, '>1')
    data.loc[:, 'Country_processed'] = df_country[['ID', 'Country_processed']].drop_duplicates().set_index('ID')

    # Discretización de valores a partir del excel externo.
    data.loc[:, 'Continent'] = data.Country_processed.map(df_continent['Continente'].to_dict())
    data.loc[:, 'Pais'] = data.Country_processed.map(df_continent['Nombre País'].to_dict())

    return data[['Pais', 'Continent']]


def get_target(data):
    """
    Función que procesará el target class
    :param data: Dataframe de entrada con la información unificada de todas las fuentes
    :return: dataframe con el campo target class procesado. Se crearán las variables code target class y desc target
             class
    """

    # Se procesa la variable Target Class, informando los valores vacios.
    data.loc[:, 'Target Class'] = data['Target Class'].where(data['Target Class'] != 'Not Found', 'Z Unknown')

    # Se separá el campo en letra inicial - descropción
    target_class_df = pd.DataFrame(data=data['Target Class'].str.split(' ', n=1, expand=True).values,
                                   columns=['Code_target_class', 'Desc_target_class'])

    # Homogenización de Descripciones de target class
    target_class_dict = {
        'Y': 'Multiple Industries',
        'O': 'Public administration and defence, compulsory social security'
    }
    target_class_df.loc[:, 'Desc_target_class'] = \
        np.where(target_class_df['Code_target_class'].map(target_class_dict).isnull(),
                 target_class_df['Desc_target_class'],
                 target_class_df['Code_target_class'].map(target_class_dict))

    return data.join(other=target_class_df)[['Code_target_class', 'Desc_target_class']]


if __name__ == '__main__':

    # Columnas comunes en todos los ficheros de entrada
    cols_set = ['Date', 'Author', 'Target', 'Description', 'Attack', 'Target Class', 'Attack Class', 'Country', 'Link']

    # Lectura de los datasets
    df_2018 = get_data(pattern='Master Data 2018')
    df_2017 = get_data(pattern='Master Data 2017')
    df_timeline = get_data(pattern='scrapping')
    df_errors = get_data(pattern='error - files')

    # Filtrado de los datos, se hacen dos tareas de limpieza:
    #
    #   1. Se eliminan aquellos reportes informados con una fecha incorrecta, incluyendo
    #      - Fechas sin informar
    #      - Fechas no coeherentes con el periodo de reporte
    #
    #   2. Se seleccionan aquellas columnas comunes en todos los reports mediante la variable subset

    df_2017_filtered = filter_master(df_2017.copy(), year_master=2017, subset=cols_set)
    df_2018_filtered = filter_master(df_2018.copy(), year_master=2018, subset=cols_set)
    df_timeline_filtered = filter_timeline(df_timeline.copy(), subset=cols_set)
    df_errors_filtered = filter_timeline(df_errors.copy(), subset=cols_set)

    # Integración de los datos. Se realiza una fusión vertical para integrar la información 2017 - Actualidad
    data = pd.concat(objs=[df_2017_filtered, df_2018_filtered, df_timeline_filtered, df_errors_filtered],
                     ignore_index=True)

    # Se eliminan duplicados. De esta forma se pretenden eliminar ataques publicados en distintos reports
    data.drop_duplicates(inplace=True)
    data.reset_index(drop=True, inplace=True)

    # Se crea un identificador único que servirá para ir informando los distintos campos.
    data.index.name = 'ID'
    data.reset_index(inplace=True)

    # Se procesa la información referente a los ataques
    data[['Code_attack_class', 'ProblemasQC']] = get_attack(data=data.copy())

    # Se procesa la información refrente al author
    data.loc[:, 'Author_processed'] = get_author(data=data.copy())

    # Se procesa la información referente al país
    data[['Country_name', 'Continent']] = get_country(data=data.copy())

    # Se procesa la información referente a target class
    data[['Code_target_class', 'Desc_target_class']] = get_target(data=data.copy())

    # Procesado Mes y Año
    data.loc[:, 'Year'] = pd.to_datetime(data.Date, utc=True).dt.year
    data.loc[:, 'Mes'] = pd.to_datetime(data.Date, utc=True).dt.month

    # Selección columnas de análisis
    # Columnas seleccionadas para sacar la información relevante del dataset
    analysis_cols = ['Year', 'Mes', 'Continent', 'Country_name', 'Code_target_class', 'Desc_target_class',
                     'ProblemasQC', 'Author_processed', 'Code_attack_class']
    data_complete = data.loc[:, analysis_cols]


    # Creación de las variables dummy de attaques + autor para hacer sumatorios
    data_complete_attacks = pd.get_dummies(data_complete[analysis_cols],
                                           columns=['Author_processed', 'Code_attack_class'])

    # Agrupación de los datos en función del año, mes, continente, país, target_class.
    aggregated_data = data_complete_attacks.groupby(analysis_cols[:-2]).sum().reset_index()

    # Recuento del número de ataques total recibido por cada crosstab
    aggregated_data.loc[:, 'NumeroAtaques'] = aggregated_data[aggregated_data.columns[-6:]].sum(axis=1)

    # Escritura del documento csv con la información procesada
    aggregated_data.to_csv(path.join(CLEAN_DATA_PATH, 'EstadisticasAtaques2017_2020_Input.csv'),
                           index=False, sep=';', decimal=',', encoding='latin-1')
