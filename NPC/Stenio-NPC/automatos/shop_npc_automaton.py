
SHOP_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Olá, aventureiro! Produtos frescos e de qualidade! O que deseja?",
        "options": {"1": "Comprar Itens", "2": "Vender Itens", "3": "Tentar Ameaçar", "4": "Despedir-se"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "MENU_VENDA_ESCOLHER_ITEM", "3": "PROCESSAR_AMEACA", "4": "FIM_DIALOGO"} # Mudou para MENU_VENDA_ESCOLHER_ITEM
    },

    # --- FLUXO DE AMEAÇA (como antes) ---
    "PROCESSAR_AMEACA": { "action_handler": "handle_ameaca", "message": "Você me ameaça?!", "options": {}, "transitions": {}},
    "FUGINDO": {"message": "SOCORRO! Um bandido! Fujam para as colinas!", "options": {"1": "[Continuar]"}, "transitions": {"1": "FIM_DIALOGO_NPC_AUSENTE"}},
    "AMEACA_FRACASSADA": {"message": "Hah! Acha que me intimida? Dê o fora da minha loja, seu verme!", "options": {"1": "[Sair da Loja]"}, "transitions": {"1": "FIM_DIALOGO"}},

    # --- FLUXO DE COMPRA (como antes, mas referenciando ITEM_DATA para preços) ---
    "MENU_COMPRA_CATEGORIAS": {
        "message": "O que te interessa hoje? Temos Poções e Equipamentos.",
        "options": { # As mensagens das opções serão formatadas pelo NPC para incluir preços de ITEM_DATA
            "1": "Poção ({preco_base_pocao}g)", 
            "2": "Espada ({preco_base_espada}g)", 
            "3": "Voltar ao Menu Principal"
        },
        "transitions": {"1": "DETALHES_ITEM_POCAO", "2": "DETALHES_ITEM_ESPADA", "3": "INICIAL"}
    },
    "DETALHES_ITEM_POCAO": {
        "item_key": "pocao",
        "message": "Uma {item_nome}, restaura vida. Custa {preco_base}g. E então?", # Será formatada
        "options": {"1": "Comprar por {preco_base}g", "2": "Tentar Negociar Preço", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "NEGOCIANDO_PRECO_POCAO", "3": "MENU_COMPRA_CATEGORIAS"}
    },
    "DETALHES_ITEM_ESPADA": {
        "item_key": "espada",
        "message": "Uma {item_nome}, confiável. Custa {preco_base}g. Leva?", # Será formatada
        "options": {"1": "Comprar por {preco_base}g", "2": "Tentar Negociar Preço", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_ESPADA_BASE", "2": "NEGOCIANDO_PRECO_ESPADA", "3": "MENU_COMPRA_CATEGORIAS"} # Adicionar NEGOCIANDO_PRECO_ESPADA se quiser
    },
    "NEGOCIANDO_PRECO_POCAO": {
        "item_key": "pocao",
        "message": "Negociar, é? Hmm... Sou todo ouvidos...",
        "options": {"1": "Insistir (Persuadir)", "2": "Pagar {preco_base}g", "3": "Cancelar"},
        "transitions": {"1": "PROCESSAR_PERSUASAO_POCAO", "2": "PROCESSAR_COMPRA_POCAO_BASE", "3": "DETALHES_ITEM_POCAO"}
    },
    "PROCESSAR_PERSUASAO_POCAO": {"item_key": "pocao", "action_handler": "handle_persuasao_desconto", "message": "Deixe-me pensar...", "options": {}, "transitions": {}},
    "DESCONTO_OFERECIDO_POCAO": {
        "item_key": "pocao",
        "message": "Sorte sua! {item_nome} por {preco_desconto}g. Aceita?", # Formatada
        "options": {"1": "Sim, levar por {preco_desconto}g!", "2": "Não, obrigado"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_DESCONTO", "2": "DETALHES_ITEM_POCAO"}
    },
    "NEGOCIACAO_FALHOU_POCAO": {
        "item_key": "pocao",
        "message": "Desculpe. O preço da {item_nome} é {preco_base}g. Sem choro.", # Formatada
        "options": {"1": "Ok, pagar {preco_base}g", "2": "Deixar pra lá"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "DETALHES_ITEM_POCAO"}
    },
    "PROCESSAR_COMPRA_POCAO_BASE":    {"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 10, "message": "Verificando seu ouro...", "options": {}, "transitions": {}}, # Usar preco de ITEM_DATA
    "PROCESSAR_COMPRA_POCAO_DESCONTO":{"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 8,  "message": "Verificando seu ouro...", "options": {}, "transitions": {}}, # Usar preco de ITEM_DATA
    "PROCESSAR_COMPRA_ESPADA_BASE":   {"action_handler": "handle_tentativa_compra", "item_key": "espada", "preco_final_compra_jogador": 50, "message": "Verificando seu ouro...", "options": {}, "transitions": {}}, # Usar preco de ITEM_DATA
    # (Adicionar PROCESSAR_COMPRA_ESPADA_DESCONTO e estados de negociação para espada se desejar)

    "COMPRA_SUCESSO": {"message": "{item_nome} adicionado à mochila!", "options": {"1": "[Continuar Comprando]", "2": "[Menu Principal]"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "INICIAL"}},
    "SEM_OURO": {"message": "Você não tem ouro suficiente para {item_nome}.", "options": {"1": "[Ok]"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}}, # Poderia voltar para DETALHES_ITEM_X
    "RECUSANDO_VENDA_ALEATORIA": {"message": "Hoje não estou vendendo {item_nome} para você!", "options": {"1": "[Entendido]"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}},

    # --- INÍCIO DO FLUXO DE VENDA ---
    "MENU_VENDA_ESCOLHER_ITEM": {
        "message": "Quer me vender algo? O que você tem? (Mostrarei o que compro)",
        # As opções aqui serão geradas dinamicamente pela classe NPC
        # com base no inventário do jogador e nos itens que o NPC compra.
        # As transições mapearão para "CONFIRMAR_VENDA_ITEM_GENERICO".
        "options_generator_handler": "generate_sell_options_for_player", # Novo tipo de handler
        "options": {"9": "[Voltar ao Menu Principal]"}, # Opção fixa de voltar
        "transitions": {"9": "INICIAL"} 
        # As transições para os itens (ex: "1", "2") serão adicionadas dinamicamente
        # ou interpretadas pelo process_player_choice junto com o contexto do options_generator.
    },
    "CONFIRMAR_VENDA_ITEM_GENERICO": { # Estado genérico após selecionar um item para vender
        "item_key": None, # Será preenchido dinamicamente pelo NPC com o item selecionado
        "message": "Você tem {jogador_qtd} de {item_nome}. Eu pago {preco_npc_paga}g por cada. Vender um(a)?", # Formatada pelo NPC
        "options": {"1": "Sim, vender um(a)", "2": "Não, cancelar venda"},
        "transitions": {"1": "PROCESSAR_VENDA_ITEM", "2": "MENU_VENDA_ESCOLHER_ITEM"}
    },
    "PROCESSAR_VENDA_ITEM": { # Estado intermediário para lógica de venda
        "action_handler": "handle_tentativa_venda_jogador", # Novo handler
        "item_key": None, # Preenchido dinamicamente
        "preco_npc_paga": None, # Preenchido dinamicamente
        "message": "Deixe-me inspecionar isso...",
        "options": {},
        "transitions": {} # Próximo estado (VENDA_SUCESSO ou VENDA_FALHOU) é definido pelo handler
    },
    "VENDA_SUCESSO": {
        "message": "{item_nome} vendido! Você recebeu {preco_npc_paga}g.", # Formatada pelo NPC/handler
        "options": {"1": "[Vender Mais Itens]", "2": "[Menu Principal]"},
        "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM", "2": "INICIAL"}
    },
    "VENDA_FALHOU_SEM_ITEM": { # Se o jogador não tiver mais o item (não deveria acontecer se opções são dinâmicas)
        "message": "Ué? Parece que você não tem mais {item_nome} para vender.",
        "options": {"1": "[Ok]"},
        "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}
    },
    "NPC_NAO_COMPRA_ITEM": { # Se, por algum motivo, o item selecionado não é comprável
        "message": "Desculpe, não estou interessado em comprar {item_nome} no momento.",
        "options": {"1": "[Ok]"},
        "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}
    },
    # --- FIM DO FLUXO DE VENDA ---

    "FIM_DIALOGO": {"message": "Até mais, aventureiro! E cuidado por ai.", "options": {}, "transitions": {}},
    "FIM_DIALOGO_NPC_AUSENTE": {"message": "(O mercador não está mais aqui...)", "options": {}, "transitions": {}}
}