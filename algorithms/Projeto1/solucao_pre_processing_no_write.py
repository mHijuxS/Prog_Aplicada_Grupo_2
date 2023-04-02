import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from qgis.core import (QgsVectorLayer,
                        QgsCoordinateReferenceSystem,
                        QgsVectorFileWriter,
                        QgsCoordinateTransform,
                        QgsField,
                        QgsWkbTypes, 
                        QgsPointXY, 
                        QgsGeometry, 
                        QgsProject
                        )
                      
#Convert CSV to Shapefile
df = pd.read_csv('C:/Users/Mathe/OneDrive/Área de Trabalho/Home/Work/IME/Programação Aplicada/Dados_Classroom_Projeto1/pontos_controle.csv')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y, df.z))
gdf.to_file('pontos_de_controle.shp', driver='ESRI Shapefile')

#Load Shapefile into QGIS
layer_points_control = QgsVectorLayer('pontos_de_controle.shp', 'points', 'ogr')

# Get the selected raster layer
raster_layer = iface.activeLayer()

# Get the coordinate systems of the layers
raster_crs = raster_layer.crs()
point_crs = layer_points_control.crs()

# Create a new point layer with the same CRS as the point layer
fields = QgsFields()
fields.append(QgsField('x', QVariant.Double))
fields.append(QgsField('y', QVariant.Double))
fields.append(QgsField('erro', QVariant.Double))

point_layer = QgsVectorLayer('Point?crs='+ point_crs.authid(), 'nova_camada', 'memory')
point_layer_provider = point_layer.dataProvider()
point_layer_provider.addAttributes(fields)
point_layer.updateFields()

# get the data provider for the layer
provider = raster_layer.dataProvider()

# Write the filtered points to the new layer
for feat in layer_points_control.getFeatures():
    if raster_layer.extent().contains(feat.geometry().boundingBox()):
        geom = feat.geometry()
        x, y = geom.asPoint()
        point = QgsPointXY(x,y)
        provider = raster_layer.dataProvider()
        pixel_value = provider.identify(point, QgsRaster.IdentifyFormatValue).results()[1]
        z = feat.attributes()[2]
        erro = abs(z - pixel_value)
        new_feat = QgsFeature()
        new_feat.setGeometry(geom)
        new_feat.setAttributes([x, y, erro])
        point_layer_provider.addFeature(new_feat)


QgsProject.instance().addMapLayer(point_layer)
