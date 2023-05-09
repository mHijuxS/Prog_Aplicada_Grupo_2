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


import processing
from qgis.utils import iface
from PyQt5.QtCore import QVariant
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsWkbTypes,
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
    Funções Auxiliares
    """

    """DSG TOOLS VALIDATION ALGORITHMS"""
    def prepareFlagSink(self, parameters, source, wkbType, context):
        (self.flagSink, self.flag_id) = self.prepareAndReturnFlagSink(
            parameters,
            source,
            wkbType,
            context,
            self.FLAGS
            )
    
    def prepareAndReturnFlagSink(self, parameters, source, wkbType, context, UI_FIELD):
        flagFields = self.getFlagFields()
        (flagSink, flag_id) = self.parameterAsSink(
            parameters,
            UI_FIELD,
            context,
            flagFields,
            wkbType,
            source.sourceCrs() if source is not None else QgsProject.instance().crs()
        )
        if flagSink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, UI_FIELD))
        return (flagSink, flag_id)

    def getFlagFields(self):
        fields = QgsFields()
        fields.append(QgsField('reason',QVariant.String))
        return fields
    
    def flagFeature(self, flagGeom, flagText, fromWkb=False, sink=None):
        """
        Creates and adds to flagSink a new flag with the reason.
        :param flagGeom: (QgsGeometry) geometry of the flag;
        :param flagText: (string) Text of the flag
        """
        flagSink = self.flagSink if sink is None else sink
        newFeat = QgsFeature(self.getFlagFields())
        newFeat['reason'] = flagText
        if fromWkb:
            geom = QgsGeometry()
            geom.fromWkb(flagGeom)
            newFeat.setGeometry(geom)
        else:
            newFeat.setGeometry(flagGeom)
        flagSink.addFeature(newFeat, QgsFeatureSink.FastInsert)
    """"""
    
    def initAlgorithm(self, config=None):

        #INPUTS
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_DRAINAGES, 
                                                            'Drenagens',
                                                            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_SINK_SPILL, 
                                                            'Sumidouros e Vertedouros', 
                                                             types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_CANAL, 
                                                            'Canais', 
                                                             types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_WATER_BODY, 
                                                            'Massa de Agua', 
                                                            types=[QgsProcessing.TypeVectorPolygon]))
        
        #OUTPUTS
        self.addParameter(QgsProcessingParameterFeatureSink(self.POINTFLAGS, 'Erros pontuais', 
                                                            type=QgsProcessing.TypeVectorPoint, 
                                                            createByDefault=True, 
                                                            supportsAppend=True, 
                                                            defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.LINEFLAGS, 'Erros em linhas', 
                                                            type=QgsProcessing.TypeVectorLine, 
                                                            createByDefault=True, 
                                                            supportsAppend=True, 
                                                            defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.POLYGONFLAGS, 'Erros em polígonos', 
                                                            type=QgsProcessing.TypeVectorPolygon, 
                                                            createByDefault=True, 
                                                            supportsAppend=True, 
                                                            defaultValue='TEMPORARY_OUTPUT'))


  
      
    def processAlgorithm(self, parameters, context, feedback):
        #Store the input variables
        drains = self.parameterAsVectorLayer(parameters,
                                             self.INPUT_DRAINAGES,
                                             context)
        sink_spills_points = self.parameterAsVectorLayer(parameters,
                                                         self.INPUT_SINK_SPILL,
                                                         context)
        water_body = self.parameterAsVectorLayer(parameters,
                                                   self.INPUT_WATER_BODY,
                                                   context)
        canals = self.parameterAsVectorLayer(parameters,
                                             self.INPUT_CANAL,
                                             context)
        
        #Separating Water Bodies with and without flux of water
        # Defining the Water Body with flow and without flow
        ## Without Flow
        water_body_no_flow = QgsVectorLayer(water_body.source(), 'water_body_no_flow', water_body.providerType())
        filter = QgsExpression('possuitrechodrenagem = 0')
        water_body_no_flow.setSubsetString(filter.expression())

        ## With Flow 
        water_body_with_flow = QgsVectorLayer(water_body.source(), 'water_body_with_flow', water_body.providerType())
        filter = QgsExpression('possuitrechodrenagem = 1')
        water_body_with_flow.setSubsetString(filter.expression())
        
        #Applying the same logic for the Sink and Spill Points
        sink_points = QgsVectorLayer(sink_spills_points.source(), 'sink_points', sink_spills_points.providerType())
        filter = QgsExpression('tiposumvert = 1')
        sink_points.setSubsetString(filter.expression())

        spill_points = QgsVectorLayer(sink_spills_points.source(), 'spill_points', sink_spills_points.providerType())
        filter = QgsExpression('tiposumvert = 2')
        spill_points.setSubsetString(filter.expression())

        #Applying the same logic for the Ocean=3, Bay=4 and Cove=5
        #filter = QgsExpression('tipomassadagua = ')

        # Setting the flags for output
        (self.pointFlagSink, self.point_flag_id) = self.prepareAndReturnFlagSink(parameters,
                                                                                 drains,
                                                                                 QgsWkbTypes.Point,
                                                                                 context,
                                                                                 self.POINTFLAGS
        )
        (self.lineFlagSink, self.line_flag_id) = self.prepareAndReturnFlagSink(parameters,
                                                                               drains,
                                                                               QgsWkbTypes.LineString,
                                                                               context,
                                                                               self.LINEFLAGS
        )
        (self.polygonFlagSink, self.polygon_flag_id) = self.prepareAndReturnFlagSink(parameters,
                                                                                     drains,
                                                                                     QgsWkbTypes.Polygon,
                                                                                     context,
                                                                                     self.POLYGONFLAGS)
        
        