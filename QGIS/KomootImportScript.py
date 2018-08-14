# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
					   QgsPoint,
                       QgsPointXY,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem)
import processing
import urllib.request, json, os

class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    RouteID = 'RouteID'
    PointLayer = 'PointLayer'
    LineLayer = 'LineLayer'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'KomootImporter'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Import Komoot Data')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Komoot')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Komoot'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("import Komoot Data from an ID.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterString(
                self.RouteID,
                self.tr('Komoot Route ID'),
                '41193460'
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.PointLayer,
                self.tr('Output Point layer'),
                QgsProcessing.TypeVectorPoint
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.LineLayer,
                self.tr('Output Line layer'),
                QgsProcessing.TypeVectorLine
            )
        )
        #self.addParameter(
        #    QgsProcessingOutputVectorLayer(
        #        self.PointLayer,
        #        self.tr('Output Point layer'),
        #        type = QgsProcessing.TypeVectorPoint
        #    )
        #)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
    
        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.RouteID,
            context
        )
        feedback.setProgressText("we collect the route" + parameters['RouteID'])
        with urllib.request.urlopen("https://api.komoot.de/v007/tours/" + parameters['RouteID'] + "/coordinates") as url:
            data = json.loads(url.read())
        feedback.setProgressText("Number of points: " + str(len(data["items"])))
        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.Int))
        fields.append(QgsField("LAT", QVariant.Double))
        fields.append(QgsField("LNG", QVariant.Double))
        fields.append(QgsField("TIME", QVariant.Double))
        fields.append(QgsField("HEIGHT", QVariant.Double))
        (sink, dest_id) = self.parameterAsSink(parameters, self.PointLayer, context,
                                               fields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem(4326))
        id=0
        points = []
        for vertex in data["items"]:
            
            out_feat = QgsFeature()
            points.append(QgsPoint(vertex["lng"],vertex["lat"]))
            out_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(vertex["lng"],vertex["lat"])))
            out_feat.setAttributes([id, vertex["lat"],vertex["lng"],vertex["t"],vertex["alt"]])
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)
            id+=1
        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.String))
        (sinkline, dest_id2) = self.parameterAsSink(parameters, self.LineLayer, context,
                                               fields, QgsWkbTypes.LineString, QgsCoordinateReferenceSystem(4326))
        out_feat = QgsFeature()
        out_feat.setGeometry(QgsGeometry.fromPolyline(points))
        out_feat.setAttributes([parameters['RouteID']])
        sinkline.addFeature(out_feat)
        results = {}
        results[self.PointLayer]=sink
        results[self.LineLayer]=sinkline
        return results