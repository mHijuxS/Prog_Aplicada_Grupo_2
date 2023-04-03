layer_cnt = 0
for intersect in list3:
    new_field = QgsField('Eqz',QVariant.Double)
    intersect_provider = intersect.dataProvider()
    intersect_provider.addAttributes([new_field])
    intersect.updateFields()
    erro = 0
    counter = 0
    layer_cnt = layer_cnt + 1
    intersect.startEditing()
    for feat in intersect.getFeatures():
        raster1 = project.mapLayersByName(feat.attributes()[0])[0]
        raster2 = project.mapLayersByName(feat.attributes()[1])[0]
        provider1 = raster1.dataProvider()
        provider2 = raster2.dataProvider()
        for layer_point in result:
            for point_feat in layer_point.getFeatures():
                if intersect.extent().contains(point_feat.geometry().boundingBox()):
                    geom = point_feat.geometry()
                    x,y = geom.asPoint()
                    point = QgsPointXY(x,y)
                    pixel_value1 = provider1.identify(point,QgsRaster.IdentifyFormatValue).results()[1]
                    pixel_value2 = provider2.identify(point,QgsRaster.IdentifyFormatValue).results()[1]
                    erro = abs(pixel_value1 - pixel_value2)
                    erro = erro + erro**2
                    counter = counter + 1
        EMQz = (erro/counter)**1/2
        feat[2] = EMQz
        intersect.updateFeature(feat)
    intersect.commitChanges()
    temp = intersect
    
    temp.setName(f"{feat.attributes()[0]}_{feat.attributes()[1]}")
    project.addMapLayer(temp)