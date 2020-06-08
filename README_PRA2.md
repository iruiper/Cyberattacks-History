# Cyberattacks-History. PRA2
Partiendo de la motivación expuesta en la primera parte de la práctica, a continuación describimos la estructura de carpetas y de ficheros que permiten hacer seguimiento del trabajo de tratamiento y análisis que hemos abordado en la segunda parte de la práctica. 

Tal y como referimos en README.md, esta segunda parte del proyecto, trata de resolver los problemas de calidad de datos (valores ausentes, extremos, errores en la generación de ficheros, etc.) que tenían los ficheros en bruto, así como las agregaciones y procesamiento necesarios para disponer de ficheros útiles para el análisis.

Para ello, podemos hablar de 4 grandes tareas, cuya documentación y código soporte se presentan en la sección "Contenido":
- Análisis exploratorio preliminar en R para identificacar los problemas de Calidad del Dato.
- Corrección en los csv y mejora de las tareas previas de acondicionamiento, directamente mediante Python, con el objetivo de mitigar los problemas de valores ausentes por errores, o outliers.
- Planteamiento, análisis estadístico y obtención de conclusiones, a través de R.
- Aplicación de técnicas de visualización, para aportar conclusiones gráficas y explicaciones adicionales, a través de jupyter notebooks en python.

## Miembros del equipo
La actividad ha sido realizada por **Iván Ruiz** y **Joel Bustos**.

## Contenido
El proyecto está estructurado en las siguientes carpetas.

### src
Contiene el código en Python adicional al desarrollado en la PRA1. Este, se encuentra bajo el nombre **data_processing.py**, y realiza las tareas de preprocesamiento y corrección de errores detectados a través de los procesos de procesos de control de calidad.

### R_Analysis
- **M2.851_20192_JoelBustos_IvanRuiz-PRA2.rmd**: Archivo con markdown que recoge las tareas de análisis explotatorio y análisis estadístico que hemos llevado a cabo para la obtención de respuestas a las preguntas que nos planteábamos, y que hemos descrito y analizado en el documento explicativo de la práctica.

### Visual
Contiene el código de las representaciónes gráficas que hemos llevado a cabo en las etapas de interpretación y obtención de conclusiones para nuestro trabajo. La carpeta contiene los siguientes jupyters notebooks.
- **_attack_viz.ipynb_**: visualizaciones de las distribuciones de ataques.

- **_region_viz.ipynb_**: visualizaciones de las distribuciones de ataque a lo largo de los distintos continentes.

- **_sankey_viz.ipynb_**: visualizaciones de los parallel sets que relacionan el tipo de autor causante del ataque cibernetico, con el tipo de ataque realizado y el sector afectado.

### Data
Carpeta con los distintos ficheros fuente y tratados que hemos utilizado a lo largo de la práctica. 

La carpeta data se divide en:
- **00_raw_:** Carpeta con archivos en bruto, descritos en README_PRA1.md. Adicionalmente, para la segunda parte del análisis hemos añadido el siguiente fichero:
     
     - **_DatosAtaques_2017_2020_RAW.csv_**: Información en bruto, agregada a partir de las extracciones individuales de la PRA1, con el único objetivo de poder llevar a cabo un análisis preliminar de algunas variables.
     - **_Error-files.csv_**: Información en bruto con aquellos reportes que han dado problemas durante la fase de scrapping.
     - **_scrapping 2020-06-05 17.25.57.csv_**: Información en bruto que contiene los datos rasgados a partir del reporte: https://www.hackmageddon.com/2020/05/26/16-30-april-2020-cyber-attacks-timeline/
        
- **01_clean:** Carpeta destinada a almacenar los datos procesados y limpios procedentes de _00_raw_. En concreto, a través de los distintos procesos de acondicionamiento y limpieza de datos, hemos creado los siguientes ficheros:

     - **_EstadisticasAtaques2017_2020_Input.csv_**: Archivo con la información de ataques en el periodo 2017-2020, con las tareas de acondicionamiento que nos han permitido crear variables cuantitativas y diversas tareas de limpieza de datos, que describimos en el informe.
     - **_EstadisticasAtaques2017_2020_Input_Visualization.csv_**: Archivo utilizado para generar visualizaciones.
     - **_datos_test.csv_**: Archivo con la información procesada a partir del archivo _scrapping 2020-06-05 17.25.57.csv_. Este ficherose utilizará como set de test para el análisis medir la precisión de los modelos implementados y descritos en la memoria.

- **99_aditional:** Carpeta con información complementaria que hemos necesitado utilizar en nuestro análisis. En concreto, contiene el siguiente fichero:

     - **_continent_country.xlsx_**: Relación de "Código de país"-"Continente" utilizado para el mapping de la información geográfica contenida en el dataset.


### PDF
La carpeta "PRA2" contiene el documento explicativo de la práctica.

 ## Referencias
 [1] https://www.hackmageddon.com/category/security/cyber-attacks-timeline/
 
