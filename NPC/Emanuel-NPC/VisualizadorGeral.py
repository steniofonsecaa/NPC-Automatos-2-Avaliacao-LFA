from graphviz import Digraph
import importlib
import os
import platform

# Lista dos NPCs (nomes dos arquivos sem .py)
npcs = ['NpcMercante', 'npc_guarda', 'npc_monstro']  # Adicione seus NPCs aqui

for npc_nome in npcs:
    # Importar o módulo do NPC dinamicamente
    try:
        npc = importlib.import_module(npc_nome)
        estados = npc.estados
        transicoes = npc.transicoes
        nome_npc = getattr(npc, 'nome', npc_nome)

        # Criar o diagrama
        dot = Digraph(comment=f'AFD {nome_npc}')
        for estado in estados:
            shape = 'ellipse'
            if estado.lower() in ['concluindo', 'encerrado', 'fugindo', 'recusandovenda']:
                shape = 'doublecircle'
            dot.node(estado, shape=shape)

        for origem, destino, rotulo in transicoes:
            dot.edge(origem, destino, label=rotulo)

        # Salvar e abrir
        arquivo_saida = f'{nome_npc.lower()}_afd'
        dot.format = 'png'
        output_path = dot.render(arquivo_saida, cleanup=True)

        # Abrir no visualizador padrão
        if platform.system() == 'Windows':
            os.startfile(output_path)
        elif platform.system() == 'Darwin':
            os.system(f'open {output_path}')
        else:
            os.system(f'xdg-open {output_path}')

        print(f"✅ Diagrama do NPC {nome_npc} gerado: {output_path}")

    except Exception as e:
        print(f"❌ Erro ao processar {npc_nome}: {e}")
