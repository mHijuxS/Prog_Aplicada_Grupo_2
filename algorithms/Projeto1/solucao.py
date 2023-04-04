# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupoX
                                 A QGIS plugin
 Solução do Grupo 2
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-20
        copyright            : (C) 2023 by Grupo 2
        email                : borba.philipe@ime.eb.br
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
__date__ = '2023-03-20'
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
                       QgsProcessingUtils,
                       QgsVectorLayer,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
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


class Projeto1Solucao(QgsProcessingAlgorithm):

    """
    Definindo as constantes
    """

    INPUT_CSV = 'INPUT_CSV'
    INPUT_RASTER = 'INPUT_RASTER'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def tr(self, string):
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return Projeto1Solucao()

    def name(self):
        return 'Solução do Projeto 1'

    def displayName(self):
        return self.tr(self.name())

    def group(self):        
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 1'
        
    def shortHelpString(self):
        return self.tr("""Esse algoritmo tem como objetivo determinar a acurácia 
                          absoluta de 6 modelos de superfície. Criando uma camada 
                          temporária com atributo erro, o qual contém o vlaor de 
                          e_z. Além disso, as camadas são carregadas de modo que 
                          sua simbologia permita analisar espacialmente a distri-
                          buição dos erros """
                       )
    
    
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT_CSV,
            'Input CSV file',
            extension='csv'
        ))         
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT_RASTER,
            'Input raster layer',
        ))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_LAYER,
            'Output layer',
            type=QgsProcessing.TypeVectorPoint
        ))


    """
    Função que muda a simbologia da camada baseada no valor do erro 
    """
    def apply_error_based_size(self, layer, error_field_index, scale_factor=1.0):
        symbol = QgsMarkerSymbol.createSimple({})
        renderer = QgsCategorizedSymbolRenderer('{}'.format(layer.fields()[error_field_index].name()), [])

        for feature in layer.getFeatures():
            error_value = feature.attributes()[error_field_index]
            symbol.setSize(error_value * scale_factor)
            category = QgsRendererCategory(error_value, symbol.clone(), str(error_value))
            renderer.addCategory(category)

        layer.setRenderer(renderer)
        layer.triggerRepaint()
      
    def processAlgorithm(self, parameters, context, feedback):
        # Pegando os parametros de input
        input_csv = self.parameterAsString(parameters, self.INPUT_CSV, context)
        input_raster = self.parameterAsRasterLayer(parameters,self.INPUT_RASTER, context)

        # Convertendo o CSV para um shapefile
        df = pd.read_csv(input_csv)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y, df.z))
        gdf.to_file('pontos_de_controle.shp', driver='ESRI Shapefile')

        # Carregar o shapefile no Qgis
        layer_points_control = QgsVectorLayer('pontos_de_controle.shp', 'points', 'ogr')
        if not layer_points_control.isValid():
            raise Exception('Failed to load input layer')

        # Pegar as coordenadas de referencia das camadas
        raster_crs = input_raster.crs()
        point_crs = layer_points_control.crs()

        # Criar uma nova camada do tipo ponto com a mesma CRS da camada raster
        fields = QgsFields()
        fields.append(QgsField('x', QVariant.Double))
        fields.append(QgsField('y', QVariant.Double))
        fields.append(QgsField('erro', QVariant.Double))
        (sink,dest_id) = self.parameterAsSink(
                            parameters, 
                            self.OUTPUT_LAYER, 
                            context,
                            fields,
                            QgsWkbTypes.Point,
                            raster_crs
        )

        provider = input_raster.dataProvider()
        
        
        EMQ = 0
        counter = 0
        

        # percorre todas as feições da camada de pontos de controle e calcula o valor do raster nos pontos (x,y) do ponto de controle e calcula o erro entre o z da camada do ponto de controle
        for feat in layer_points_control.getFeatures():
            if input_raster.extent().contains(feat.geometry().boundingBox()):
                geom = feat.geometry()
                x, y = geom.asPoint()
                point = QgsPointXY(x,y)
                pixel_value = provider.identify(point, QgsRaster.IdentifyFormatValue).results()[1]
                z = feat.attributes()[2]
                erro = abs(z - pixel_value)
                new_feat = QgsFeature()
                new_feat.setGeometry(QgsGeometry.fromPointXY(point))
                new_feat.setAttributes([x, y, erro])
                sink.addFeature(new_feat)
                EMQ = EMQ + erro**2
                counter = counter + 1
        EMQ = (EMQ/counter)**1/2
        
        feedback.pushInfo(f"EMQ = {EMQ}")

        A_EP = 1.67
        B_EP = 3.33
        C_EP = 4.0
        D_EP = 5.0

        if (EMQ < A_EP):
            feedback.pushInfo("A classe é a A")

        elif (A_EP < EMQ < B_EP):
            feedback.pushInfo("A classe é a B")
            
        elif (B_EP <EMQ < C_EP):
            feedback.pushInfo("A classe é a C")

        elif (C_EP < EMQ < D_EP):
            feedback.pushInfo("A classe é a D")

        else:
            feedback.pushInfo("Não conforme")
            
        
        """
        Define o estilo da camada de saida
        """
       
        # Aplicar tamanho baseado no valor do erro na camada de saída
        error_field_index = 2  # A coluna do erro é a segunda coluna (índice 2)
        scale_factor = 1.0
        output_layer = QgsProcessingUtils.mapLayerFromString(dest_id, context)
        self.apply_error_based_size(output_layer, error_field_index, scale_factor)

        return {self.OUTPUT_LAYER: dest_id}
    

 