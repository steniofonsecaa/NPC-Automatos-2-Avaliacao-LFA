from graphviz import Digraph
import os
import platform

PERGUNTAS_DISPONIVEIS_INFORMANTE = [
    "cidade", "castelo", "monstros", "historia", "lendas", 
    "animais magicos", "armas lendarias"
]

RESPOSTAS_INFORMANTE = {
    'cidade': "As cidades deste reino são antigas e cheias de segredos...",
    'castelo': "O grande castelo ao norte? Dizem que foi erguido por gigantes...",
}

INFORMANTE_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Saudações, viajante! Buscas conhecimento ou apenas um pouco de prosa? Tenho muitas histórias e informações.",
        "options": {"1": "Fazer uma pergunta", "2": "Despedir-se"},
        "transitions": {"1": "ESCOLHER_PERGUNTA", "2": "ENCERRADO"}
    },
    "ESCOLHER_PERGUNTA": { 
        "message": "Muito bem. Sobre o que sua curiosidade se debruça?",
        "options_generator_handler": "generate_informant_questions",
        "options": {"9": "Não tenho mais perguntas (Sair)"},
        "transitions": {"9": "ENCERRADO"}
    },
    "PROCESSAR_ESCOLHA_PERGUNTA": {
        "action_handler": "handle_escolha_pergunta",
        "message": "Hmm, uma boa pergunta...",
        "options": {}, "transitions": {}
    },
    "EXIBINDO_RESPOSTA": {
        "message": "Sobre isso, posso dizer que...", 
        "options": {"1": "Fazer outra pergunta", "2": "Entendido (Sair)"},
        "transitions": {"1": "ESCOLHER_PERGUNTA", "2": "ENCERRADO"}
    },
    "ENCERRADO": {
        "message": "Que seus caminhos sejam iluminados pelo conhecimento. Até breve!",
        "options": {}, "transitions": {}
    }
}

RESULTADOS_HANDLERS_INFORMANTE = {
    "PROCESSAR_ESCOLHA_PERGUNTA": {
        "Resposta Encontrada": "EXIBINDO_RESPOSTA"
    }
}

def gerar_grafo_informante_simples(automato_dict, nome_arquivo_saida='informante_afd_simples'):
    dot = Digraph(comment='AFD Informante Simplificado')
    dot.attr(rankdir='TD', labelloc='t', label='Autômato do Informante', fontsize='18',
             nodesep='0.5', ranksep='0.7') 

    estados_finais_reais = ['ENCERRADO'] 
    estados_de_processamento = [estado for estado, info in automato_dict.items() if info.get("action_handler") and not info.get("options")]
    estados_geradores_opcoes = [estado for estado, info in automato_dict.items() if info.get("options_generator_handler")]

    # 1. Adicionar TODOS os nós
    for estado_nome in automato_dict.keys():
        label_no = estado_nome 
        formato_no = 'ellipse' # Padrão para todos
        cor_borda_no = 'black'

        if estado_nome in estados_finais_reais:
            formato_no = 'doublecircle'
            
        dot.node(estado_nome, label=label_no, shape=formato_no, color=cor_borda_no)

    # 2. Adicionar transições
    for nome_estado_origem, info_estado_origem in automato_dict.items():
        opcoes = info_estado_origem.get("options", {})
        transicoes_definidas = info_estado_origem.get("transitions", {})

        # A. Transições diretas baseadas nas 'options' do jogador
        for chave_opcao, texto_opcao_completo in opcoes.items():
            if chave_opcao in transicoes_definidas:
                nome_estado_destino = transicoes_definidas[chave_opcao]
                
                label_aresta = texto_opcao_completo.replace("[", "").replace("]", "")
                if "(" in label_aresta: label_aresta = label_aresta.split("(")[0].strip() # Remove ex: (Sair)
                if not label_aresta: label_aresta = chave_opcao 
                if len(label_aresta) > 25: label_aresta = label_aresta[:22] + "..."


                dot.edge(nome_estado_origem, nome_estado_destino, label=label_aresta, style="solid", color="black", fontsize="8")
        
        # B. Transições a partir de estados de 'action_handler' (seus resultados)
        if nome_estado_origem in RESULTADOS_HANDLERS_INFORMANTE:
            for label_resultado, destino_final in RESULTADOS_HANDLERS_INFORMANTE[nome_estado_origem].items():
                dot.edge(nome_estado_origem, destino_final, label=label_resultado, style="solid", color="black", fontsize="8")

        # C. Transição especial para 'options_generator_handler'
        if nome_estado_origem == "ESCOLHER_PERGUNTA" and info_estado_origem.get("options_generator_handler"):
            # Transição genérica para representar a escolha de um tópico da lista
            # O destino é o estado que processa essa escolha.
            dot.edge(nome_estado_origem, "PROCESSAR_ESCOLHA_PERGUNTA", label="Seleciona Tópico", style="solid", color="black", fontsize="8")


    try:
        dot.format = 'png'
        output_path = dot.render(filename=nome_arquivo_saida, directory='.', cleanup=True)
        print(f"Diagrama '{output_path}' gerado com sucesso.")
        if platform.system() == 'Windows': os.startfile(output_path)
        elif platform.system() == 'Darwin': os.system(f'open "{output_path}"')
        else: os.system(f'xdg-open "{output_path}"')
    except Exception as e:
        print(f"Erro ao gerar ou abrir o diagrama: {e}")
        # print("\n--- CÓDIGO DOT GERADO ---"); print(dot.source); print("--------------------------")

if __name__ == '__main__':
    gerar_grafo_informante_simples(INFORMANTE_NPC_AUTOMATON)