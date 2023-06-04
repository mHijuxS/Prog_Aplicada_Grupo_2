layer_1 = QgsProject.instance().mapLayersByName('VE4-Ligacao — elemnat_curva_nivel_l')[0]
layer_2 = QgsProject.instance().mapLayersByName('VE4-Ligacao — elemnat_trecho_drenagem_l')[0]
layer_3 = QgsProject.instance().mapLayersByName('VE4-Ligacao — infra_elemento_energia_l')[0]
layer_4 = QgsProject.instance().mapLayersByName('VE4-Ligacao — infra_via_deslocamento_l')[0]

layer_1_path = layer_1.source()
layer_2_path = layer_2.source()
layer_3_path = layer_3.source()
layer_4_path = layer_4.source()

layers_paths = [layer_1_path, layer_2_path, layer_3_path, layer_4_path]

bounding_layer = QgsProject.instance().mapLayersByName('VE4-Ligacao — aux_moldura_a')[0]

search_distance = 0.001  

if not bounding_layer.isValid(): 
    print("Camada de moldura não carregada!") 
    exit(1) 

# Criar uma camada de saída
crs = bounding_layer.crs().toWkt()
uri = "Point?crs=" + crs + "&field=id:integer&field=error_type:string"
error_layer = QgsVectorLayer(uri, "error_layer", "memory")
error_provider = error_layer.dataProvider()

# Loop sobre as camadas de linha
for path in layers_paths:
    line_layer = QgsVectorLayer(path, "line_layer", "ogr")
    if not line_layer.isValid(): 
        print("Camada de linha não carregada!") 
        continue
    
    # Crie uma indexação espacial
    index = QgsSpatialIndex()
    for ft in line_layer.getFeatures():
        index.insertFeature(ft)

    # Procure por erros de ligação
    for feature in line_layer.getFeatures():
        # Encontre todos os recursos que compartilham uma borda
        candidates = index.intersects(feature.geometry().boundingBox())
        for candidate_id in candidates:
            candidate_feature = line_layer.getFeature(candidate_id)

            # As bordas dos produtos que não são compartilhadas no conjunto de dados não devem ser verificadas
            if not candidate_feature.geometry().touches(feature.geometry()):
                print("Erro de ligação detectado entre o produto {} e o produto {}".format(feature['ID'], candidate_feature['ID']))

                # Adicione o ponto de erro à camada de erro
                error_feature = QgsFeature()
                error_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(feature.geometry().centroid().asPoint())))
                error_feature.setAttributes([feature['ID'], "Erro de ligação"])
                error_provider.addFeature(error_feature)

QgsProject.instance().addMapLayer(error_layer)