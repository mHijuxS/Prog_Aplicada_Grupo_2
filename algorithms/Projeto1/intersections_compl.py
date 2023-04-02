list2 = list.copy()
list3 = []
project = QgsProject().instance()
for layer1 in list:
    list2.remove(layer1)
    for layer2 in list2:
        result = processing.run("qgis:intersection", {
        'INPUT': layer1,
        'OVERLAY': layer2,
        'OUTPUT': 'memory:'
       })
        intersect_layer = result['OUTPUT']
        if not intersect_layer.featureCount()==0:
            list3.append(intersect_layer)

#for layer in list3:
#    project.addMapLayer(layer)