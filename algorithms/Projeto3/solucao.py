# -*- coding: utf-8 -*-

"""
/***************************************************************************
<<<<<<< HEAD
 DeslocamentoEdificacoes
                                 A QGIS plugin
 Movendo edificacoes fora das rodovias
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-20
        copyright            : (C) 2023 by OpenAI
        email                : openai@example.com
=======
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
>>>>>>> dbc3911de928f810fc5311ef1afcc6fd8d2fbc2d
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

<<<<<<< HEAD
__author__ = 'OpenAI'
__date__ = '2023-03-20'
__copyright__ = '(C) 2023 by OpenAI'
=======
__author__ = 'Grupo 2'
__date__ = '2023-05-05'
__copyright__ = '(C) 2023 by Grupo 2'
>>>>>>> dbc3911de928f810fc5311ef1afcc6fd8d2fbc2d

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

<<<<<<< HEAD
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, 
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFeatureSink,
                       QgsFeature,
                       QgsVectorLayer,
                       QgsGeometry,
                       QgsFeatureSink
                       )

class DeslocamentoEdificacoes(QgsProcessingAlgorithm):

    INPUT_EDIFICACOES = 'INPUT_EDIFICACOES'
    INPUT_RODOVIAS = 'INPUT_RODOVIAS'
    DISTANCIA = 'DISTANCIA'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return DeslocamentoEdificacoes()

    def name(self):
        return 'deslocamento_edificacoes'

    def displayName(self):
        return self.tr('Deslocamento de Edificações')

    def group(self):
        return self.tr('Exemplos')

    def groupId(self):
        return 'exemplos'

    def shortHelpString(self):
        return self.tr("O algoritmo move as edificações para a lateral da rodovia, caso a edificação esteja em cima da rodovia")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_EDIFICACOES,
                self.tr('Camada de Edificações'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_RODOVIAS,
                self.tr('Camada de Rodovias'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterDistance(
                self.DISTANCIA,
                self.tr('Distância de deslocamento'),
                parentParameterName=self.INPUT_EDIFICACOES,
                minValue=0,
                defaultValue=10
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Edificações Deslocadas')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        edificacoes_layer = self.parameterAsVectorLayer(parameters, self.INPUT_EDIFICACOES, context)
        rodovias_layer = self.parameterAsVectorLayer(parameters, self.INPUT_RODOVIAS, context)
        distancia = self.parameterAsDouble(parameters, self.DISTANCIA, context)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               edificacoes_layer.fields(),
                                               edificacoes_layer.wkbType(),
                                               edificacoes_layer.sourceCrs())

        for edificacao in edificacoes_layer.getFeatures():
            for rodovia in rodovias_layer.getFeatures():
                if edificacao.geometry().intersects(rodovia.geometry()):
                    new_geom = edificacao.geometry().translate(-distancia, -distancia)
                    new_feature = QgsFeature(edificacao)
                    new_feature.setGeometry(new_geom)
                    sink.addFeature(new_feature, QgsFeatureSink.FastInsert)
                else:
                    sink.addFeature(edificacao, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}
=======
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
                       QgsSpatialIndex,
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


class Projeto3Solucao(QgsProcessingAlgorithm):

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
                                                           drains.sourceCrs()
                                                           )
        
        (sink_line, dest_id_line) = self.parameterAsSink(parameters,
                                                         self.LINEFLAGS,
                                                         context,
                                                         fields,
                                                         QgsWkbTypes.LineString,
                                                         drains.sourceCrs()
                                                         ) 

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
                
   ###############################################################################################
   ######################################### ITEM 1 ##############################################    
   ###############################################################################################

        for current, (point, dictCounter) in enumerate(pointInAndOutDictionary.items()):
            if multiStepFeedback.isCanceled():
                break
            errorMsg = self.errorWhenCheckingInAndOut(dictCounter)
            if errorMsg != '':
                flag = QgsFeature(fields)
                flag.setGeometry(QgsGeometry.fromWkt(point))
                flag["Motivo"] = errorMsg
                sink_point.addFeature(flag)

   ###############################################################################################
   ###################################### ITEM 2 e 3 #############################################    
   ###############################################################################################

   # TO DO
   ########################################### ITEM 4 ############################################    
   ###############################################################################################

   ###############################################################################################
   ######################################### ITEM 7 ##############################################    
   ###############################################################################################


   ##############################################################################################
   ######################################## ITEM 8 ##############################################    
   ###############################################################################################      

                    
        return {self.POINTFLAGS: dest_id_point,
                self.LINEFLAGS: dest_id_line,
                self.POLYGONFLAGS: dest_id_polygon} 
        
    def tr(self, string):
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return Projeto3Solucao()

    def name(self):
        return 'Solução do Projeto 3'

    def displayName(self):
        return self.tr(self.name())

    def group(self):        
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 3'
        
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
            return 'Existem linhas saindo desse ponto, mas não tem linhas entrando'

        if (outgoing == 0):
            return 'Existem linhas entrando nesse ponto, mas não tem linhas saindo dele'

        return ''
    
>>>>>>> dbc3911de928f810fc5311ef1afcc6fd8d2fbc2d
