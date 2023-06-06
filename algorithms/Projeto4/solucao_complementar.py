# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupo2
                                 A QGIS plugin
 Solução do Grupo 2
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-05
        copyright            : (C) 2023 by Grupo 2
        email                : matheus.ferreira@ime.eb.br
                               leonardo.fernandes@ime.eb.br
                               daniel.nojima@ime.eb.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Grupo 2'
__date__ = '2023-05-05'
__copyright__ = '(C) 2023 by Grupo 2'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterDistance,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsProcessingFeatureSourceDefinition,
                       QgsProcessingFeatureSource,
                       QgsProcessingFeedback,
                       QgsProcessingContext,
                       QgsVectorLayer,
                       QgsVectorFileWriter,
                       QgsFeatureSink,
                       QgsProcessingException)

from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication

class Projeto4SolucaoComplementar(QgsProcessingAlgorithm):
    BUILDINGS = 'BUILDINGS'
    BOUNDARIES = 'BOUNDARIES'
    DISTANCE = 'DISTANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.BUILDINGS, 'Camada de Edificações', [QgsProcessing.TypeVectorPolygon])
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.BOUNDARIES, 'Camada de Molduras', [QgsProcessing.TypeVectorPolygon])
        )
        self.addParameter(
            QgsProcessingParameterDistance(
                self.DISTANCE, 'Distância do Buffer', defaultValue=0.0001)
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT, 'Camada de Saída')
        )

    def processAlgorithm(self, parameters, context, feedback):
        buildings_layer = self.parameterAsVectorLayer(parameters, self.BUILDINGS, context)
        boundaries_layer = self.parameterAsVectorLayer(parameters, self.BOUNDARIES, context)
        distance = self.parameterAsDouble(parameters, self.DISTANCE, context)

        if buildings_layer is None or boundaries_layer is None:
            raise QgsProcessingException('Invalid input layer.')

        # Extrair bordas dos polígonos da camada de molduras
        (boundaries_sink, boundaries_dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                                                     QgsFields(), QgsWkbTypes.MultiLineString,
                                                                     buildings_layer.sourceCrs())

        boundaries_result = processing.run('native:boundary', {
            'INPUT': boundaries_layer,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)

        for feature in boundaries_result['OUTPUT'].getFeatures():
            boundaries_sink.addFeature(feature)

        # Criar buffer e interseção
        (buffer_intersect_sink, buffer_intersect_dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                                                                 boundaries_result['OUTPUT'].fields(),
                                                                                 boundaries_result['OUTPUT'].wkbType(),
                                                                                 boundaries_result['OUTPUT'].sourceCrs())

        total = 100.0 / buildings_layer.featureCount() if buildings_layer.featureCount() else 0

        buildings_features = buildings_layer.getFeatures()
        for current, building_feat in enumerate(buildings_features):
            if feedback.isCanceled():
                break

            # Criar buffer
            building_geom = building_feat.geometry().buffer(distance, 5)
            if building_geom.isEmpty():
                continue

            boundaries_features = boundaries_result['OUTPUT'].getFeatures()
            for boundary_feat in boundaries_features:
                boundary_geom = boundary_feat.geometry()

                if building_geom.intersects(boundary_geom):
                    intersected_geom = building_geom.intersection(boundary_geom)

                    if intersected_geom.wkbType() == QgsWkbTypes.LineString:
                        new_feature = QgsFeature(boundary_feat)
                        new_feature.setGeometry(intersected_geom)
                        buffer_intersect_sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        return {self.OUTPUT: buffer_intersect_dest_id}


    def name(self):
        return 'Solução Complementar do Projeto 4'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 4'

    def shortHelpString(self):
        return self.tr("""
                          """
                       )
    
    def tr(self, string):
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return Projeto4SolucaoComplementar()
    
    