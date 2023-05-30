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

import os
import processing

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingFeatureSourceDefinition,
                       QgsFeature, QgsGeometry, QgsPoint, QgsPointXY, QgsGeometryUtils)

import math
import random
from qgis.core import QgsProcessingUtils, QgsProject


class MoveBuildings(QgsProcessingAlgorithm):
    BUILDINGS = 'BUILDINGS'
    ROADS = 'ROADS'
    DISTANCE = 'DISTANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.BUILDINGS, 'Camada de Edificações', [QgsProcessing.TypeVectorPoint]))
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ROADS, 'Camada de Rodovias', [QgsProcessing.TypeVectorLine]))
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE, 'Distância de deslocamento', minValue=0, defaultValue=10))
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT, 'Edificações Deslocadas'))

    def processAlgorithm(self, parameters, context, feedback):
        source_buildings = self.parameterAsSource(parameters, self.BUILDINGS, context)
        source_roads = self.parameterAsSource(parameters, self.ROADS, context)
        maxDisplacementDistance = self.parameterAsDouble(parameters, self.DISTANCE, context)
        min_building_distance = maxDisplacementDistance

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               source_buildings.fields(), source_buildings.wkbType(),
                                               source_buildings.sourceCrs())

        minDistHighway = 35.0  # Adapt this value as necessary
        moved_buildings = []

        for building in source_buildings.getFeatures():
            buildingGeometry = building.geometry()
            for vertex in buildingGeometry.vertices():
                newX, newY = self.processVertex(vertex, source_roads, minDistHighway, maxDisplacementDistance, feedback)
                newBuilding = QgsGeometry.fromPointXY(QgsPointXY(newX, newY))

                while self.too_close_to_other_buildings(newBuilding, moved_buildings, min_building_distance) or self.near_highway(newBuilding, source_roads, minDistHighway):
                    feedback.reportError('Building is too close to another building or highway, adjusting position')
                    # Move the building slightly in a random direction
                    newBuilding.translate(random.uniform(-1, 1), random.uniform(-1, 1))

                building.setGeometry(newBuilding)
                moved_buildings.append(building)
                sink.addFeature(building)

        return {self.OUTPUT: dest_id}

    def processVertex(self, vertex, highwaysLayer, minDistHighway, maxDisplacementDistance, feedback):
        initialX = vertex.x()
        initialY = vertex.y()
        newX = initialX
        newY = initialY

        for highway in highwaysLayer.getFeatures():
            highwayGeometry = highway.geometry()
            for highwayPart in highwayGeometry.parts():
                tempBuilding = QgsGeometry.fromPointXY(QgsPointXY(newX, newY))
                tempGeo = QgsPoint(newX, newY)
                distance = tempBuilding.distance(highwayGeometry)

                if distance < minDistHighway:
                    closestPoint = QgsGeometryUtils.closestPoint(highwayPart, tempGeo)
                    closestX = closestPoint.x()
                    closestY = closestPoint.y()
                    factor = ((newX - closestX) ** 2 + (newY - closestY) ** 2) ** 0.5
                    newX = closestX + (minDistHighway / factor) * (newX - closestX)
                    newY = closestY + (minDistHighway / factor) * (newY - closestY)

                tempBuilding_n = QgsGeometry.fromPointXY(QgsPointXY(newX, newY))
                tempBuilding_i = QgsGeometry.fromPointXY(QgsPointXY(initialX, initialY))
                displacement = tempBuilding_n.distance(tempBuilding_i)
                if displacement > maxDisplacementDistance:
                    newX = initialX
                    newY = initialY

                if feedback.isCanceled():
                    break

        return newX, newY

    def too_close_to_other_buildings(self, building_geometry, buildings_list, min_distance):
        for other_building in buildings_list:
            other_building_geometry = other_building.geometry()
            if building_geometry.distance(other_building_geometry) < min_distance:
                return True
        return False

    def near_highway(self, building_geometry, highways_layer, min_distance):
        for highway in highways_layer.getFeatures():
            highway_geometry = highway.geometry()
            if building_geometry.distance(highway_geometry) < min_distance:
                return True
        return False

    def name(self):
        return 'movebuildings'

    def displayName(self):
        return 'Deslocar Edificações'

    def group(self):
        return 'Exemplos'

    def groupId(self):
        return 'examples'
    
    def configureOutputLayerStyle(self, output_dest_id, context, feedback):
        atual_dir = os.path.dirname(_file_)
        estilo = os.path.join(atual_dir, 'edificacoes.qml')
        alg_params = {
            'INPUT': output_dest_id,
            'STYLE': estilo
        }
        processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
    def createInstance(self):
        return MoveBuildings()
