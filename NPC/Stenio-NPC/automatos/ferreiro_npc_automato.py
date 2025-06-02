FERREIRO_NPC = {
    "INICIAL": { # Equivalente a 'Esperando'
        "message": "Sou Férgus, o ferreiro. Posso sentir o aço em suas veias. Do que precisa?",
        "options": {
            "1": "Serviços de Forja",
            "2": "Desafiar o Ferreiro", # Se quiser manter essa opção
            "3": "Nada, obrigado"
        },
        "transitions": {
            "1": "OFERECENDO_SERVICO",
            "2": "CONFIRMAR_DESAFIO", # Leva a uma confirmação antes do processamento
            "3": "ENCERRADO"
        }
    },
    "OFERECENDO_SERVICO": {
        "message": "Posso forjar uma nova arma, melhorar uma que você já tenha, ou talvez precise de um reparo simples. O que será?",
        "options": {
            "1": "Forjar Nova Arma",    # Input 'forjar'
            "2": "Melhorar Arma Existente", # Input 'melhorar'
            "3": "Voltar"
        },
        "transitions": {
            "1": "PROCESSAR_PEDIDO_FORJAR", # Estado intermediário para 'forjar'
            "2": "PROCESSAR_PEDIDO_MELHORAR", # Estado intermediário para 'melhorar'
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
        "action_handler": "handle_pedido_forjar", # Decide entre Forjando, Negociando, Recusando
        "message": "Forjar uma nova arma, hein? Deixe-me ver suas intenções...", # Mensagem enquanto processa
        "options": {}, "transitions": {}
    },
    "FORJANDO_ARMA": { # Se o pedido for aceito diretamente ou após negociação
        "action_handler": "handle_resultado_forja", # Determina sucesso ou falha da forja
        "message": "O aço canta ao meu comando! Estou forjando sua arma... Isso levará tempo e precisão.",
        "options": {}, "transitions": {} # Jogador espera
    },


    # --- Fluxo de Melhorar Arma ---
    "PROCESSAR_PEDIDO_MELHORAR": {
        "action_handler": "handle_pedido_melhorar", # Decide se aceita melhorar ou recusa
        "message": "Melhorar seu equipamento? Mostre-me o que você tem...",
        "options": {}, "transitions": {}
    },
    "ESCOLHER_ITEM_MELHORIA": { # Se o pedido de melhoria for aceito
        "message": "Qual dos seus equipamentos você gostaria de melhorar? (Requer materiais e ouro)",
        "options_generator_handler": "generate_melhoria_options_for_player", # Lista itens do jogador
        "options": {"9": "Voltar"}, # Opção fixa de voltar
        "transitions": {"9": "OFERECENDO_SERVICO"}
        # Transições para itens específicos serão para CONFIRMAR_MELHORIA_ITEM
    },
    "CONFIRMAR_MELHORIA_ITEM": {
        "item_key": None, # Preenchido dinamicamente
        "message": "Melhorar sua {item_nome}? Custará [CustoMelhoria] e [Materiais]. Continuar?", # Dinâmico
        "options": {"1": "Sim, melhorar", "2": "Não, ainda não"},
        "transitions": {"1": "MELHORANDO_ARMA", "2": "ESCOLHER_ITEM_MELHORIA"}
    },
    "MELHORANDO_ARMA": {
        "action_handler": "handle_resultado_melhoria", # Determina sucesso/falha
        "item_key": None, # Preenchido pelo estado anterior
        "message": "Com cuidado e precisão, o potencial do seu equipamento será revelado...",
        "options": {}, "transitions": {} # Jogador espera
    },

    # --- Fluxo de Desafio ---
    "CONFIRMAR_DESAFIO": { # Equivalente a 'OferecendoServico' -> 'desafio'
        "message": "Então você acha que pode me desafiar, é? Um teste de habilidade ou força? Confirme!",
        "options": {"1": "Sim, eu o desafio!", "2": "Não, foi um engano"},
        "transitions": {"1": "PROCESSAR_DESAFIO", "2": "INICIAL"}
    },
    "PROCESSAR_DESAFIO": {
        "action_handler": "handle_aceitar_desafio", # Decide se aceita ou recusa o desafio
        "message": "Um desafio... interessante.",
        "options": {}, "transitions": {}
    },
    "ACEITANDO_DESAFIO": { # Se o desafio for aceito
        "action_handler": "handle_resultado_luta_desafio", # Determina sucesso/falha da luta
        "message": "Que seja! Prepare-se para enfrentar a fúria da minha forja... e dos meus punhos! LUTE!",
        "options": {}, "transitions": {} # Lógica da luta ocorreria aqui
    },
    
    # --- Estados de Resultado Comuns (Forja/Melhoria/Desafio) ---
    "SUCESSO_FORJA_MELHORIA_DESAFIO": { # 'SucessoForja'
        "message": "Perfeito! Sinta o poder desta criação/melhoria! Ou... impressionante sua perícia!",
        "options": {"1": "[Excelente!]"},
        "transitions": {"1": "OFERECENDO_SERVICO"} # Ou INICIAL
    },
    "FALHA_FORJA_MELHORIA_DESAFIO": { # 'FalhaForja'
        "message": "Droga! Algo deu errado... o metal não respondeu, ou sua sorte o abandonou. Perdão.",
        "options": {"1": "[Que pena]"},
        "transitions": {"1": "OFERECENDO_SERVICO"} # Ou INICIAL
    },

    # --- Recusa de Serviço ---
    "RECUSANDO_SERVICO_GERAL": { # 'RecusandoServico'
        "message": "Hmpf. Não estou com disposição para trabalhar para você hoje. Volte outra hora... talvez.",
        "options": {"1": "[Entendido]"},
        "transitions": {"1": "INICIAL"} 
    },

    # --- Fim ---
    "ENCERRADO": { # 'Encerrado'
        "message": "Que seus caminhos sejam firmes e seu aço afiado. Até a próxima.",
        "options": {}, "transitions": {} # Sem opções, o Game.py encerrará
    }
}