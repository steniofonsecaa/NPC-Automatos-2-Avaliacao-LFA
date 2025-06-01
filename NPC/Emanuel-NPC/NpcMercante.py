import random

class MercadorAFD:
    def __init__(self):
        self.estado = 'Esperando'
        self.transicoes = {
            ('Esperando', 'comprar'): 'ApresentandoItens',
            ('Esperando', 'ameaçar'): 'Fugindo',
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
                print(f"Mercador: 'Não sei como reagir a {entrada} no estado {self.estado}'.")
        else:
            self._verificar_compra()

    def _verificar_compra(self):
        if random.random() < self.chance_recusar:
            self.estado = 'RecusandoVenda'
            print("Mercador cruza os braços: 'Não vendo para você!'.")
        else:
            self.estado = 'ConcluindoVenda'
            print("Mercador sorri: 'Negócio fechado, obrigado pela compra!'")

    def _mensagem_estado(self):
        mensagens = {
            'Esperando': "Mercador está esperando um cliente...",
            'ApresentandoItens': "Mercador mostra seus itens: 'Veja, tenho boas ofertas!'",
            'NegociandoPreco': "Mercador diz: 'Podemos negociar o preço, mas não abuse!'",
            'OferecendoDesconto': "Mercador suspira: 'Tá bom, um desconto pequeno!'",
            'AceitandoTroca': "Mercador pondera: 'Hmm, aceito essa troca...'",
            'RecusandoVenda': "Mercador diz: 'Não vendo para você!'",
            'ConcluindoVenda': "Mercador sorri: 'Negócio fechado, obrigado pela compra!'",
            'Fugindo': "Mercador grita: 'Socorro!' e foge rapidamente!",
            'Encerrado': "Mercador se despede: 'Até logo!'",
        }
        print(mensagens.get(self.estado, f"Mercador está em um estado estranho: {self.estado}"))
# Definindo os dados para o visualizador
estados = [
    'Esperando', 'ApresentandoItens', 'NegociandoPreco', 'OferecendoDesconto',
    'AceitandoTroca', 'RecusandoVenda', 'ConcluindoVenda', 'Fugindo', 'Encerrado'
]

transicoes = [
    ('Esperando', 'ApresentandoItens', 'comprar'),
    ('Esperando', 'Fugindo', 'ameaçar'),
    ('ApresentandoItens', 'NegociandoPreco', 'pressionar'),
    ('ApresentandoItens', 'AceitandoTroca', 'oferecer_troca'),
    ('ApresentandoItens', 'verificar_compra', 'pagar'),
    ('ApresentandoItens', 'Encerrado', 'sair'),
    ('NegociandoPreco', 'OferecendoDesconto', 'pressionar'),
    ('NegociandoPreco', 'verificar_compra', 'pagar'),
    ('NegociandoPreco', 'AceitandoTroca', 'oferecer_troca'),
    ('NegociandoPreco', 'sair', 'Encerrado'),
    ('OferecendoDesconto', 'verificar_compra', 'pagar'),
    ('OferecendoDesconto', 'sair', 'Encerrado'),
    ('AceitandoTroca', 'verificar_compra', 'pagar'),
    ('AceitandoTroca', 'sair', 'Encerrado'),
    ('RecusandoVenda', 'sair', 'Encerrado'),
    ('ConcluindoVenda', 'sair', 'Encerrado'),
    ('Fugindo', 'sair', 'Encerrado')
]
mensagens_customizadas = {
    'Esperando': "Olá, aventureiro! Posso ajudá-lo com algo?",
    'ApresentandoItens': "Veja meus produtos: poções, espadas e muito mais!",
    'NegociandoPreco': "Podemos discutir o preço, mas não exagere!",
    'OferecendoDesconto': "Tudo bem, posso oferecer um pequeno desconto.",
    'AceitandoTroca': "Sua oferta é interessante. Aceito a troca.",
    'RecusandoVenda': "Desculpe, não posso vender para você.",
    'ConcluindoVenda': "Negócio fechado! Obrigado pela compra.",
    'Fugindo': "Socorro! Estou sendo ameaçado!",
    'Encerrado': "Até logo! Volte sempre que precisar."
}
mensagens = {
            'Esperando': "Mercador está esperando um cliente...",
            'ApresentandoItens': "Mercador mostra seus itens: 'Veja, tenho boas ofertas!'",
            'NegociandoPreco': "Mercador diz: 'Podemos negociar o preço, mas não abuse!'",
            'OferecendoDesconto': "Mercador suspira: 'Tá bom, um desconto pequeno!'",
            'AceitandoTroca': "Mercador pondera: 'Hmm, aceito essa troca...'",
            'RecusandoVenda': "Mercador diz: 'Não vendo para você!'",
            'ConcluindoVenda': "Mercador sorri: 'Negócio fechado, obrigado pela compra!'",
            'Fugindo': "Mercador grita: 'Socorro!' e foge rapidamente!",
            'Encerrado': "Mercador se despede: 'Até logo!'",
        }
nome = "Mercador"
tipo = "shop"


