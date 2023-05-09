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

import pandas as pd
import geopandas as gpd

from qgis import processing
from qgis.utils import iface
from PyQt5.QtCore import QVariant
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsWkbTypes,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingUtils,
                       QgsVectorLayer,
                       QgsFeatureSink,
                       QgsExpression,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterRasterLayer,
                       QgsVectorFileWriter,
                       QgsCoordinateTransform,
                       QgsWkbTypes,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFields,
                       QgsFeature,
                       QgsField,
                       QgsRaster,
                       QgsMarkerSymbol,
                       QgsCategorizedSymbolRenderer,
                       QgsRendererCategory,
                       QgsSymbol,
                       QgsProcessingParameterFeatureSink
                    )


class Projeto2Solucao(QgsProcessingAlgorithm):

    """
    Definindo as constantes
    """
    
    # INPUTS 
    INPUT_DRAINAGES = 'INPUT_DRAINAGES'
    INPUT_SINK_SPILL = 'INPUT_SINK_SPILL'
    INPUT_WATER_BODY = 'INPUT_WATER'
    INPUT_CANAL = 'INPUT_CANAL'

    # OUTPUTS
    POINTFLAGS = 'POINTFLAGS'
    LINEFLAGS = 'LINEFLAGS'
    POLYGONFLAGS = 'POLYGONFLAGS'
      
    def initAlgorithm(self, config=None):

        #INPUTS
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_DRAINAGES, 
                                                            'Drenagens',
                                                            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_SINK_SPILL, 
                                                            'Sumidouros e Vertedouros', 
                                                             types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_CANAL, 
                                                            'Canais', 
                                                             types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_WATER_BODY, 
                                                            'Massa de Agua', 
                                                            types=[QgsProcessing.TypeVectorPolygon]))
        
        #OUTPUTS
        self.addParameter(QgsProcessingParameterFeatureSink(self.POINTFLAGS, 'Erros pontuais'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.LINEFLAGS, 'Erros em linhas'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.POLYGONFLAGS, 'Erros em polígonos'))


  
      
    def processAlgorithm(self, parameters, context, feedback):
        #Store the input variables
        drains = self.parameterAsSource(parameters,
                                        self.INPUT_DRAINAGES,
                                        context)
        sink_spills_points = self.parameterAsSource(parameters,
                                                    self.INPUT_SINK_SPILL,
                                                    context)
        water_body = self.parameterAsSource(parameters,
                                            self.INPUT_WATER_BODY,
                                            context)
        canals = self.parameterAsSource(parameters,
                                        self.INPUT_CANAL,
                                        context)
        
        # Outputs terão um campo de atributo explicando a razão da flag
        fields = QgsFields()
        fields.append(QgsField("Motivo", QVariant.String))

        # Configurando os Outputs 
        (sink_point, dest_id_point) = self.parameterAsSink(parameters,
                                                           self.POINTFLAGS,
                                                           context,
                                                           fields,
                                                           QgsWkbTypes.Point,
                                                           drains.sourceCrs())
        
        (sink_line, dest_id_line) = self.parameterAsSink(parameters,
                                                         self.LINEFLAGS,
                                                         context,
                                                         fields,
                                                         QgsWkbTypes.LineString,
                                                         drains.sourceCrs()) 

        (sink_polygon, dest_id_polygon) = self.parameterAsSink(parameters,
                                                               self.POLYGONFLAGS,
                                                               context,
                                                               fields,
                                                               QgsWkbTypes.Polygon,
                                                               drains.sourceCrs()
                                                               )
        
        
        

        
        # Calculando a estrutura das linhas
        pointInAndOutDictionary = {}

        lineCount = drains.featureCount()
        multiStepFeedback = QgsProcessingMultiStepFeedback(2, feedback)
        multiStepFeedback.setCurrentStep(0)
        multiStepFeedback.setProgressText(self.tr("Calculando a estrutura das Linhas..."))
        stepSize = 100/lineCount

        # Adicionando ao dicionário a quantidade de linhas que entram e saem de um determinado ponto
        for current, line in enumerate(drains.getFeatures()):
            if multiStepFeedback.isCanceled():
                break
            geom = list(line.geometry().vertices())
            if len(geom) == 0:
                continue
            first_vertex = geom[0]
            last_vertex = geom[-1]

            if first_vertex.asWkt() not in pointInAndOutDictionary:
                pointInAndOutDictionary[first_vertex.asWkt()] = { "incoming": 0, "outgoing": 0}

            if last_vertex.asWkt() not in pointInAndOutDictionary:
                pointInAndOutDictionary[last_vertex.asWkt()] = { "incoming": 0, "outgoing": 0}
            
            pointInAndOutDictionary[first_vertex.asWkt()]["outgoing"] += 1
            pointInAndOutDictionary[last_vertex.asWkt()]["incoming"] += 1
            multiStepFeedback.setProgress(current * stepSize)
        
        multiStepFeedback.setCurrentStep(1)
        stepSize = 100/len(pointInAndOutDictionary)

   ###############################################################################################
   ######################################### ITEM 1 ##############################################    
   ###############################################################################################
        for current, (point, dictCounter) in enumerate(pointInAndOutDictionary.items()):
            if multiStepFeedback.isCanceled():
                break
            errorMsg = self.errorWhenCheckingInAndOut(dictCounter)
            if errorMsg != '':
                flagFeature = QgsFeature(fields)
                flagFeature.setGeometry(QgsGeometry.fromWkt(point))
                flagFeature["Motivo"] = errorMsg
                sink_point.addFeature(flagFeature)
        
        
        
        
                



   ###############################################################################################
   ###################################### ITEM 2 e 3 #############################################    
   ###############################################################################################

    #Iterando sobre o dicionario e vendo se algum dos pontos do tipo sumidouro estão no caso em que
    #"Incoming = 0" e "Outgoing = 1"
        for point in sink_spills_points.getFeatures():
            sink_type = point.attributes()[4]
            if sink_type != 1:
                continue
            for (point_wkt,in_out) in pointInAndOutDictionary.items():
                if (in_out["incoming"] ==0 and in_out["outgoing"] == 1):
                    if point.geometry().equals(QgsGeometry.fromWkt(point_wkt)):
                        flagFeature = QgsFeature(fields)
                        flagFeature.setGeometry(QgsGeometry.fromWkt(point.geometry().asWkt()))
                        flagFeature["Motivo"] = "Não pode ser um Sumidouro"
                        sink_point.addFeature(flagFeature)
    #Mesma Lógica para "Incoming=1" e "Outgoing = 0"
        for point in sink_spills_points.getFeatures():
            sink_type = point.attributes()[4]
            if sink_type != 2:
                continue
            for (point_wkt,in_out) in pointInAndOutDictionary.items():
                if (in_out["incoming"] ==1 and in_out["outgoing"] == 0):
                    if point.geometry().equals(QgsGeometry.fromWkt(point_wkt)):
                        flagFeature = QgsFeature(fields)
                        flagFeature.setGeometry(QgsGeometry.fromWkt(point.geometry().asWkt()))
                        flagFeature["Motivo"] = "Não pode ser um Vertedouro"
                    
                

    


   #################################### ITEM 4, 5 e 6 ############################################    
   ###############################################################################################

   ###############################################################################################
   ######################################### ITEM 7 ##############################################    
   ###############################################################################################

   ###############################################################################################
   ######################################### ITEM 8 ##############################################    
   ###############################################################################################      

        return {self.POINTFLAGS: dest_id_point,
                self.LINEFLAGS: dest_id_line,
                self.POLYGONFLAGS: dest_id_polygon} 
        
    def tr(self, string):
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return Projeto2Solucao()

    def name(self):
        return 'Solução do Projeto 2'

    def displayName(self):
        return self.tr(self.name())

    def group(self):        
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 2'
        
    def shortHelpString(self):
        return self.tr("""ESCREVER AQUI"""
                       )
    
    """ 

    FUNÇÕES AUXILIARES
    """
    
    def errorWhenCheckingInAndOut(self, inAndOutCounters):
        incoming = inAndOutCounters["incoming"]
        outgoing = inAndOutCounters["outgoing"]
        total = incoming + outgoing

        if total == 1:
            return ''
        if total >= 4:
            return '4 or more lines conected to this point.'
        
        if (incoming == 0):
            return 'There are lines coming from this point, but not lines going in.'

        if (outgoing == 0):
            return 'There are lines going into this point, but not lines coming from it.'

        return ''

