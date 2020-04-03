# Cyberattacks-History
Proyecto para la asignatura M2.851

[Versón en desarrollo]

La versión actual incluye princpalmente la idea y el guión que estamos siguiendo para el desarrollo de la práctica. Este documento puede revisarse en la carpeta "pdf".

En cuanto al grado de desarrollo, de momento se encuentran subidos los siguientes archivos con código fuente:

* scraper_Masters: A partir de la URL principal del site, www.hackmageddon.com, identifica los enlaces a los informes anuales, y ejecuta el script adecuado para cada uno de ellos (hay dos formatos distintos, que requieren técnicas de scraping distintas).
* scraper_Master2017: Scraper del historial anual para el caso del formato del año 2017. Se basa en la descarga de una archivo almacenado en google docs.
* scraper_Master2018: Scraper del historial anual para el caso del formato del año 2018. Se basa en la descarga a través de un botón de un applet de Java.


Principales hitos pendientes, planificados en el proyecto:
* Scraper de los informes quincenales desde 2019 en adelante.
* Consolidación y normalización de formatos de los distintos scrapers para disponer de un dataset final único para todo el periodo con datos.
* Incorporación de parámetros de entrada que permitan indicar al scraper de qué periodo se desean extraer datos, y que sólo ejecute las tareas de scraping mínimas para generar el dataset.

