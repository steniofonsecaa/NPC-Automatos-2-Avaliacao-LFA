import graphviz
import os
import platform

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

# Mapeamento dos resultados dos action_handlers para o Ferreiro
# Isso é usado para desenhar as transições implícitas no grafo
RESULTADOS_HANDLERS_FERREIRO = {
    "PROCESSAR_PEDIDO_FORJAR": {
        "Aceita Forjar": "FORJANDO_ARMA",
        "Recusa Serviço": "RECUSANDO_SERVICO_GERAL"
    },
    "FORJANDO_ARMA": {
        "Sucesso Forja": "SUCESSO_FORJA_MELHORIA_DESAFIO",
        "Falha Forja": "FALHA_FORJA_MELHORIA_DESAFIO"
    },
    "PROCESSAR_PEDIDO_MELHORAR": {
        "Aceita Melhorar": "ESCOLHER_ITEM_MELHORIA",
        "Recusa Serviço": "RECUSANDO_SERVICO_GERAL"
    },
    "MELHORANDO_ARMA": {
        "Melhoria Sucesso": "SUCESSO_FORJA_MELHORIA_DESAFIO",
        "Melhoria Falha": "FALHA_FORJA_MELHORIA_DESAFIO",
        "Recursos Insuficientes": "RECURSOS_INSUFICIENTES_MELHORIA"
    },
    "PROCESSAR_DESAFIO": {
        "Aceita Desafio": "ACEITANDO_DESAFIO",
        "Recusa Desafio": "RECUSANDO_SERVICO_GERAL"
    },
    "ACEITANDO_DESAFIO": {
        "Jogador Vence": "SUCESSO_FORJA_MELHORIA_DESAFIO",
        "Jogador Perde": "FALHA_FORJA_MELHORIA_DESAFIO"
    }
}

def generate_automaton_graph_ferreiro(automaton_data, graph_name="npc_ferreiro_afd"):
    dot = graphviz.Digraph(comment=graph_name, graph_attr={'rankdir': 'LR', 'splines': 'spline'})

    # Adicionar todos os estados como nós
    for state_name in automaton_data.keys():
        # Estados finais recebem formato de círculo duplo
        if state_name == "ENCERRADO":
            dot.node(state_name, state_name, shape='doublecircle', style='filled', fillcolor='lightcoral')
        # Estado inicial recebe formato especial ou cor
        elif state_name == "INICIAL":
            dot.node(state_name, state_name, shape='Mdiamond', style='filled', fillcolor='lightblue')
        # Outros estados normais
        else:
            dot.node(state_name, state_name)

    # Adicionar transições (arestas)
    for state_name, state_info in automaton_data.items():
        # Transições explícitas definidas no dicionário 'transitions'
        if "transitions" in state_info and state_info["transitions"]:
            for option, next_state in state_info["transitions"].items():
                label = state_info["options"].get(option, f"Opção {option}")
                # Limitar o tamanho do label para evitar sobreposição excessiva
                if len(label) > 30:
                    label = label[:27] + "..."
                dot.edge(state_name, next_state, label=label)

        # Tratar transições implícitas por 'action_handler'
        if state_name in RESULTADOS_HANDLERS_FERREIRO:
            for label_resultado, destino_final in RESULTADOS_HANDLERS_FERREIRO[state_name].items():
                dot.edge(state_name, destino_final, label=f"Ação: {label_resultado}")

        # Tratar transições implícitas por 'options_generator_handler'
        # No caso do Ferreiro, ESCOLHER_ITEM_MELHORIA leva a CONFIRMAR_MELHORIA_ITEM
        if state_name == "ESCOLHER_ITEM_MELHORIA" and \
           state_info.get("options_generator_handler") == "generate_melhoria_options_for_player":
            dot.edge(state_name, "CONFIRMAR_MELHORIA_ITEM", label="Item selecionado")


    # Renderizar o grafo
    output_path = os.path.join(os.getcwd(), graph_name)
    try:
        dot.render(output_path, format='png', view=True)
        print(f"Diagrama '{output_path}.png' gerado com sucesso.")
    except Exception as e:
        print(f"Erro ao gerar o diagrama: {e}")
        print("Certifique-se de que o Graphviz está instalado e configurado corretamente.")
        print(f"Output path tentado: {output_path}")

if __name__ == '__main__':
    generate_automaton_graph_ferreiro(FERREIRO_NPC)