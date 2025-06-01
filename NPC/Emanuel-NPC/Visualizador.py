from graphviz import Digraph
import os
import platform

# Criando o objeto do diagrama
dot = Digraph(comment='AFD Mercador Ultra Complexo')

# Definindo os estados (nós)
estados = [
    'Esperando', 'ApresentandoItens', 'NegociandoPreco', 'OferecendoDesconto',
    'AceitandoTroca', 'RecusandoVenda', 'ConcluindoVenda', 'Fugindo', 'Encerrado'
]

for estado in estados:
    shape = 'ellipse'
    if estado in ['ConcluindoVenda', 'RecusandoVenda', 'Encerrado', 'Fugindo']:
        shape = 'doublecircle'  # Estados finais
    dot.node(estado, shape=shape)

# Definindo as transições (arestas)
transicoes = [
    ('Esperando', 'ApresentandoItens', 'comprar'),
    ('Esperando', 'Fugindo', 'ameaçar'),
    ('ApresentandoItens', 'NegociandoPreco', 'pressionar'),
    ('ApresentandoItens', 'AceitandoTroca', 'oferecer_troca'),
    ('ApresentandoItens', 'verificar_compra', 'pagar'),
    ('ApresentandoItens', 'Encerrado', 'sair'),
    ('NegociandoPreco', 'OferecendoDesconto', 'pressionar'),
    ('NegociandoPreco', 'verificar_compra', 'pagar'),
    ('NegociandoPreco', 'AceitandoTroca', 'oferecer_troca'),
    ('NegociandoPreco', 'Encerrado', 'sair'),
    ('OferecendoDesconto', 'verificar_compra', 'pagar'),
    ('OferecendoDesconto', 'Encerrado', 'sair'),
    ('AceitandoTroca', 'verificar_compra', 'pagar'),
    ('AceitandoTroca', 'Encerrado', 'sair'),
    ('RecusandoVenda', 'Encerrado', 'sair'),
    ('ConcluindoVenda', 'Encerrado', 'sair'),
    ('Fugindo', 'Encerrado', 'sair')
]

# Adicionando as transições
for origem, destino, rotulo in transicoes:
    dot.edge(origem, destino, label=rotulo)

# Transições do verificador de compra (probabilidade)
dot.edge('verificar_compra', 'ConcluindoVenda', label='aceita')
dot.edge('verificar_compra', 'RecusandoVenda', label='recusa')

# Definindo o nome do arquivo
arquivo_saida = 'mercador_afd'

# Gerar o PNG
dot.format = 'png'
output_path = dot.render(arquivo_saida, cleanup=True)

# Abrir o arquivo no visualizador padrão do sistema
if platform.system() == 'Windows':
    os.startfile(output_path)
elif platform.system() == 'Darwin':  # macOS
    os.system(f'open {output_path}')
else:  # Linux
    os.system(f'xdg-open {output_path}')

print(f"Diagrama gerado e aberto: {output_path}")
