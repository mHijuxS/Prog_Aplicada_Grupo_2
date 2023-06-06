from qgis.core import QgsProject

def create_error_points_layer():
    error_layer = QgsVectorLayer("Point", "error_points", "memory")
    pr = error_layer.dataProvider()

    # Adiciona o campo de descrição do erro
    pr.addAttributes([QgsField("Erro", QVariant.String)])

    error_layer.updateFields() 
    return error_layer, pr

def find_features_with_same_name(layer):
    name_to_feature = {}
    for feature in layer.getFeatures():
        if feature['nome'] not in name_to_feature:
            name_to_feature[feature['nome']] = []
        name_to_feature[feature['nome']].append(feature)
    return name_to_feature

def find_discontinuous_features(layer, buffer_layer, tolerance, error_layer_provider):
    name_to_feature = find_features_with_same_name(layer)
    errors = set()

    for buffer_feature in buffer_layer.getFeatures():
        buffer_geom = buffer_feature.geometry()

        for name, features in name_to_feature.items():
            if len(features) > 1:
                for i in range(len(features)):
                    end_point_1 = features[i].geometry().asMultiPolyline()[-1][-1]
                    for j in range(i + 1, len(features)):
                        start_point_2 = features[j].geometry().asMultiPolyline()[0][0]
                        if buffer_geom.contains(end_point_1) and buffer_geom.contains(start_point_2):
                            if end_point_1.distance(start_point_2) <= tolerance:
                                error_pair = tuple(sorted([features[i].id(), features[j].id()]))
                                errors.add(error_pair)
                                
                                # Calcula o ponto médio
                                midpoint = QgsPointXY((end_point_1.x() + start_point_2.x()) / 2, (end_point_1.y() + start_point_2.y()) / 2)
                                
                                # Cria uma nova feição de erro
                                error_feature = QgsFeature()
                                error_feature.setGeometry(QgsGeometry.fromPointXY(midpoint))
                                error_feature.setAttributes(["Erro de geometria desconectada"])
                                
                                # Adiciona a feição à camada de erros
                                error_layer_provider.addFeature(error_feature)

    return errors


def find_features_with_different_names(layer, buffer_layer, error_layer_provider):
    errors = set()
    
    for buffer_feature in buffer_layer.getFeatures():
        buffer_geom = buffer_feature.geometry()

        features = [feature for feature in layer.getFeatures()]
        for i in range(len(features) - 1):
            end_point_1 = features[i].geometry().asMultiPolyline()[-1][-1]
            start_point_2 = features[i+1].geometry().asMultiPolyline()[0][0]
            
            if buffer_geom.contains(end_point_1) and buffer_geom.contains(start_point_2):
                if features[i]['name'] != features[i+1]['name']:
                    error_pair = tuple(sorted([features[i].id(), features[i+1].id()]))
                    errors.add(error_pair)
                    
                    # Cria uma nova feição de erro
                    error_feature = QgsFeature()
                    error_feature.setGeometry(QgsGeometry.fromPointXY(end_point_1))
                    error_feature.setAttributes(["Erro de geometrias conectadas com conjuntos de atributos distintos."])

                    # Adiciona a feição à camada de erros
                    error_layer_provider.addFeature(error_feature)
    return errors


def create_buffer_layer(moldura_layer, buffer_distance):
    buffer_layer = QgsVectorLayer("Polygon", "buffer_layer", "memory")
    pr = buffer_layer.dataProvider()

    for moldura_feature in moldura_layer.getFeatures():
        moldura_geom = moldura_feature.geometry()

        # Desconstruir a geometria do polígono em linhas individuais
        for ring in moldura_geom.asMultiPolygon():
            for line in ring:
                line_geom = QgsGeometry.fromPolylineXY(line)

                # Cria um buffer em torno da linha
                buffer_geom = line_geom.buffer(buffer_distance, 5)

                # Cria e adiciona a feição de buffer
                buffer_feature = QgsFeature()
                buffer_feature.setGeometry(buffer_geom)
                pr.addFeature(buffer_feature)

    buffer_layer.updateExtents() 
    return buffer_layer




project = QgsProject.instance()
moldura_layer = project.mapLayersByName('VE4-Ligacao — aux_moldura_a')[0]
linhas_layer = project.mapLayersByName('VE4-Ligacao — infra_elemento_energia_l')[0]

tolerance = 0.0001  # Ajuste esse valor conforme necessário
buffer_distance = 0.00002  # Distância do buffer em metros
buffer_layer = create_buffer_layer(moldura_layer, buffer_distance)

# Cria a camada de pontos de erro
error_points_layer, error_points_provider = create_error_points_layer()

print("Verificando linhas com atributos iguais e que não são contínuas espacialmente...")
errors = find_discontinuous_features(linhas_layer, buffer_layer, tolerance, error_points_provider)
for error_pair in errors:
    print(f"Erro encontrado: IDs - {error_pair[0]} e {error_pair[1]}")

print("Verificando linhas com nomes diferentes e que são contínuas...")
errors = find_features_with_different_names(linhas_layer, buffer_layer,error_points_provider)
for error_pair in errors:
    print(f"Erro encontrado: IDs - {error_pair[0]} e {error_pair[1]}")

project = QgsProject.instance()
error_points_layer.updateExtents()
project.addMapLayer(error_points_layer)

