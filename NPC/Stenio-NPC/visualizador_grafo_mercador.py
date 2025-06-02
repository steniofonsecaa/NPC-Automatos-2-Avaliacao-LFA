from graphviz import Digraph
import os
import platform

AFD_MERCADOR = {
    "INICIAL": {
        "message": "Olá, aventureiro! Produtos frescos e de qualidade! O que deseja?",
        "options": {"1": "Comprar Itens", "2": "Vender Itens", "3": "Tentar Ameaçar", "4": "Despedir-se"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "MENU_VENDA_ESCOLHER_ITEM", "3": "PROCESSAR_AMEACA", "4": "FIM_DIALOGO"}
    },
    "PROCESSAR_AMEACA": {"action_handler": "handle_ameaca", "message": "Você me ameaça?!", "options": {}, "transitions": {}}, # Será "pulado" no grafo
    "FUGINDO": {"message": "SOCORRO! Um bandido!", "options": {"1": "[Continuar]"}, "transitions": {"1": "FIM_DIALOGO_NPC_AUSENTE"}},
    "AMEACA_FRACASSADA": {"message": "Hah! Acha que me intimida?", "options": {"1": "[Sair da Loja]"}, "transitions": {"1": "FIM_DIALOGO"}},
    "MENU_COMPRA_CATEGORIAS": {
        "message": "O que te interessa hoje?",
        "options": {"1": "Poção", "2": "Espada", "3": "Voltar"},
        "transitions": {"1": "DETALHES_ITEM_POCAO", "2": "DETALHES_ITEM_ESPADA", "3": "INICIAL"}
    },
    "DETALHES_ITEM_POCAO": {
        "item_key": "pocao", "message": "Poção de Cura...",
        "options": {"1": "Comprar", "2": "Negociar", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "NEGOCIANDO_PRECO_POCAO", "3": "MENU_COMPRA_CATEGORIAS"}
    },
    "DETALHES_ITEM_ESPADA": {
        "item_key": "espada", "message": "Espada Curta...",
        "options": {"1": "Comprar", "2": "Negociar", "3": "Voltar"}, # Adicionar NEGOCIANDO_PRECO_ESPADA se existir
        "transitions": {"1": "PROCESSAR_COMPRA_ESPADA_BASE", "2": "NEGOCIANDO_PRECO_ESPADA", "3": "MENU_COMPRA_CATEGORIAS"}
    },
    "NEGOCIANDO_PRECO_POCAO": {
        "item_key": "pocao", "message": "Negociar, é?",
        "options": {"1": "Insistir", "2": "Pagar Normal", "3": "Cancelar"},
        "transitions": {"1": "PROCESSAR_PERSUASAO_POCAO", "2": "PROCESSAR_COMPRA_POCAO_BASE", "3": "DETALHES_ITEM_POCAO"}
    },
    "PROCESSAR_PERSUASAO_POCAO": {"item_key": "pocao", "action_handler": "handle_persuasao_desconto", "message": "Pensando...", "options": {}, "transitions": {}}, # Pulado
    "DESCONTO_OFERECIDO_POCAO": {
        "item_key": "pocao", "message": "Poção com desconto!",
        "options": {"1": "Aceitar Desconto", "2": "Recusar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_DESCONTO", "2": "DETALHES_ITEM_POCAO"}
    },
    "NEGOCIACAO_FALHOU_POCAO": {
        "item_key": "pocao", "message": "Preço firme.",
        "options": {"1": "Pagar Normal", "2": "Deixar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "DETALHES_ITEM_POCAO"}
    },
    "PROCESSAR_COMPRA_POCAO_BASE":    {"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 10, "message": "Verificando...", "options": {}, "transitions": {}}, # Pulado
    "PROCESSAR_COMPRA_POCAO_DESCONTO":{"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 8,  "message": "Verificando...", "options": {}, "transitions": {}}, # Pulado
    "PROCESSAR_COMPRA_ESPADA_BASE":   {"action_handler": "handle_tentativa_compra", "item_key": "espada", "preco_final_compra_jogador": 50, "message": "Verificando...", "options": {}, "transitions": {}}, # Pulado
    
    "COMPRA_SUCESSO": {"message": "Comprado!", "options": {"1": "Continuar", "2": "Menu Principal"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "INICIAL"}},
    "SEM_OURO": {"message": "Sem ouro.", "options": {"1": "Ok"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}},
    "RECUSANDO_VENDA_ALEATORIA": {"message": "Hoje não!", "options": {"1": "Entendido"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}},
    
    "MENU_VENDA_ESCOLHER_ITEM": {
        "message": "Vender algo?", "options_generator_handler": "generate_sell_options_for_player",
        "options": {"9": "Voltar"}, "transitions": {"9": "INICIAL"} 
    },
    "CONFIRMAR_VENDA_ITEM_GENERICO": {
        "message": "Vender {item_nome}?", "options": {"1": "Sim", "2": "Não"},
        "transitions": {"1": "PROCESSAR_VENDA_ITEM", "2": "MENU_VENDA_ESCOLHER_ITEM"}
    },
    "PROCESSAR_VENDA_ITEM": {"action_handler": "handle_tentativa_venda_jogador", "message": "Inspecionando...", "options": {}, "transitions": {}}, # Pulado
    
    "VENDA_SUCESSO": {"message": "Vendido!", "options": {"1": "Vender Mais", "2": "Menu Principal"}, "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM", "2": "INICIAL"}},
    "VENDA_FALHOU_SEM_ITEM": {"message": "Sem item.", "options": {"1": "Ok"}, "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}},
    "NPC_NAO_COMPRA_ITEM": {"message": "Não compro.", "options": {"1": "Ok"}, "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}},
    
    "FIM_DIALOGO": {"message": "Até mais!", "options": {}, "transitions": {}},
    "FIM_DIALOGO_NPC_AUSENTE": {"message": "Ausente", "options": {}, "transitions": {}}
}
# --- FIM: Definição do SHOP_NPC_AUTOMATON ---


# Mapeamento manual dos resultados dos action_handlers
# Chave: nome do estado de processamento (com action_handler)
# Valor: dicionário de {label_para_aresta_de_saida: estado_de_destino_real}
RESULTADOS_DOS_HANDLERS = {
    "PROCESSAR_AMEACA": {
        "NPC Foge (chance)": "FUGINDO",
        "Ameaça Falha (chance)": "AMEACA_FRACASSADA"
    },
    "PROCESSAR_PERSUASAO_POCAO": { # Adicionar para espada se tiver
        "Desconto Aceito (chance)": "DESCONTO_OFERECIDO_POCAO",
        "Desconto Negado (chance)": "NEGOCIACAO_FALHOU_POCAO"
    },
    # Para os PROCESSAR_COMPRA_X, o handler leva a 3 possíveis resultados
    # Vamos criar uma chave genérica e tratar no loop, ou listar todos
    "PROCESSAR_COMPRA_POCAO_BASE": { # Exemplo específico
        "Compra OK": "COMPRA_SUCESSO",
        "Sem Ouro": "SEM_OURO",
        "Recusa Aleatória": "RECUSANDO_VENDA_ALEATORIA"
    },
    "PROCESSAR_COMPRA_POCAO_DESCONTO": {
        "Compra OK": "COMPRA_SUCESSO",
        "Sem Ouro": "SEM_OURO",
        "Recusa Aleatória": "RECUSANDO_VENDA_ALEATORIA"
    },
    "PROCESSAR_COMPRA_ESPADA_BASE": { # Adicionar para espada com desconto
        "Compra OK": "COMPRA_SUCESSO",
        "Sem Ouro": "SEM_OURO",
        "Recusa Aleatória": "RECUSANDO_VENDA_ALEATORIA"
    },
    "PROCESSAR_VENDA_ITEM": {
        "Venda OK": "VENDA_SUCESSO",
        "Jogador Sem Item": "VENDA_FALHOU_SEM_ITEM",
        "NPC Não Compra": "NPC_NAO_COMPRA_ITEM"
    }
}


def gerar_grafo_mercador_ultra_simplificado(automato_dict, nome_arquivo_saida='mercador_afd'):
    dot = Digraph(comment='AFD Mercador')
    dot.attr(rankdir='TD', label='Autômato do Mercador', fontsize='18', concentrate='true')

    estados_de_processamento = [estado for estado, info in automato_dict.items() if info.get("action_handler")]
    
    # Estados que efetivamente terminam o diálogo ou um fluxo importante
    estados_finais_visuais = [
        'FIM_DIALOGO', 'FIM_DIALOGO_NPC_AUSENTE', 'FUGINDO', 'AMEACA_FRACASSADA',
        'COMPRA_SUCESSO', 'SEM_OURO', 'RECUSANDO_VENDA_ALEATORIA',
        'VENDA_SUCESSO', 'VENDA_FALHOU_SEM_ITEM', 'NPC_NAO_COMPRA_ITEM'
    ]

    # 1. Adicionar apenas nós que NÃO são de processamento puro
    for estado_nome, info_estado in automato_dict.items():
        if estado_nome not in estados_de_processamento:
            label_no = estado_nome
            formato_no = 'ellipse'
            if estado_nome in estados_finais_visuais: # Estiliza como "final" visualmente
                formato_no = 'doublecircle'
            elif estado_nome == 'INICIAL':
                 formato_no = 'ellipse' # Pode dar um estilo especial se quiser
            
            dot.node(estado_nome, label=label_no, shape=formato_no)

    # 2. Adicionar transições, pulando os estados de processamento
    for nome_estado_origem, info_estado_origem in automato_dict.items():
        # Não desenha transições partindo de estados de processamento (eles serão pulados)
        if nome_estado_origem in estados_de_processamento:
            continue

        opcoes = info_estado_origem.get("options", {})
        transicoes_definidas = info_estado_origem.get("transitions", {})

        # Transições normais (definidas por 'options' do jogador)
        for chave_opcao, texto_opcao_completo in opcoes.items():
            if chave_opcao in transicoes_definidas:
                destino_imediato = transicoes_definidas[chave_opcao]
                
                # Simplifica o label da aresta
                palavras_opcao = texto_opcao_completo.replace("[", "").replace("]", "").split(" ")
                label_aresta = palavras_opcao[0] if palavras_opcao else chave_opcao
                if len(palavras_opcao) > 1 and len(label_aresta) < 6 : label_aresta += " " + palavras_opcao[1]
                if "Voltar" in texto_opcao_completo or "Sair" in texto_opcao_completo or "Cancelar" in texto_opcao_completo:
                    label_aresta = texto_opcao_completo
                if "(" in label_aresta: label_aresta = label_aresta.split("(")[0].strip()


                if destino_imediato in estados_de_processamento:
                    # Se o destino é um estado de processamento, pega os resultados desse handler
                    if destino_imediato in RESULTADOS_DOS_HANDLERS:
                        for label_resultado, destino_final in RESULTADOS_DOS_HANDLERS[destino_imediato].items():
                            # Aresta do estado original para o resultado final do handler
                            # O label combina a escolha do jogador com o resultado do handler
                            dot.edge(nome_estado_origem, destino_final, label=f"{label_aresta}\n({label_resultado})", style="solid") # Solid, mas poderia ser dashed
                    else:
                        # Handler sem resultados mapeados, apenas ignora o estado de processamento (não ideal)
                        # Ou desenha uma aresta para ele se ele não for removido (mas queremos remover)
                        pass
                elif destino_imediato not in estados_de_processamento:
                    # Transição direta para um estado não-processamento
                    dot.edge(nome_estado_origem, destino_imediato, label=label_aresta, style="solid")
        
        # Lidar com options_generator_handler (MENU_VENDA_ESCOLHER_ITEM)
        if nome_estado_origem == "MENU_VENDA_ESCOLHER_ITEM" and info_estado_origem.get("options_generator_handler"):
            # Mostra uma transição genérica para o estado de confirmação
            # Este estado CONFIRMAR_VENDA_ITEM_GENERICO não é de processamento, então será um nó.
            dot.edge(nome_estado_origem, "CONFIRMAR_VENDA_ITEM_GENERICO", label="Seleciona Item P/ Venda", style="solid")


    try:
        dot.format = 'png'
        output_path = dot.render(filename=nome_arquivo_saida, directory='.', cleanup=True)
        print(f"Diagrama '{output_path}' gerado com sucesso.")
        if platform.system() == 'Windows': os.startfile(output_path)
        elif platform.system() == 'Darwin': os.system(f'open "{output_path}"')
        else: os.system(f'xdg-open "{output_path}"')
    except Exception as e:
        print(f"Erro ao gerar ou abrir o diagrama: {e}")
       
if __name__ == '__main__':
    gerar_grafo_mercador_ultra_simplificado(AFD_MERCADOR)