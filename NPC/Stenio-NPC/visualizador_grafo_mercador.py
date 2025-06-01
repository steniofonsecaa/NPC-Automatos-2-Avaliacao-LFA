# gerar_grafo_mercador_simplificado.py
from graphviz import Digraph
import os
import platform

# --- INÍCIO: Definição do SHOP_NPC_AUTOMATON ---
# COPIE A DEFINIÇÃO COMPLETA E MAIS ATUAL DO SEU SHOP_NPC_AUTOMATON AQUI
SHOP_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Olá, aventureiro! Produtos frescos e de qualidade! O que deseja?",
        "options": {"1": "Comprar Itens", "2": "Vender Itens", "3": "Tentar Ameaçar", "4": "Despedir-se"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "MENU_VENDA_ESCOLHER_ITEM", "3": "PROCESSAR_AMEACA", "4": "FIM_DIALOGO"}
    },
    "PROCESSAR_AMEACA": {"action_handler": "handle_ameaca", "message": "Você me ameaça?!", "options": {}, "transitions": {}},
    "FUGINDO": {"message": "SOCORRO! Um bandido! Fujam para as colinas!", "options": {"1": "[Continuar]"}, "transitions": {"1": "FIM_DIALOGO_NPC_AUSENTE"}},
    "AMEACA_FRACASSADA": {"message": "Hah! Acha que me intimida? Dê o fora da minha loja, seu verme!", "options": {"1": "[Sair da Loja]"}, "transitions": {"1": "FIM_DIALOGO"}},
    "MENU_COMPRA_CATEGORIAS": {
        "message": "O que te interessa hoje? Temos Poções e Equipamentos.",
        "options": {"1": "Poção", "2": "Espada", "3": "Voltar"}, # Texto da opção simplificado para o label da aresta
        "transitions": {"1": "DETALHES_ITEM_POCAO", "2": "DETALHES_ITEM_ESPADA", "3": "INICIAL"}
    },
    "DETALHES_ITEM_POCAO": {
        "item_key": "pocao", "message": "Uma {item_nome}, restaura vida. Custa {preco_base}g. E então?",
        "options": {"1": "Comprar", "2": "Negociar", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "NEGOCIANDO_PRECO_POCAO", "3": "MENU_COMPRA_CATEGORIAS"}
    },
    "DETALHES_ITEM_ESPADA": {
        "item_key": "espada", "message": "Uma {item_nome}, confiável. Custa {preco_base}g. Leva?",
        "options": {"1": "Comprar", "2": "Negociar", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_ESPADA_BASE", "2": "NEGOCIANDO_PRECO_ESPADA", "3": "MENU_COMPRA_CATEGORIAS"}
    },
    "NEGOCIANDO_PRECO_POCAO": {
        "item_key": "pocao", "message": "Negociar, é? Hmm... Sou todo ouvidos...",
        "options": {"1": "Insistir", "2": "Pagar Preço Normal", "3": "Cancelar"},
        "transitions": {"1": "PROCESSAR_PERSUASAO_POCAO", "2": "PROCESSAR_COMPRA_POCAO_BASE", "3": "DETALHES_ITEM_POCAO"}
    },
    "PROCESSAR_PERSUASAO_POCAO": {"item_key": "pocao", "action_handler": "handle_persuasao_desconto", "message": "Deixe-me pensar...", "options": {}, "transitions": {}},
    "DESCONTO_OFERECIDO_POCAO": {
        "item_key": "pocao", "message": "Sorte sua! {item_nome} por {preco_desconto}g. Aceita?",
        "options": {"1": "Aceitar Desconto", "2": "Recusar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_DESCONTO", "2": "DETALHES_ITEM_POCAO"}
    },
    "NEGOCIACAO_FALHOU_POCAO": {
        "item_key": "pocao", "message": "Desculpe. O preço da {item_nome} é {preco_base}g. Sem choro.",
        "options": {"1": "Pagar Preço Normal", "2": "Deixar pra lá"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "DETALHES_ITEM_POCAO"}
    },
    "PROCESSAR_COMPRA_POCAO_BASE":    {"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 10, "message": "Verificando...", "options": {}, "transitions": {}},
    "PROCESSAR_COMPRA_POCAO_DESCONTO":{"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 8,  "message": "Verificando...", "options": {}, "transitions": {}},
    "PROCESSAR_COMPRA_ESPADA_BASE":   {"action_handler": "handle_tentativa_compra", "item_key": "espada", "preco_final_compra_jogador": 50, "message": "Verificando...", "options": {}, "transitions": {}},
    "COMPRA_SUCESSO": {"message": "{item_nome} adicionado!", "options": {"1": "Continuar Comprando", "2": "Menu Principal"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "INICIAL"}},
    "SEM_OURO": {"message": "Sem ouro para {item_nome}.", "options": {"1": "Ok"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}},
    "RECUSANDO_VENDA_ALEATORIA": {"message": "Hoje não vendo {item_nome}!", "options": {"1": "Entendido"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}},
    "MENU_VENDA_ESCOLHER_ITEM": {
        "message": "Quer me vender algo?", "options_generator_handler": "generate_sell_options_for_player",
        "options": {"9": "Voltar"}, "transitions": {"9": "INICIAL"} 
    },
    "CONFIRMAR_VENDA_ITEM_GENERICO": {
        "message": "Vender {item_nome} por {preco_npc_paga}g?", "options": {"1": "Sim", "2": "Não"},
        "transitions": {"1": "PROCESSAR_VENDA_ITEM", "2": "MENU_VENDA_ESCOLHER_ITEM"}
    },
    "PROCESSAR_VENDA_ITEM": {"action_handler": "handle_tentativa_venda_jogador", "message": "Inspecionando...", "options": {}, "transitions": {}},
    "VENDA_SUCESSO": {"message": "{item_nome} vendido!", "options": {"1": "Vender Mais", "2": "Menu Principal"}, "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM", "2": "INICIAL"}},
    "VENDA_FALHOU_SEM_ITEM": {"message": "Você não tem mais {item_nome}.", "options": {"1": "Ok"}, "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}},
    "NPC_NAO_COMPRA_ITEM": {"message": "Não compro {item_nome}.", "options": {"1": "Ok"}, "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}},
    "FIM_DIALOGO": {"message": "Até mais!", "options": {}, "transitions": {}},
    "FIM_DIALOGO_NPC_AUSENTE": {"message": "(Mercador ausente)", "options": {}, "transitions": {}}
}
# --- FIM: Definição do SHOP_NPC_AUTOMATON ---


def gerar_grafo_mercador_estilo_imagem(automato_dict, nome_arquivo_saida='mercador_afd'):
    dot = Digraph(comment='AFD Mercador')
    dot.attr(rankdir='TD', labelloc='t', label='Autômato do Mercador', fontsize='18') # TD para Top-Down

    # Estados que serão desenhados com círculo duplo (simulando estados finais ou de conclusão de um fluxo)
    # Baseado no seu exemplo e no nosso autômato
    estados_estilo_final = [
        'FIM_DIALOGO', 'FIM_DIALOGO_NPC_AUSENTE', 'FUGINDO', 'AMEACA_FRACASSADA',
        'COMPRA_SUCESSO', 'SEM_OURO', 'RECUSANDO_VENDA_ALEATORIA',
        'VENDA_SUCESSO', 'VENDA_FALHOU_SEM_ITEM', 'NPC_NAO_COMPRA_ITEM'
    ]
    
    # Estados que são pontos de processamento (action handlers)
    estados_de_processamento = [estado for estado, info in automato_dict.items() if info.get("action_handler")]

    for estado_nome in automato_dict.keys():
        label_no = estado_nome # Apenas o nome do estado no nó
        formato_no = 'ellipse'
        cor_borda = 'black'

        if estado_nome in estados_estilo_final:
            formato_no = 'doublecircle'
        elif estado_nome in estados_de_processamento:
            formato_no = 'box' # Ou 'diamond' para destacar pontos de lógica interna

        dot.node(estado_nome, label=label_no, shape=formato_no, color=cor_borda)

    # Adicionando as transições definidas no autômato
    for nome_estado_origem, info_estado in automato_dict.items():
        opcoes = info_estado.get("options", {})
        transicoes_definidas = info_estado.get("transitions", {})
        
        for chave_opcao, texto_opcao_completo in opcoes.items():
            if chave_opcao in transicoes_definidas:
                nome_estado_destino = transicoes_definidas[chave_opcao]
                # Usar o texto da opção como label, simplificado para ser mais curto
                # Pega a primeira palavra ou as duas primeiras se forem curtas, ou um placeholder
                palavras_opcao = texto_opcao_completo.replace("[", "").replace("]", "").split(" ")
                if palavras_opcao:
                    if len(palavras_opcao) > 1 and len(palavras_opcao[0]) < 5:
                        label_transicao = f"{palavras_opcao[0]} {palavras_opcao[1]}"
                    else:
                        label_transicao = palavras_opcao[0]
                    if "Voltar" in texto_opcao_completo or "Sair" in texto_opcao_completo or "Cancelar" in texto_opcao_completo:
                        label_transicao = texto_opcao_completo # Mantém "Voltar", "Sair", "Cancelar"
                else:
                    label_transicao = chave_opcao # Fallback para a chave numérica

                # Remove parênteses de preços para ficar mais limpo
                if "(" in label_transicao:
                    label_transicao = label_transicao.split("(")[0].strip()

                dot.edge(nome_estado_origem, nome_estado_destino, label=label_transicao)
        
        # Transições de 'action_handler' (simuladas com base no conhecimento da lógica)
        # Estilo de label similar ao exemplo (ex: 'aceita', 'recusa')
        cor_aresta_handler = "black"
        estilo_aresta_handler = "dashed"

        if nome_estado_origem == "PROCESSAR_AMEACA":
            dot.edge(nome_estado_origem, "FUGINDO", label="foge (chance)", style=estilo_aresta_handler, color=cor_aresta_handler)
            dot.edge(nome_estado_origem, "AMEACA_FRACASSADA", label="resiste (chance)", style=estilo_aresta_handler, color=cor_aresta_handler)
        
        if nome_estado_origem == "PROCESSAR_PERSUASAO_POCAO": # Adicionar para outros itens se houver
            dot.edge(nome_estado_origem, "DESCONTO_OFERECIDO_POCAO", label="desconto OK (chance)", style=estilo_aresta_handler, color=cor_aresta_handler)
            dot.edge(nome_estado_origem, "NEGOCIACAO_FALHOU_POCAO", label="desconto negado (chance)", style=estilo_aresta_handler, color=cor_aresta_handler)

        # Para PROCESSAR_COMPRA_X
        if nome_estado_origem.startswith("PROCESSAR_COMPRA_"):
            dot.edge(nome_estado_origem, "COMPRA_SUCESSO", label="aceita compra", style=estilo_aresta_handler, color=cor_aresta_handler)
            dot.edge(nome_estado_origem, "SEM_OURO", label="sem ouro", style=estilo_aresta_handler, color=cor_aresta_handler)
            dot.edge(nome_estado_origem, "RECUSANDO_VENDA_ALEATORIA", label="recusa (chance)", style=estilo_aresta_handler, color=cor_aresta_handler)

        if nome_estado_origem == "PROCESSAR_VENDA_ITEM":
            dot.edge(nome_estado_origem, "VENDA_SUCESSO", label="aceita venda", style=estilo_aresta_handler, color=cor_aresta_handler)
            dot.edge(nome_estado_origem, "VENDA_FALHOU_SEM_ITEM", label="jogador sem item", style=estilo_aresta_handler, color=cor_aresta_handler)
            dot.edge(nome_estado_origem, "NPC_NAO_COMPRA_ITEM", label="não compra este item", style=estilo_aresta_handler, color=cor_aresta_handler)
            
        # Para MENU_VENDA_ESCOLHER_ITEM (opções dinâmicas)
        if nome_estado_origem == "MENU_VENDA_ESCOLHER_ITEM" and info_estado.get("options_generator_handler"):
            dot.edge(nome_estado_origem, "CONFIRMAR_VENDA_ITEM_GENERICO", label="Seleciona Item", style="dotted", color=cor_aresta_handler)


    try:
        dot.format = 'png'
        # Salva na pasta atual com o nome fornecido
        output_path = dot.render(filename=nome_arquivo_saida, directory='.', cleanup=True) 
        print(f"Diagrama '{output_path}' gerado com sucesso.")

        if platform.system() == 'Windows':
            os.startfile(output_path)
        elif platform.system() == 'Darwin':
            os.system(f'open "{output_path}"')
        else:
            os.system(f'xdg-open "{output_path}"')

    except Exception as e:
        print(f"Erro ao gerar ou abrir o diagrama: {e}")
        print("Verifique se o Graphviz está instalado e configurado no PATH do sistema.")
        print("Você pode copiar o código DOT gerado (se houver) e usar um visualizador online.")
        # print("\n--- CÓDIGO DOT GERADO PARA DEBUG ---")
        # print(dot.source) # Descomente para ver o código DOT no console se a renderização falhar
        # print("------------------------------------")


if __name__ == '__main__':
    # Certifique-se que SHOP_NPC_AUTOMATON está definido acima ou importado corretamente
    gerar_grafo_mercador_estilo_imagem(SHOP_NPC_AUTOMATON)