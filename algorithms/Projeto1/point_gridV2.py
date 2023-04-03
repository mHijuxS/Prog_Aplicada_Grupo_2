result = []
for layer in list3:
    extent = layer.extent()

    resultado = processing.run("native:creategrid", {'TYPE':0,
    'EXTENT':extent,
    'HSPACING':200,
    'VSPACING':200,
    'HOVERLAY':0,
    'VOVERLAY':0,
    'CRS':QgsCoordinateReferenceSystem('EPSG:31982'),
    'OUTPUT':'TEMPORARY_OUTPUT'})

    result.append(resultado['OUTPUT'])