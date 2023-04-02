layer = iface.activeLayer()

# Definir qual nome do atributo utilizar e o numero de classes
field_name = 'erro'
num_classes = 5

# Pegar os valores unicos do campo de atributo
unique_values = set(feature[field_name] for feature in layer.getFeatures())

# Determina o tamanho do valor do range para cada classe
value_range = (max(unique_values) - min(unique_values)) / num_classes

# Definir os ranges e os simbolos para cada classe
ranges_list = []
symbol_min_size = 1
symbol_max_size = 5
for i in range(num_classes):
    range_min = min(unique_values) + i * value_range
    range_max = range_min + value_range
    symbol_size = symbol_min_size + (symbol_max_size - symbol_min_size) * (i / (num_classes - 1))
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    symbol.setSize(symbol_size)
    range_label = '{:.2f} - {:.2f}'.format(range_min, range_max)
    renderer_range = QgsRendererRange(range_min, range_max, symbol, range_label)
    ranges_list.append(renderer_range)

# Cria o renderizador de simbolos graduados
renderer = QgsGraduatedSymbolRenderer(field_name, ranges_list)
renderer.setClassAttribute(field_name)

# Aplica a renderização para a camada e atualiza o mapa
layer.setRenderer(renderer)
layer.triggerRepaint()
