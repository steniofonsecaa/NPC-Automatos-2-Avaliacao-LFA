SHOP_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Olá, aventureiro! Produtos frescos e de qualidade! O que deseja?",
        "options": {"1": "Comprar Itens", "2": "Vender Itens", "3": "Tentar Ameaçar", "4": "Despedir-se"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "MENU_VENDA_CATEGORIAS", "3": "PROCESSAR_AMEACA", "4": "FIM_DIALOGO"}
    },

    # --- FLUXO DE AMEAÇA ---
    "PROCESSAR_AMEACA": { # Estado intermediário, sem opções para o jogador aqui. A lógica do NPC decide.
        "action_handler": "handle_ameaca", # NPC.py decidirá se vai para FUGINDO ou AMEACA_FRACASSADA
        "message": "Você me ameaça?!", # Mensagem inicial enquanto NPC processa
        "options": {},
        "transitions": {} # Definido programaticamente pelo handler
    },
    "FUGINDO": {
        "message": "SOCORRO! Um bandido! Fujam para as colinas!",
        "options": {"1": "[Continuar]"}, # Para o jogador fechar a "cena"
        "transitions": {"1": "FIM_DIALOGO_NPC_AUSENTE"} # Estado especial para indicar que NPC pode ter sumido
    },
    "AMEACA_FRACASSADA": {
        "message": "Hah! Acha que me intimida? Dê o fora da minha loja, seu verme!",
        "options": {"1": "[Sair da Loja]"},
        "transitions": {"1": "FIM_DIALOGO"}
    },

    # --- FLUXO DE COMPRA ---
    "MENU_COMPRA_CATEGORIAS": { # Jogador escolhe o item que quer ver/comprar
        "message": "O que te interessa hoje? Temos Poções e Equipamentos.",
        # As opções aqui poderiam ser geradas dinamicamente baseadas nos itens disponíveis.
        # Por agora, fixo para os itens que temos.
        "options": {
            "1": "Poção (10g)", 
            "2": "Espada (50g)", 
            "3": "Voltar ao Menu Principal"
        },
        "transitions": { # Estas transições levam a um estado onde o jogador confirma/negocia o item específico
            "1": "DETALHES_ITEM_POCAO", 
            "2": "DETALHES_ITEM_ESPADA", 
            "3": "INICIAL"
        }
    },
    "DETALHES_ITEM_POCAO": {
        "item_key": "pocao", # Para o NPC saber sobre qual item estamos falando
        "message": "Uma Poção de Cura, restaura um pouco de vida. Custa 10g. E então?",
        "options": {"1": "Comprar por 10g", "2": "Tentar Negociar Preço", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "NEGOCIANDO_PRECO_POCAO", "3": "MENU_COMPRA_CATEGORIAS"}
    },
    "DETALHES_ITEM_ESPADA": {
        "item_key": "espada",
        "message": "Uma Espada Curta, confiável para iniciantes. Custa 50g. Leva?",
        "options": {"1": "Comprar por 50g", "2": "Tentar Negociar Preço", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_COMPRA_ESPADA_BASE", "2": "NEGOCIANDO_PRECO_ESPADA", "3": "MENU_COMPRA_CATEGORIAS"}
    },

    # Negociação de Preço (Exemplo para Poção)
    "NEGOCIANDO_PRECO_POCAO": {
        "item_key": "pocao",
        "message": "Negociar, é? Hmm... Sou todo ouvidos, mas não espere milagres.",
        "options": {"1": "Insistir por um preço melhor (Persuadir)", "2": "Desistir (Pagar 10g)", "3": "Cancelar"},
        "transitions": {"1": "PROCESSAR_PERSUASAO_POCAO", "2": "PROCESSAR_COMPRA_POCAO_BASE", "3": "DETALHES_ITEM_POCAO"}
    },
    "PROCESSAR_PERSUASAO_POCAO": { # Estado intermediário para lógica de persuasão
        "item_key": "pocao",
        "action_handler": "handle_persuasao_desconto",
        "message": "Deixe-me pensar na sua... 'proposta'...",
        "options": {},
        "transitions": {} # Próximo estado (DESCONTO_OFERECIDO ou NEGOCIACAO_FALHOU) é definido pelo handler
    },
    "DESCONTO_OFERECIDO_POCAO": {
        "item_key": "pocao",
        "message": "Sorte sua, estou de bom humor! Poção por 8g. Aceita?", # Preço com desconto
        "options": {"1": "Sim, levar por 8g!", "2": "Não, obrigado"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_DESCONTO", "2": "DETALHES_ITEM_POCAO"}
    },
    "NEGOCIACAO_FALHOU_POCAO": {
        "item_key": "pocao",
        "message": "Desculpe, amigo. O preço da Poção é 10g. Sem choro.",
        "options": {"1": "Ok, pagar 10g", "2": "Deixar pra lá"},
        "transitions": {"1": "PROCESSAR_COMPRA_POCAO_BASE", "2": "DETALHES_ITEM_POCAO"}
    },
    
    # Processamento de Compra (estados intermediários para lógica de ouro e recusa)
    # A chave 'item_key' e 'preco_final' seriam usadas pela lógica do NPC.
    "PROCESSAR_COMPRA_POCAO_BASE":    {"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final": 10, "message": "Verificando seu ouro...", "options": {}, "transitions": {}},
    "PROCESSAR_COMPRA_POCAO_DESCONTO":{"action_handler": "handle_tentativa_compra", "item_key": "pocao",  "preco_final": 8,  "message": "Verificando seu ouro...", "options": {}, "transitions": {}},
    "PROCESSAR_COMPRA_ESPADA_BASE":   {"action_handler": "handle_tentativa_compra", "item_key": "espada", "preco_final": 50, "message": "Verificando seu ouro...", "options": {}, "transitions": {}},
    # Adicionar aqui PROCESSAR_COMPRA_ESPADA_DESCONTO se implementar negociação para espada

    # Resultados da Compra
    "COMPRA_SUCESSO": { # Mensagem será formatada pelo NPC com o nome do item
        "message": "Excelente escolha! {item_nome} adicionado à sua mochila.",
        "options": {"1": "[Continuar Comprando]", "2": "[Menu Principal]"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS", "2": "INICIAL"}
    },
    "SEM_OURO": { # Mensagem será formatada pelo NPC
        "message": "Ah, que pena. Parece que você não tem ouro suficiente para {item_nome}.",
        "options": {"1": "[Ok]"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS"} # Ou para o estado do item específico: DETALHES_ITEM_X
    },
    "RECUSANDO_VENDA_ALEATORIA": { # Mensagem será formatada
        "message": "Hmm... Quer saber? Hoje não estou com vontade de vender {item_nome} para você. Volte outra hora!",
        "options": {"1": "[Entendido]"},
        "transitions": {"1": "MENU_COMPRA_CATEGORIAS"}
    },

    # --- FLUXO DE VENDA (Simplificado por enquanto) ---
    "MENU_VENDA_CATEGORIAS": {
        "message": "Então você quer vender algo? O que você tem aí? (Venda não implementada)",
        "options": {"1": "[Voltar]"},
        "transitions": {"1": "INICIAL"}
    },

    # --- ESTADOS FINAIS DE DIÁLOGO ---
    "FIM_DIALOGO": { # Jogador escolheu sair ou uma ação levou ao fim
        "message": "Até mais, aventureiro! E cuidado por aí.",
        "options": {}, # Sem opções, o Game.py encerrará o modo de diálogo
        "transitions": {}
    },
    "FIM_DIALOGO_NPC_AUSENTE": { # NPC fugiu
        "message": "(O mercador não está mais aqui...)",
        "options": {},
        "transitions": {}
    }
}