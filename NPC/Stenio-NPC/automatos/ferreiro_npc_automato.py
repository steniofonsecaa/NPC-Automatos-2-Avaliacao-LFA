FERREIRO_NPC = {
    "INICIAL": {
        "message": "Sou Férgus, o ferreiro. Posso sentir o aço em suas veias. Do que precisa?",
        "options": {
            "1": "Serviços de Forja",
            "2": "Desafiar o Ferreiro", 
            "3": "Nada, obrigado"
        },
        "transitions": {
            "1": "OFERECENDO_SERVICO",
            "2": "CONFIRMAR_DESAFIO",
            "3": "ENCERRADO"
        }
    },
    "OFERECENDO_SERVICO": {
        "message": "Posso forjar uma nova arma, melhorar uma que você já tenha, ou talvez precise de um reparo simples. O que será?",
        "options": {
            "1": "Forjar Nova Arma",   
            "2": "Melhorar Arma Existente",
            "3": "Voltar"
        },
        "transitions": {
            "1": "PROCESSAR_PEDIDO_FORJAR", 
            "2": "PROCESSAR_PEDIDO_MELHORAR",
            "3": "INICIAL"
        }
    },
    "RECURSOS_INSUFICIENTES_MELHORIA": {
        "message": "Você não possui todo o ouro ou materiais necessários para melhorar {item_nome}.",
        "options": {"1": "[Entendido]"},
        "transitions": {"1": "ESCOLHER_ITEM_MELHORIA"}
    },

    # --- Fluxo de Forjar Nova Arma ---
    "PROCESSAR_PEDIDO_FORJAR": {
        "action_handler": "handle_pedido_forjar", 
        "message": "Forjar uma nova arma, hein? Deixe-me ver suas intenções...", 
        "options": {}, "transitions": {}
    },
    "FORJANDO_ARMA": { 
        "action_handler": "handle_resultado_forja", 
        "message": "O aço canta ao meu comando! Estou forjando sua arma... Isso levará tempo e precisão.",
        "options": {}, "transitions": {} 
    },


    # --- Fluxo de Melhorar Arma ---
    "PROCESSAR_PEDIDO_MELHORAR": {
        "action_handler": "handle_pedido_melhorar", 
        "message": "Melhorar seu equipamento? Mostre-me o que você tem...",
        "options": {}, "transitions": {}
    },
    "ESCOLHER_ITEM_MELHORIA": { 
        "message": "Qual dos seus equipamentos você gostaria de melhorar? (Requer materiais e ouro)",
        "options_generator_handler": "generate_melhoria_options_for_player", 
        "options": {"9": "Voltar"}, 
        "transitions": {"9": "OFERECENDO_SERVICO"}
    },
    "CONFIRMAR_MELHORIA_ITEM": {
        "item_key": None,
        "message": "Melhorar sua {item_nome}? Custará [CustoMelhoria] e [Materiais]. Continuar?",
        "options": {"1": "Sim, melhorar", "2": "Não, ainda não"},
        "transitions": {"1": "MELHORANDO_ARMA", "2": "ESCOLHER_ITEM_MELHORIA"}
    },
    "MELHORANDO_ARMA": {
        "action_handler": "handle_resultado_melhoria", 
        "item_key": None, 
        "message": "Com cuidado e precisão, o potencial do seu equipamento será revelado...",
        "options": {}, "transitions": {}
    },

    # --- Fluxo de Desafio ---
    "CONFIRMAR_DESAFIO": { 
        "message": "Então você acha que pode me desafiar, é? Um teste de habilidade ou força? Confirme!",
        "options": {"1": "Sim, eu o desafio!", "2": "Não, foi um engano"},
        "transitions": {"1": "PROCESSAR_DESAFIO", "2": "INICIAL"}
    },
    "PROCESSAR_DESAFIO": {
        "action_handler": "handle_aceitar_desafio", 
        "message": "Um desafio... interessante.",
        "options": {}, "transitions": {}
    },
    "ACEITANDO_DESAFIO": { 
        "action_handler": "handle_resultado_luta_desafio", 
        "message": "Que seja! Prepare-se para enfrentar a fúria da minha forja... e dos meus punhos! LUTE!",
        "options": {}, "transitions": {} 
    },
    
    # --- Estados de Resultado Comuns (Forja/Melhoria/Desafio) ---
    "SUCESSO_FORJA_MELHORIA_DESAFIO": { 
        "message": "Perfeito! Sinta o poder desta criação/melhoria! Ou... impressionante sua perícia!",
        "options": {"1": "[Excelente!]"},
        "transitions": {"1": "OFERECENDO_SERVICO"} 
    },
    "FALHA_FORJA_MELHORIA_DESAFIO": { 
        "message": "Droga! Algo deu errado... o metal não respondeu, ou sua sorte o abandonou. Perdão.",
        "options": {"1": "[Que pena]"},
        "transitions": {"1": "OFERECENDO_SERVICO"} 
    },

    # --- Recusa de Serviço ---
    "RECUSANDO_SERVICO_GERAL": { 
        "message": "Hmpf. Não estou com disposição para trabalhar para você hoje. Volte outra hora... talvez.",
        "options": {"1": "[Entendido]"},
        "transitions": {"1": "INICIAL"} 
    },

    # --- Fim ---
    "ENCERRADO": { 
        "message": "Que seus caminhos sejam firmes e seu aço afiado. Até a próxima.",
        "options": {}, "transitions": {} 
    }
}