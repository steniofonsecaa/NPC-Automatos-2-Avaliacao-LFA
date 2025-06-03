
from graphviz import Digraph
import importlib
import os
import platform

# Lista dos NPCs (nomes dos arquivos sem .py)
npcs = ['NpcMercante', 'NpcFerreiro', 'NpcInformante']  # Atualize com seus NPCs

for npc_nome in npcs:
    try:
        npc = importlib.import_module(npc_nome)
        estados = npc.estados
        nome_npc = getattr(npc, 'nome', npc_nome)

        dot = Digraph(comment=f'AFD/AFN/AP {nome_npc}')
        for estado in estados:
            shape = 'ellipse'
            if estado.lower() in ['concluindo', 'encerrado', 'fugindo', 'recusandovenda', 'sucessoforja', 'falhaforja','sair','concluindovenda']:
                shape = 'doublecircle'
            dot.node(estado, shape=shape)

        transicoes = npc.transicoes

        if npc_nome.lower() == 'npcinformante':
            # 💡 É o AP do Informante
            for (origem, entrada), destinos in transicoes.items():
                for destino in destinos:
                    dot.edge(origem, destino, label=f"{entrada} / push(pop)")
        elif isinstance(transicoes, list):
            # AFD clássico
            for origem, destino, rotulo in transicoes:
                dot.edge(origem, destino, label=rotulo)
        elif isinstance(transicoes, dict):
            # AFN simples (Mercante / Ferreiro)
            for (origem, entrada), destinos in transicoes.items():
                for destino in destinos:
                    dot.edge(origem, destino, label=entrada)
        else:
            print(f"❌ Transições não reconhecidas para {nome_npc}")

        # Salvar e abrir
        arquivo_saida = f'{nome_npc.lower()}_automato'
        dot.format = 'png'
        output_path = dot.render(arquivo_saida, cleanup=True)

        if platform.system() == 'Windows':
            os.startfile(output_path)
        elif platform.system() == 'Darwin':
            os.system(f'open {output_path}')
        else:
            os.system(f'xdg-open {output_path}')

        print(f"✅ Diagrama do NPC {nome_npc} gerado: {output_path}")

    except Exception as e:
        print(f"❌ Erro ao processar {npc_nome}: {e}")