
VENDEDOR_NPC_AUTOMATO = {
    "INICIAL": {
        "message": "Olá, aventureiro! Produtos frescos e de qualidade! O que deseja?",
        "options": {"1": "Comprar Itens", "2": "Vender Itens", "3": "Tentar Ameaçar", "4": "Despedir-se"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "MENU_VENDA_ESCOLHER_ITEM", "3": "PROCESSAR_AMEACA", "4": "FIM_DIALOGO"}
    },


    "PROCESSAR_AMEACA": { "action_handler": "handle_ameaca", "message": "Você me ameaça?!", "options": {}, "transitions": {}},
    "FUGINDO": {"message": "SOCORRO! Um bandido! Fujam para as colinas!", "options": {"1": "[Continuar]"}, "transitions": {"1": "FIM_DIALOGO_NPC_AUSENTE"}},
    "AMEACA_FRACASSADA": {"message": "Hah! Acha que me intimida? Dê o fora da minha loja, seu verme!", "options": {"1": "[Sair da Loja]"}, "transitions": {"1": "FIM_DIALOGO"}},

    "MENU_COMPRA_CATEGORIAS": {
        "message": "O que te interessa hoje? Temos Poções e Equipamentos.",
        "options": { 
            "1": "Poção (10g)", 
            "2": "Espada (50g)", 
            "3": "Voltar ao Menu Principal"
        },
        "transitions": {"1": "DETALHES_ITEM_POCAO", "2": "DETALHES_ITEM_ESPADA", "3": "INICIAL"}
    },
    "DETALHES_ITEM_POCAO": {
        "item_key": "pocao",
        "message": "Uma {item_nome}, restaura vida. Custa {preco_base}g. E então?", 
        "options": {"1": "Comprar por {preco_base}g", "2": "Tentar Negociar Preço", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "NEGOCIANDO_PRECO_POCAO", "3": "MENU_COMPRA_CATEGORIAS"}
    },
    "DETALHES_ITEM_ESPADA": {
        "item_key": "espada",
        "message": "Uma {item_nome}, confiável. Custa {preco_base}g. Leva?", 
        "options": {"1": "Comprar por {preco_base}g", "2": "Tentar Negociar Preço", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_ESPADA_BASE", "2": "NEGOCIANDO_PRECO_ESPADA", "3": "MENU_COMPRA_CATEGORIAS"}
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
        "message": "Sorte sua! {item_nome} por {preco_desconto}g. Aceita?", 
        "options": {"1": "Sim, levar por {preco_desconto}g!", "2": "Não, obrigado"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_DESCONTO", "2": "DETALHES_ITEM_POCAO"}
    },
    "NEGOCIACAO_FALHOU_POCAO": {
        "item_key": "pocao",
        "message": "Desculpe. O preço da {item_nome} é {preco_base}g. Sem choro.", 
        "options": {"1": "Ok, pagar {preco_base}g", "2": "Deixar pra lá"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "DETALHES_ITEM_POCAO"}
    },
    "NEGOCIANDO_PRECO_ESPADA": {
        "item_key": "espada",
        "message": "Negociar o preço da {item_nome}, é? Sou todo ouvidos...",
        "options": {"1": "Insistir por um preço melhor (Persuadir)", "2": "Ok, pagar {preco_base}g", "3": "Cancelar Negociação"},
        "transitions": {"1": "PROCESSAR_PERSUASAO_ESPADA", "2": "PROCESSAR_COMPRA_ESPADA_BASE", "3": "DETALHES_ITEM_ESPADA"}
    },
    "PROCESSAR_PERSUASAO_ESPADA": {
        "item_key": "espada",
        "action_handler": "handle_persuasao_desconto",
        "message": "Deixe-me pensar sobre o preço desta {item_nome}...",
        "options": {},
        "transitions": {}
    },
    "DESCONTO_OFERECIDO_ESPADA": {
        "item_key": "espada",
        "message": "É seu dia de sorte! Consigo fazer a {item_nome} por {preco_desconto}g para você. Aceita?",
        "options": {"1": "Sim, levar por {preco_desconto}g!", "2": "Não, obrigado"},
        "transitions": {"1": "PROCESSAR_COMPRA_ESPADA_DESCONTO", "2": "DETALHES_ITEM_ESPADA"}
    },
    "NEGOCIACAO_FALHOU_ESPADA": {
        "item_key": "espada",
        "message": "Sinto muito. O preço da {item_nome} é {preco_base}g. Não posso baixar mais.",
        "options": {"1": "Ok, pagar {preco_base}g", "2": "Deixar pra lá"},
        "transitions": {"1": "PROCESSAR_COMPRA_ESPADA_BASE", "2": "DETALHES_ITEM_ESPADA"}
    },
    "PROCESSAR_COMPRA_POCAO_BASE":    {"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 10, "message": "Verificando seu ouro...", "options": {}, "transitions": {}},
    "PROCESSAR_COMPRA_POCAO_DESCONTO":{"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final_compra_jogador": 8,  "message": "Verificando seu ouro...", "options": {}, "transitions": {}}, 
    "PROCESSAR_COMPRA_ESPADA_BASE":   {"action_handler": "handle_tentativa_compra", "item_key": "espada", "preco_final_compra_jogador": 50, "message": "Verificando seu ouro...", "options": {}, "transitions": {}}, 

     "PROCESSAR_COMPRA_ESPADA_DESCONTO":{
        "action_handler": "handle_tentativa_compra", 
        "item_key": "espada",
        "preco_final_compra_jogador": 40, 
        "message": "Verificando seu ouro para a espada com desconto...",
        "options": {},
        "transitions": {} 
    },

    "COMPRA_SUCESSO": {"message": "{item_nome} adicionado à mochila!", "options": {"1": "[Continuar Comprando]", "2": "[Menu Principal]"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "INICIAL"}},
    "SEM_OURO": {"message": "Você não tem ouro suficiente para {item_nome}.", "options": {"1": "[Ok]"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}}, 
    "RECUSANDO_VENDA_ALEATORIA": {"message": "Hoje não estou vendendo {item_nome} para você!", "options": {"1": "[Entendido]"}, "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}},

    "MENU_VENDA_ESCOLHER_ITEM": {
        "message": "Quer me vender algo? O que você tem? (Mostrarei o que compro)",
        "options_generator_handler": "generate_sell_options_for_player", 
        "options": {"9": "[Voltar ao Menu Principal]"}, 
        "transitions": {"9": "INICIAL"} 
    },
    "CONFIRMAR_VENDA_ITEM_GENERICO": {
        "item_key": None, 
        "message": "Você tem {jogador_qtd} de {item_nome}. Eu pago {preco_npc_paga}g por cada. Vender um(a)?",
        "options": {"1": "Sim, vender um(a)", "2": "Não, cancelar venda"},
        "transitions": {"1": "PROCESSAR_VENDA_ITEM", "2": "MENU_VENDA_ESCOLHER_ITEM"}
    },
    "PROCESSAR_VENDA_ITEM": { 
        "action_handler": "handle_tentativa_venda_jogador",
        "item_key": None, 
        "preco_npc_paga": None,
        "message": "Deixe-me inspecionar isso...",
        "options": {},
        "transitions": {}
    },
    "VENDA_SUCESSO": {
        "message": "{item_nome} vendido! Você recebeu {preco_npc_paga}g.", 
        "options": {"1": "[Vender Mais Itens]", "2": "[Menu Principal]"},
        "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM", "2": "INICIAL"}
    },
    "VENDA_FALHOU_SEM_ITEM": { 
        "message": "Ué? Parece que você não tem mais {item_nome} para vender.",
        "options": {"1": "[Ok]"},
        "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}
    },
    "NPC_NAO_COMPRA_ITEM": { 
        "message": "Desculpe, não estou interessado em comprar {item_nome} no momento.",
        "options": {"1": "[Ok]"},
        "transitions": {"1": "MENU_VENDA_ESCOLHER_ITEM"}
    },

    "FIM_DIALOGO": {"message": "Até mais, aventureiro! E cuidado por ai.", "options": {}, "transitions": {}},
    "FIM_DIALOGO_NPC_AUSENTE": {"message": "(O mercador não está mais aqui...)", "options": {}, "transitions": {}}
}