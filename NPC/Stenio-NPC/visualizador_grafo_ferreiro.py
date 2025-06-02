# gerar_grafo_ferreiro_afn_simples.py
from graphviz import Digraph
import os
import platform

# --- COPIE A DEFINIÇÃO COMPLETA E MAIS ATUAL DO SEU FERREIRO_NPC AQUI ---
# Esta é a versão que você forneceu, sem a negociação de preço da forja.
FERREIRO_NPC = {
    "INICIAL": { 
        "message": "Sou Férgus, o ferreiro. Posso sentir o aço em suas veias. Do que precisa?",
        "options": {"1": "Serviços de Forja", "2": "Desafiar o Ferreiro", "3": "Nada, obrigado"},
        "transitions": {"1": "OFERECENDO_SERVICO", "2": "CONFIRMAR_DESAFIO", "3": "ENCERRADO"}
    },
    "OFERECENDO_SERVICO": {
        "message": "Posso forjar uma nova arma, melhorar uma que você já tenha, ou talvez precise de um reparo simples. O que será?",
        "options": {"1": "Forjar Nova Arma", "2": "Melhorar Arma Existente", "3": "Voltar"},
        "transitions": {"1": "PROCESSAR_PEDIDO_FORJAR", "2": "PROCESSAR_PEDIDO_MELHORAR", "3": "INICIAL"}
    },
    "RECURSOS_INSUFICIENTES_MELHORIA": {
        "message": "Você não possui todo o ouro ou materiais necessários para melhorar {item_nome}.",
        "options": {"1": "[Entendido e Sair]"},
        "transitions": {"1": "ENCERRADO"} 
    },
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
    "RECUSANDO_SERVICO_GERAL": { 
        "message": "Hmpf. Não estou com disposição para trabalhar para você hoje. Volte outra hora... talvez.",
        "options": {"1": "[Entendido]"},
        "transitions": {"1": "INICIAL"} 
    },
    "ENCERRADO": { 
        "message": "Que seus caminhos sejam firmes e seu aço afiado. Até a próxima.",
        "options": {}, "transitions": {} 
    }
}
# --- FIM: Definição do FERREIRO_NPC ---

# Mapeamento dos resultados dos action_handlers para o Ferreiro (como antes)
RESULTADOS_HANDLERS_FERREIRO = {
    "PROCESSAR_PEDIDO_FORJAR": {"Aceita Forjar": "FORJANDO_ARMA", "Recusa Serviço": "RECUSANDO_SERVICO_GERAL"},
    "FORJANDO_ARMA": {"Sucesso": "SUCESSO_FORJA_MELHORIA_DESAFIO", "Falha": "FALHA_FORJA_MELHORIA_DESAFIO"},
    "PROCESSAR_PEDIDO_MELHORAR": {"Aceita Melhorar": "ESCOLHER_ITEM_MELHORIA", "Recusa Serviço": "RECUSANDO_SERVICO_GERAL"},
    "MELHORANDO_ARMA": {"Melhoria OK": "SUCESSO_FORJA_MELHORIA_DESAFIO", "Falha Melhoria": "FALHA_FORJA_MELHORIA_DESAFIO", "Sem Recursos": "RECURSOS_INSUFICIENTES_MELHORIA"},
    "PROCESSAR_DESAFIO": {"Aceita Desafio": "ACEITANDO_DESAFIO", "Recusa Desafio": "RECUSANDO_SERVICO_GERAL"},
    "ACEITANDO_DESAFIO": {"Jogador Vence": "SUCESSO_FORJA_MELHORIA_DESAFIO", "Jogador Perde": "FALHA_FORJA_MELHORIA_DESAFIO"}
}

def gerar_grafo_afn_ferreiro(automato_dict, nome_arquivo_saida='ferreiro_afn_visual'):
    dot = Digraph(comment='AFN Ferreiro')
    dot.attr(rankdir='TD', labelloc='t', label='Autômato do Ferreiro', fontsize='18',
             nodesep='0.5', ranksep='0.7', splines='spline') # Ajuste splines conforme necessário

    # Apenas o estado 'ENCERRADO' será visualmente "final" com círculo duplo
    estados_finais_reais = ['ENCERRADO'] 

    # 1. Adicionar TODOS os nós
    for estado_nome in automato_dict.keys():
        label_no = estado_nome # Apenas o nome do estado no nó
        formato_no = 'ellipse' # Padrão para todos os estados não-finais
        cor_borda_no = 'black'

        if estado_nome in estados_finais_reais:
            formato_no = 'doublecircle'
        elif estado_nome == 'INICIAL':
            # Pode dar um destaque sutil ao estado inicial se quiser, ex: borda mais grossa
            # dot.node(estado_nome, ..., penwidth='2')
            pass # Ou manter padrão
            
        dot.node(estado_nome, label=label_no, shape=formato_no, color=cor_borda_no)

    # 2. Adicionar transições
    for nome_estado_origem, info_estado_origem in automato_dict.items():
        opcoes = info_estado_origem.get("options", {})
        transicoes_definidas = info_estado_origem.get("transitions", {})

        # A. Transições diretas baseadas nas 'options' do jogador (escolhas visíveis)
        for chave_opcao, texto_opcao_completo in opcoes.items():
            if chave_opcao in transicoes_definidas:
                nome_estado_destino = transicoes_definidas[chave_opcao]
                
                label_aresta = texto_opcao_completo.replace("[", "").replace("]", "")
                if "(" in label_aresta: label_aresta = label_aresta.split("(")[0].strip()
                if len(label_aresta) > 20: label_aresta = label_aresta[:18] + "..."
                if not label_aresta: label_aresta = chave_opcao # Fallback

                dot.edge(nome_estado_origem, nome_estado_destino, label=label_aresta, style="solid", color="black", fontsize="8")
        
        # B. Transições a partir de estados de 'action_handler' (seus resultados)
        # Estas mostram o comportamento "não determinístico" do NPC
        if nome_estado_origem in RESULTADOS_HANDLERS_FERREIRO:
            for label_resultado, destino_final in RESULTADOS_HANDLERS_FERREIRO[nome_estado_origem].items():
                # Todas as linhas são sólidas e pretas. O label indica a natureza do resultado.
                dot.edge(nome_estado_origem, destino_final, label=label_resultado, style="solid", color="black", fontsize="8")

        # C. Transição especial para 'options_generator_handler'
        if nome_estado_origem == "ESCOLHER_ITEM_MELHORIA" and info_estado_origem.get("options_generator_handler"):
            # Transição genérica para representar a escolha de um item da lista
            dot.edge(nome_estado_origem, "CONFIRMAR_MELHORIA_ITEM", label="Seleciona Item", style="solid", color="black", fontsize="8")


    try:
        dot.format = 'png'
        output_path = dot.render(filename=nome_arquivo_saida, directory='.', cleanup=True)
        print(f"Diagrama '{output_path}' gerado com sucesso.")
        if platform.system() == 'Windows': os.startfile(output_path)
        elif platform.system() == 'Darwin': os.system(f'open "{output_path}"')
        else: os.system(f'xdg-open "{output_path}"')
    except Exception as e:
        print(f"Erro ao gerar ou abrir o diagrama: {e}")
        # print("\n--- CÓDIGO DOT GERADO PARA DEBUG ---"); print(dot.source); print("------------------------------------")

if __name__ == '__main__':
    gerar_grafo_afn_ferreiro(FERREIRO_NPC)