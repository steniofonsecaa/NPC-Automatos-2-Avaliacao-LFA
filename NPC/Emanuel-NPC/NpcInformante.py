tipo = "info"
nome = "Informante"

# Estados do AP
estados = ['Esperando', 'Respondendo', 'Encerrado']

# Transições com pilha
transicoes = {
    ('Esperando', 'perguntar'): ['Respondendo'],
    ('Respondendo', 'perguntar'): ['Respondendo'],
    ('Respondendo', 'sair'): ['Encerrado'],
    ('Esperando', 'sair'): ['Encerrado'],
}

# Mensagens para cada estado
mensagens_customizadas = {
    'Esperando': "Ola, aventureiro! Posso ajuda-lo com algo?",
    'Respondendo': "Hmmm, sobre o que voce quer saber?",
    'Encerrado': "Espero ter ajudado. Ate logo!",
}
# Respostas personalizadas para perguntas
respostas_perguntas = {
    # Respostas para perguntas específicas (opcional, contextualizado)
    'cidade': "As cidades deste reino são antigas e cheias de segredos.",
    'castelo': "O castelo foi construído ha seculos, dizem que e assombrado.",
    'monstros': "Monstros rondam as florestas, cuidado ao viajar à noite!",
    'historia': "A historia deste mundo e repleta de batalhas e heróis lendarios.",
    'lendas': "Lendas falam de artefatos místicos escondidos.",
    'personagens': "Existem muitos personagens notaveis, cada um com sua própria história.",
    'cidades antigas': "As cidades antigas foram destruídas em uma grande guerra.",
    'guildas': "As guildas controlam o comercio e os contratos de mercenarios.",
    'reino perdido': "O Reino Perdido e uma lenda... ou talvez não.",
    'animais': "Dizem que animais magicos podem ser encontrados nas montanhas.",
    'lendas antigas': "As lendas antigas são passadas de geracão em geracão.",
    'rituais secretos': "Existem rituais que apenas os sabios conhecem.",
    'a origem da magia': "Ninguem sabe ao certo como a magia surgiu neste mundo.",
    'os guardioes do tempo': "Poucos ouviram falar dos Guardiões do Tempo, seres que vigiam as linhas temporais.",
    'armas': "Armas lendarias são forjadas com materiais raros e encantamentos poderosos.",
    'portais misticos': "Os portais místicos conectam reinos distantes, mas são perigosos de usar."
}


# Pilha para rastrear perguntas
pilha = []
# Perguntas disponíveis
perguntas_possiveis = [
   # "cidade", "castelo", "monstros", "história", "lendas", "personagens",
    #"cidades antigas", "guildas", "reino perdido", "animais magicos",
    #"lendas antigas", "rituais secretos", "a origem da magia", "os guardiões do tempo",
   # "armas lendarias", "portais místicos"
    "cidade", "castelo", "monstros", "historia", "lendas" #Versão Simplificada (não tinha tecla o suficiente pra ter todas acima)
    , "animais", "armas"

]

# Pilha para rastrear perguntas
pilha = []

def empilhar(pergunta):
    pilha.append(pergunta)

def desempilhar_tudo():
    return ", ".join(pilha) if pilha else "voce não perguntou nada."


def topo_pilha():
    return pilha[-1] if pilha else None