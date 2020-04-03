# Cyberattacks-History
Proyecto para la asignatura M2.851

[Versón en desarrollo]

La versión actual incluye princpalmente la idea y el guión que estamos siguiendo para el desarrollo de la práctica. Este documento puede revisarse en la carpeta "pdf".

En cuanto al grado de desarrollo, de momento se encuentran subidos los siguientes archivos con código fuente:

* main.py: Será el script principal a partir del cual se enlazarán los distintos desarrollos que estamos abordando en paralelo.
* constants.py: Contiene las variables globales y la definición de la estructura del dataset. A partir de ésta, definiremos en el informe las características de los campos. A fecha de presentación de este grado de avance, la definición inicial del dataset consiste en lo siguiente: 

    FIELDS_NAME = \
    ["id", "date", "author", "target", "description", "attack", "target_class", "attack_class", "country", "link",
     "tag", 'author_report', 'date_report']
     
* scrapper.py: Tareas de scraping recursivas a través de los informes quincenales que se presentan desde el año 2019. Este código aún no es funcional porque hemos identificado discrepancias en las tablas que se presentan en algunas quincenas, y estamos trabajando en reparar la extracción para esos periodos.
* scraper_Masters: A partir de la URL principal del site, www.hackmageddon.com, identifica los enlaces a los informes anuales, y ejecuta el script adecuado para cada uno de ellos (hay dos formatos distintos, que requieren técnicas de scraping distintas).
* scraper_Master2017: Scraper del historial anual para el caso del formato del año 2017. Se basa en la descarga de una archivo almacenado en google docs.
* scraper_Master2018: Scraper del historial anual para el caso del formato del año 2018. Se basa en la descarga a través de un botón de un applet de Java.


Principales hitos pendientes, planificados en el proyecto:
* Scraper de los informes quincenales desde 2019 en adelante (corregir código).
* Consolidar en un único script los distintos scrapers para los distintos formatos que hemos ido identificando.
* Consolidación y normalización de formatos de los distintos scrapers para disponer de un dataset final único para todo el periodo con datos.
* Incorporación de parámetros de entrada que permitan indicar al scraper de qué periodo se desean extraer datos, y que sólo ejecute las tareas de scraping mínimas para generar el dataset.
* Creación de una wiki explicativa del proceso. 
