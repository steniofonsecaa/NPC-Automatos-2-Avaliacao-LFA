import graphviz
import os
import platform

# As definições do autômato do informante
PERGUNTAS_DISPONIVEIS_INFORMANTE = [
    "cidade", "castelo", "monstros", "historia", "lendas",
    "animais magicos", "armas lendarias"
]

RESPOSTAS_INFORMANTE = {
    'cidade': "As cidades deste reino são antigas e cheias de segredos. Cada pedra conta uma história.", 
    'castelo': "O grande castelo ao norte? Dizem que foi erguido por gigantes e que seus salões ecoam com os fantasmas do passado.", 
    'monstros': "As bestas selvagens e criaturas da noite espreitam além das muralhas seguras. Viaje com cautela, especialmente ao anoitecer!", 
    'historia': "Este reino viu a ascensão e queda de impérios! Heróis nasceram e pereceram, e muitas crônicas se perderam no tempo.", 
    'lendas': "Ah, as lendas! Falam de tesouros esquecidos, bestas míticas e ilhas que aparecem e desaparecem com a maré.", 
    'animais magicos': "Sim, criaturas imbuídas de magia ainda vagam pelas florestas primordiais e picos montanhosos. Avistá-las é um privilégio... ou um aviso.", 
    'armas lendarias': "Existem contos sobre armas de poder incomensurável, forjadas pelos deuses antigos ou por artesãos de eras esquecidas. Encontrá-las é o destino de poucos." 
}

INFORMANTE_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Saudações, viajante! Buscas conhecimento ou apenas um pouco de prosa? Tenho muitas histórias e informações.", 
        "options": {
            "1": "Fazer uma pergunta", 
            "2": "Despedir-se"
        },
        "transitions": {
            "1": "ESCOLHER_PERGUNTA", 
            "2": "ENCERRADO" 
        }
    },
    "ESCOLHER_PERGUNTA": {
        "message": "Muito bem. Sobre o que sua curiosidade se debruça?", 
        "options_generator_handler": "generate_informant_questions",
        "options": {
            "9": "Não tenho mais perguntas (Sair)"
        },
        "transitions": {
            "9": "ENCERRADO" 
        }
    },
    "PROCESSAR_ESCOLHA_PERGUNTA": {
        "action_handler": "handle_escolha_pergunta", 
        "message": "Hmm, uma boa pergunta...", 
        "options": {}, 
        "transitions": {}
    },
    "EXIBINDO_RESPOSTA": {
        "message": "Sobre isso, posso dizer que...", 
        "options": {
            "1": "Fazer outra pergunta", 
            "2": "Entendido (Sair)" 
        },
        "transitions": {
            "1": "ESCOLHER_PERGUNTA", 
            "2": "ENCERRADO" 
        }
    },
    "ENCERRADO": {
        "message": "Que seus caminhos sejam iluminados pelo conhecimento. Até breve!", 
        "options": {},
        "transitions": {} 
    }
} 

def generate_automaton_graph_informant(automaton_data, graph_name="npc_informante_afd"):

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
                dot.edge(state_name, next_state, label=label)

        # Tratar transições implícitas por 'action_handler'
        # No caso do Informante, PROCESSAR_ESCOLHA_PERGUNTA leva a EXIBINDO_RESPOSTA
        if state_name == "PROCESSAR_ESCOLHA_PERGUNTA" and state_info.get("action_handler") == "handle_escolha_pergunta":
            dot.edge(state_name, "EXIBINDO_RESPOSTA", label="Ação: Resposta Gerada")

        # Tratar transições implícitas por 'options_generator_handler'
        # ESCOLHER_PERGUNTA gera opções que levam a PROCESSAR_ESCOLHA_PERGUNTA
        if state_name == "ESCOLHER_PERGUNTA" and state_info.get("options_generator_handler") == "generate_informant_questions":
            dot.edge(state_name, "PROCESSAR_ESCOLHA_PERGUNTA", label="Tópico de pergunta selecionado")

    # Renderizar o grafo
    output_path = os.path.join(os.getcwd(), graph_name)
    dot.render(output_path, format='png', view=True)

# Chamar a função para gerar o grafo
if __name__ == '__main__':
    generate_automaton_graph_informant(INFORMANTE_NPC_AUTOMATON)