# komoot2GIS
Import your komoot routes in the GIS of your choice
## ArcGIS
To download a komoot route as a layer for ArcGIS Pro (tested with 2.2.1), download or clone the repo and add the file ArcGIS\Komoot2ArcGIS.pyt as a python toolbox to your project. After running the tool, you will be able to save it locally in GPX or whatever you like. Even Shapefile ;-):

![Python Toolbox in ArcGIS Pro](https://i.imgur.com/ervC9ri.png)
## QGIS
The QGIS solution works as a geoprocessing script. Download or clone the repo and add the file QGIS\KomootImportScript.py as a script to your QGIS project. It was developed using QGIS 3.2

![Geoprocessing in QGIS](https://i.imgur.com/97TatSq.png)

## Usage
To get the geometry of your planned tour copy the tour ID of the route-page from Komoot. 
As an example a planned tour is hosted here:
![Komoot tour](https://i.imgur.com/nVRlQd9.png)
The URL of the page contains the tour ID: https://www.komoot.com/tour/27555914

Both solutions (QGIS and ArcGIS) use the tour ID "27555914" as an input, donwloads the geometry and creates a polyline and point layer.

The layers in QGIS:
![QGIS result](https://i.imgur.com/Nm0XFsX.png)

The layers in ArcGIS:
![QGIS result](https://i.imgur.com/fo8mw4j.png)
