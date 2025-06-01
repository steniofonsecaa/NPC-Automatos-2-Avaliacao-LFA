import random

tipo = "forge"
nome = "Ferreiro"

# Estados possíveis no AFN
estados = [
    'Esperando', 'OferecendoServico', 'ForjandoArma', 'MelhorandoArma',
    'FalhaForja', 'SucessoForja', 'NegociandoPreco', 'AceitandoDesafio',
    'RecusandoServico', 'Encerrado'
]

# Transições: AFN com múltiplos caminhos
transicoes = {
    ('Esperando', 'interagir'): ['OferecendoServico'],
    ('OferecendoServico', 'forjar'): ['ForjandoArma', 'NegociandoPreco', 'RecusandoServico'],
    ('OferecendoServico', 'melhorar'): ['MelhorandoArma', 'RecusandoServico'],
    ('OferecendoServico', 'desafio'): ['AceitandoDesafio', 'RecusandoServico'],
    ('ForjandoArma', 'resultado'): ['SucessoForja', 'FalhaForja'],
    ('MelhorandoArma', 'resultado'): ['SucessoForja', 'FalhaForja'],
    ('NegociandoPreco', 'pagar'): ['ForjandoArma'],
    ('AceitandoDesafio', 'lutar'): ['SucessoForja', 'FalhaForja'],
    ('SucessoForja', 'sair'): ['Encerrado'],
    ('FalhaForja', 'sair'): ['Encerrado'],
    ('RecusandoServico', 'sair'): ['Encerrado'],
}

# Mensagens fixas para cada estado
mensagens_customizadas = {
    'Esperando': "Sou o ferreiro desta vila. Precisa de algo?",
    'OferecendoServico': "Posso forjar armas, melhorar as suas ou aceitar um desafio. O que deseja?",
    'ForjandoArma': "Forjando sua arma... isso pode demorar.",
    'MelhorandoArma': "Afiando e reforçando sua arma...",
    'FalhaForja': "A forja falhou! Desculpe.",
    'SucessoForja': "Aqui está! Uma arma poderosa forjada especialmente para você.",
    'NegociandoPreco': "Esse serviço não é barato... pague ou saia.",
    'AceitandoDesafio': "Desafio aceito! Prepare-se para lutar.",
    'RecusandoServico': "Não vou trabalhar para alguém como você!",
    'Encerrado': "Boa sorte em sua jornada, guerreiro!"
}

# Função para escolher um estado no AFN (aleatório)
def escolher_proximo_estado(possiveis):
    return random.choice(possiveis) if possiveis else None
