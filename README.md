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
Carpeta almacenada para  

### Drivers
Carpeta que contiene los drivers de Chrome y FireFox necesarios para poder ejecutar selenium. Estos drivers son compatibles con las versiones:
    - _CHROME_: 
    - _FIREFOX_:
### Data
Carpeta utilizada para almacenar la información extraída por el programa al finalizar el scraping. Los datos obtenidos, son almacenados en formato csv. 

La carpeta data se divide en:
 ## Referéncias
 [1] https://www.hackmageddon.com/category/security/cyber-attacks-timeline/
 [2] https://www.hackmageddon.com/2018-master-table/
 [3] https://www.hackmageddon.com/2017-master-table/
