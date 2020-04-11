# Cyberattacks-History
Proyecto para la asignatura M2.851


## Descripción:
TO DO
     
## Miembros del equipo
La actividad ha sido realizada por **Ivan Ruiz** y **Joel Bustos**.

## Contenido
El proyecto está estructurado en las siguientes carpetas.

### src
Contiene el código del proyecto con el que se realiza el scrapping de la página web www.hackmageddon.com. En la carpeta existen los siguientes scripts:

- **main.py**: punto de entrada del programa. Se inicia el proceso de scraping mediante un objeto de la clase _BeautyScraper_.

- **scrapper.py**: contiene la implementación de la clase _BeautyScraper_ para generar el conjunto de datos a partir de la pagina web de la práctica. Esta clase contiene 4 métodos principales:
    1. _start_scrapping_. Adminte como parámetros de entrada una fecha de inicio (_ini_date_) y una fecha de fin (_fin_date_) para seleccionar el periodo de tiempo sobre el cual se realizará el scrapping. Adicionalmente, permite la opción de escoger entre el driver empleado ('chrome' o 'firefox') mediante el parámetro _driver_name_. En función del periodo de tiempo especificado se realiza el scrapping de las paginas web Timeline [1], Master Table 2018 [2] y Master Table 2017 [3].
    
    2. _ _scrap_timeline_. Adminte como parámetros de entrada una fecha de inicio (_start_date_) y una fecha de fin (_end_date_) para seleccionar el periodo de tiempo sobre el cual se realizará el scrapping. Adicionalmente, permite la opción de escoger entre el driver empleado ('chrome' o 'firefox') mediante el parámetro _driver_name_. Este método permite scrapear las distintas tablas de los reports contenidos en el Timeline de la web. 
    
    3. _ _scrap_2017_. Adminte como parámetros de entrada una fecha de inicio (_start_date_) y una fecha de fin (_end_date_) para seleccionar el periodo de tiempo sobre el cual se realizará el scrapping. Adicionalmente, permite la opción de escoger entre el driver empleado ('chrome' o 'firefox') mediante el parámetro _driver_name_. Este método permite scrapear el historial anual del año 2017. Se basa en la descarga de una archivo almacenado en google docs y un procesado para seleccionar el periodo de tiempo deseado.
    
     4. _ _scrap_2018_. Adminte como parámetros de entrada una fecha de inicio (_start_date_) y una fecha de fin (_end_date_) para seleccionar el periodo de tiempo sobre el cual se realizará el scrapping. Adicionalmente, permite la opción de escoger entre el driver empleado ('chrome' o 'firefox') mediante el parámetro _driver_name_. Este método permite scrapear el historial anual del año 2018. Se basa en la descarga de una archivo csv a través de la interacción con un botón de JavaScript y un procesado para seleccionar el periodo de tiempo deseado.
     
- **scrapper_utils.py**. Script que contiene funciones auxiliares empleadas por la clase _BeautyScraper_. 

- **constants.py**. Script que contiene las constantes utilizadas por el programa.

### Logging
Carpeta utilizada para almacenar los distintos logs generados durante el proceso de scrapping. Para poder identidicar el archivo con el momento en el que se inicia el proceso de rasgado web, se ha definido la siguiente nomenclatura: _scrapping dd-mm-YYYY HH.MM.SS.csv_. 

Cada uno de estos archivos, contiene la siguiente información:
- **Fecha:** Momento en el que se ha realizado el proceso de scrapping.
- **Title:** Título del report sobre el que se extrae la información.
- **URL:** Dirección URL del report sobre la cual se realiza el rasgado web.
- **Status:** Informa sobre el éxito del scraping (OK); sobre el fracaso (KO) o sobre información adicional (INFO).
- **Scrapping Time**: Tiempo transcurrido entre que se ha realizado la petición y se ha extraído toda la información requerida.
- **Request Time:** Tiempo transcurrido en realizar la petición HTTP. 
- **Info:** Información adicional del proceso. Si el status es KO, este campo contiene el error.

### Drivers
Carpeta que contiene los drivers de Chrome y FireFox necesarios para poder ejecutar selenium. Estos drivers son compatibles con las versiones:
- **CHROME:** 
- **FIREFOX:**
    
### Data
Carpeta utilizada para almacenar la información extraída por el programa al finalizar el scraping. Los datos obtenidos, son almacenados en formato csv. 

La carpeta data se divide en:
- **00_raw_:**
- **01_clean:**


 ## Referéncias
 [1] https://www.hackmageddon.com/category/security/cyber-attacks-timeline/
 
 [2] https://www.hackmageddon.com/2018-master-table/
 
 [3] https://www.hackmageddon.com/2017-master-table/
