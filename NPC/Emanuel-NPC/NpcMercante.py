import random

class MercadorAFD:
    def __init__(self):
        self.estado = 'Esperando'
        self.transicoes = {
            ('Esperando', 'comprar'): 'ApresentandoItens',
            ('Esperando', 'ameacar'): 'Fugindo',
            ('ApresentandoItens', 'pressionar'): 'NegociandoPreco',
            ('ApresentandoItens', 'oferecer_troca'): 'AceitandoTroca',
            ('ApresentandoItens', 'pagar'): 'verificar_compra',
            ('ApresentandoItens', 'sair'): 'Encerrado',
            ('NegociandoPreco', 'pressionar'): 'OferecendoDesconto',
            ('NegociandoPreco', 'pagar'): 'verificar_compra',
            ('NegociandoPreco', 'oferecer_troca'): 'AceitandoTroca',
            ('NegociandoPreco', 'sair'): 'Encerrado',
            ('OferecendoDesconto', 'pagar'): 'verificar_compra',
            ('OferecendoDesconto', 'sair'): 'Encerrado',
            ('AceitandoTroca', 'pagar'): 'verificar_compra',
            ('AceitandoTroca', 'sair'): 'Encerrado',
            ('RecusandoVenda', 'sair'): 'Encerrado',
            ('ConcluindoVenda', 'sair'): 'Encerrado',
            ('Fugindo', 'sair'): 'Encerrado',
        }
        self.chance_recusar = 0.3  # 30% de chance de recusar

    def interagir(self, entrada):
        if self.estado != 'verificar_compra':
            chave = (self.estado, entrada)
            if chave in self.transicoes:
                proximo_estado = self.transicoes[chave]
                if proximo_estado == 'verificar_compra':
                    self._verificar_compra()
                else:
                    self.estado = proximo_estado
                    self._mensagem_estado()
            else:
                print(f"Mercador: 'nao sei como reagir a {entrada} no estado {self.estado}'.")
        else:
            self._verificar_compra()

    def _verificar_compra(self):
        if random.random() < self.chance_recusar:
            self.estado = 'RecusandoVenda'
            print("Mercador cruza os bracos: 'nao vendo para voce!'.")
        else:
            self.estado = 'ConcluindoVenda'
            print("Mercador sorri: 'negocio fechado, obrigado pela compra!'")

    def _mensagem_estado(self):
        mensagens = {
            'Esperando': "Mercador esta esperando um cliente...",
            'ApresentandoItens': "Mercador mostra seus itens: 'Veja, tenho boas ofertas!'",
            'NegociandoPreco': "Mercador diz: 'Podemos negociar o preco, mas nao abuse!'",
            'OferecendoDesconto': "Mercador suspira: 'Ta bom, um desconto pequeno!'",
            'AceitandoTroca': "Mercador pondera: 'Hmm, aceito essa troca...'",
            'RecusandoVenda': "Mercador diz: 'nao vendo para voce!'",
            'ConcluindoVenda': "Mercador sorri: 'negocio fechado, obrigado pela compra!'",
            'Fugindo': "Mercador grita: 'Socorro!' e foge rapidamente!",
            'Encerrado': "Mercador se despede: 'Ate logo!'",
        }
        print(mensagens.get(self.estado, f"Mercador esta em um estado estranho: {self.estado}"))
# Definindo os dados para o visualizador
estados = [
    'Esperando', 'ApresentandoItens', 'NegociandoPreco', 'OferecendoDesconto',
    'AceitandoTroca', 'RecusandoVenda', 'ConcluindoVenda', 'Fugindo', 'Encerrado','verificar_compra'
]

transicoes = [
    ('Esperando', 'ApresentandoItens', 'comprar'),
    ('Esperando', 'Fugindo', 'ameacar'),
    ('ApresentandoItens', 'NegociandoPreco', 'pressionar'),
    ('ApresentandoItens', 'AceitandoTroca', 'OferecerTroca'),
    ('ApresentandoItens', 'verificar_compra', 'pagar'),
    ('ApresentandoItens', 'Encerrado', 'sair'),
    ('NegociandoPreco', 'OferecendoDesconto', 'pressionar'),
    ('NegociandoPreco', 'verificar_compra', 'pagar'),
    ('NegociandoPreco', 'AceitandoTroca', 'OferecerTroca'),
    ('NegociandoPreco', 'Encerrado', 'sair'),
    ('OferecendoDesconto', 'verificar_compra', 'pagar'),
    ('OferecendoDesconto', 'Encerrado', 'sair'),
    ('AceitandoTroca', 'verificar_compra', 'pagar'),
    ('verificar_compra', 'RecusandoVenda', 'insistir'),
    ('verificar_compra', 'ConcluindoVenda', 'aceitar'), 
    ('AceitandoTroca', 'Encerrado', 'sair'),
    ('RecusandoVenda', 'Encerrado', 'sair'),
    ('ConcluindoVenda','Encerrado', 'sair'),
    ('Fugindo', 'Encerrado', 'sair')
]
mensagens_customizadas = {
    'Esperando': "Ola, aventureiro! Posso ajuda-lo com algo?",
    'ApresentandoItens': "Veja meus produtos: pocões, espadas e muito mais!",
    'NegociandoPreco': "Podemos discutir o preco, mas nao exagere!",
    'OferecendoDesconto': "Tudo bem, posso oferecer um pequeno desconto.",
    'AceitandoTroca': "Sua oferta e interessante. Aceito a troca.",
    'RecusandoVenda': "Desculpe, nao posso vender para voce.",
    'ConcluindoVenda': "negocio fechado! Obrigado pela compra.",
    'Fugindo': "Socorro! Estou sendo ameacado!",
    'verificar_compra': "O mercador esta pensando se vai vender ou nao para voce...",
    'Encerrado': "Ate logo! Volte sempre que precisar."
}
mensagens = {
            'Esperando': "Mercador esta esperando um cliente...",
            'ApresentandoItens': "Mercador mostra seus itens: 'Veja, tenho boas ofertas!'",
            'NegociandoPreco': "Mercador diz: 'Podemos negociar o preco, mas nao abuse!'",
            'OferecendoDesconto': "Mercador suspira: 'Ta bom, um desconto pequeno!'",
            'AceitandoTroca': "Mercador pondera: 'Hmm, aceito essa troca...'",
            'RecusandoVenda': "Mercador diz: 'nao vendo para voce!'",
            'ConcluindoVenda': "Mercador sorri: 'negocio fechado, obrigado pela compra!'",
            'verificar_compra': "O mercador esta pensando se vai vender ou nao para voce...",
            'Fugindo': "Mercador grita: 'Socorro!' e foge rapidamente!",
            'Encerrado': "Mercador se despede: 'Ate logo!'",
        }
nome = "Mercador"
tipo = "shop"


