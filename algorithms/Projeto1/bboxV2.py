list = []
project = QgsProject.instance()
for layer in project.mapLayers().values():
    rect = layer.extent()

    polygon_geom = QgsGeometry.fromPolygonXY([[QgsPointXY(rect.xMinimum(),  rect.yMinimum()),
                                                QgsPointXY(rect.xMinimum(), rect.yMaximum()),
                                                QgsPointXY(rect.xMaximum(), rect.yMaximum()),
                                                QgsPointXY(rect.xMaximum(), rect.yMinimum()),
                                                QgsPointXY(rect.xMinimum(), rect.yMinimum())]]
                                                )
    new_layer = QgsVectorLayer("Polygon",f"{layer.name()}_BBox",'memory')
    new_layer.setCrs(layer.crs())

    fields = QgsFields()
    fields.append(QgsField('raster',QVariant.String))

    provider = new_layer.dataProvider()
    provider.addAttributes(fields)

    nome = layer.name()
    feature = QgsFeature(new_layer.fields())
    feature.setGeometry(polygon_geom)
    feature.setAttributes([nome])
    provider.addFeature(feature)

    new_layer.updateFields()
    list.append(new_layer)