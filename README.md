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
- **CHROME:**  Versión 81 de Google Chrome. Driver utilizado: ChromeDriver 81.0.4044.69 [4]
- **FIREFOX:** Versión > 60 de FireFox. Driver utilizado: GeckoDriver v.0.26 [5]
    
### Data
Carpeta utilizada para almacenar la información extraída por el programa al finalizar el scraping. Los datos obtenidos, son almacenados en formato csv. 

La carpeta data se divide en:
- **00_raw_:** Carpeta destinada a almacenar los datos crudos extraídos del proceso de web scrapping. Estos datos no han sido procesados, limpiados o manipulados. Adicionalmente, al tener 3 fuentes de datos distintas (Timeline, Master Table 2017 y Master Table 2018), los archivos almacenados se dividen en:
     1. _scrapping YYYY-mm-dd HH.MM.SS.csv_: contiene la información extraída del Timeline.
     2- _Master Data 2018 YYYY-mm-dd HH.MM.SS.csv_ o _2018 Master Table.csv_: contiene la información extraída de Master Data 2018.
     3- _Master Data 2017 YYYY-mm-dd HH.MM.SS.csv_ o _2017 Master Table Sheet1.csv _: contiene la información extraída de Master data 2017.

Finalmente, los datos extraídos contienen los siguientes campos:
     1. _ID_: Identificador de registros de cada campo.
     2. _DATE_: Fecha en la que se ha realizado el ataque.
     3. _AUTHOR_: Autor que ha realizado el ataque cibernético.
     4. _TARGET_: Empresa o entidad receptora del ataque cibernético.
     5. _DESCRIPTION_: 
     6. _ATTACK_:
     7. _TARGET_CLASS_:
     8. _COUNTRY_: País receptor del ataque cibernético.
     9. _LINK_: 
     10._AUTHOR_REPORT_: Nombre del autor que ha publicado el report en el Timeline. No aplica para Master Table 2018 y 2017.
     11._DATE_REPORT_: Fecha de publicación del report en el Timeline. No aplica para Master Table 2018 y 2017.
     12._VIEWS_: Número de visualizaciones del report en el Timeline. No aplica para Master Table 2018 y 2017.

- **01_clean:** Carpeta destinada a almacenar los datos procesados y limpos procedentes de _00_raw_. Durante la realización de esta practica, no se ha empleado esta carpeta.


 ## Referéncias
 [1] https://www.hackmageddon.com/category/security/cyber-attacks-timeline/
 
 [2] https://www.hackmageddon.com/2018-master-table/
 
 [3] https://www.hackmageddon.com/2017-master-table/
 
 [4] https://chromedriver.storage.googleapis.com/index.html?path=81.0.4044.69/
 
 [5] https://github.com/mozilla/geckodriver/releases
