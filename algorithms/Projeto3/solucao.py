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

import numpy as np
import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.Qt import QVariant, QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsPointXY,
                       QgsPoint,
                       QgsFeature,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsGeometry,
                       QgsGeometryUtils)
import processing

class Projeto3Solucao(QgsProcessingAlgorithm):
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

    EDIFICACOES = 'EDIFICACOES'
    RODOVIAS = 'RODOVIAS'
    DESLOCAMENTO_MAXIMO = 'DESLOCAMENTO_MAXIMO'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterVectorLayer(self.EDIFICACOES, self.tr('Insira os edifícios'), 
                                                            types=[QgsProcessing.TypeVectorPoint], 
                                                            defaultValue=None))
        
        self.addParameter(QgsProcessingParameterVectorLayer(self.RODOVIAS, self.tr('Insira as rodovias'), 
                                                            types=[QgsProcessing.TypeVectorLine], 
                                                            defaultValue=None))
                
        self.addParameter(QgsProcessingParameterNumber(self.DESLOCAMENTO_MAXIMO,
                                                       self.tr('Insira a distância máxima de deslocamento'),
                                                       defaultValue=100,
                                                       type=QgsProcessingParameterNumber.Double))

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Edifícios generalizados'), 
                                                            type=QgsProcessing.TypeVectorPoint, 
                                                            createByDefault=True, 
                                                            supportsAppend=True, 
                                                            defaultValue='TEMPORARY_OUTPUT'))

    def processAlgorithm(self, parameters, context, feedback):

        edific_cam = self.parameterAsVectorLayer(parameters,self.EDIFICACOES,context)
        rodov_cam = self.parameterAsVectorLayer(parameters,self.RODOVIAS,context)
        max_desloc = self.parameterAsDouble(parameters,self.DESLOCAMENTO_MAXIMO,context)

        (output_sink,output_dest_id) = self.parameterAsSink(parameters,
                                                            self.OUTPUT,
                                                            context,
                                                            edific_cam.fields(),
                                                            1,
                                                            edific_cam.sourceCrs())

            
        self.processamento_rodov_edif(edific_cam, rodov_cam, max_desloc, output_sink, feedback)
        self.configureOutputLayerStyle(output_dest_id, context, feedback)
        return {self.OUTPUT: output_dest_id}
    
    def processamento_rodov_edif(self, edific_cam, rodov_cam, max_desloc, output_sink, feedback):
        total = 100.0 / edific_cam.featureCount() if edific_cam.featureCount() else 0
        
        edificios = edific_cam.getFeatures()
        dist_min_rodov = 32.5
        campos_sink = edific_cam.fields()

        for current, edificio in enumerate(edificios):
            edif_geom = edificio.geometry()
            for geometryParts in edif_geom.parts():
                for vertex in geometryParts.vertices():
                    novo_X, novo_Y = self.processamentoEdif(vertex, rodov_cam, dist_min_rodov, max_desloc, feedback)
                    # novo_X, novo_Y = self.deslocamento_edif(novo_X,novo_Y, edific_cam,v_x,v_y)
                    novo_edif = QgsGeometry.fromPointXY(QgsPointXY(novo_X,novo_Y))
                    newFeature = QgsFeature(campos_sink)
                    newFeature.setGeometry(novo_edif)
                    output_sink.addFeature(newFeature)

            feedback.setProgress(int(current * total))
            

              
    
    def processamentoEdif(self, vertex, rodov_cam, dist_min_rodov, max_desloc, feedback):
        novo_X = vertex.x()
        novo_Y = vertex.y()
        edif_atual = QgsGeometry.fromPointXY(QgsPointXY(vertex.x(),vertex.y()))
        for rodov in rodov_cam.getFeatures():
            rodov_geom = rodov.geometry()
            for part in rodov_geom.parts():
                edif_temp = QgsGeometry.fromPointXY(QgsPointXY(novo_X,novo_Y))
                point = QgsPoint(novo_X,novo_Y)
                distance = edif_temp.distance(rodov_geom)

                # Se a distancia for menor que a minima, separar da rodovia 
                if distance < dist_min_rodov:
                    closestPoint = QgsGeometryUtils.closestPoint(part,point)
                    closestX = closestPoint.x()
                    closestY = closestPoint.y()
                    dist = np.sqrt((novo_X-closestX)**2 + (novo_Y-closestY)**2)
                    novo_X = closestX + (dist_min_rodov)*(novo_X-closestX)/dist
                    novo_Y = closestY + (dist_min_rodov)*(novo_Y-closestY)/dist

                novo_edif = QgsGeometry.fromPointXY(QgsPointXY(novo_X,novo_Y))
                delta = novo_edif.distance(edif_atual)
                
                if delta > max_desloc:
                    novo_X = vertex.x()
                    novo_Y = vertex.y()

                if feedback.isCanceled():
                    break

        return novo_X, novo_Y 

    def configureOutputLayerStyle(self, output_dest_id, context, feedback):
        atual_dir = os.path.dirname(__file__)
        estilo = os.path.join(atual_dir, 'edificacoes.qml')
        alg_params = {
            'INPUT': output_dest_id,
            'STYLE': estilo
        }
        processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

    def name(self):
        return 'Solução Principal'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 3'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto3Solucao()