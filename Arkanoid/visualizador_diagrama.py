from graphviz import Digraph
import os

def gerar_diagrama_afd():
    dot = Digraph(comment='AFD Arkanoid')
    dot.attr(rankdir='LR')
    
    estados = [
        'EsperandoLançamento', 'RastreandoBolaLenta', 'RastreandoBolaRapida',
        'AjustandoFino', 'DesviandoDeBloco', 'RecuperandoCentro',
        'ColetandoPowerUp', 'Pânico', 'GameOver'
    ]
    finais = ['GameOver']

    for estado in estados:
        shape = 'doublecircle' if estado in finais else 'ellipse'
        dot.node(estado, shape=shape)

    transicoes = [
        ('EsperandoLançamento', 'RastreandoBolaLenta', 'bola_lançada'),
        ('RastreandoBolaLenta', 'RastreandoBolaRapida', 'bola_rápida'),
        ('RastreandoBolaRapida', 'RastreandoBolaLenta', 'bola_lenta'),
        ('RastreandoBolaLenta', 'AjustandoFino', 'bola_perto_paddle'),
        ('RastreandoBolaRapida', 'AjustandoFino', 'bola_perto_paddle'),
        ('AjustandoFino', 'RastreandoBolaLenta', 'ajuste_feito'),
        ('RastreandoBolaLenta', 'Pânico', 'vidas==1'),
        ('RastreandoBolaRapida', 'Pânico', 'vidas==1'),
        ('Pânico', 'RastreandoBolaLenta', 'vidas>1 and len(powerups)<=1'),
        ('Pânico', 'GameOver', 'vidas==0'),
        ('ColetandoPowerUp', 'Pânico', 'len(powerups)>1'),
        ('RastreandoBolaLenta', 'DesviandoDeBloco', 'bloco_acima'),
        ('DesviandoDeBloco', 'RastreandoBolaLenta', 'bloco_livre'),
        ('RastreandoBolaLenta', 'ColetandoPowerUp', 'powerup_visível'),
        ('RastreandoBolaRapida', 'ColetandoPowerUp', 'powerup_visível && !perigo'),
        ('ColetandoPowerUp', 'RastreandoBolaLenta', 'powerup_coletado'),
        ('Pânico', 'RastreandoBolaLenta', 'situação_normaliza'),
        ('RastreandoBolaLenta', 'GameOver', 'perdeu_vida || vidas==0'),
        ('RastreandoBolaRapida', 'GameOver', 'perdeu_vida || vidas==0'),
        ('RecuperandoCentro', 'GameOver', 'perdeu_vida || vidas==0'),
        ('ColetandoPowerUp', 'GameOver', 'perdeu_vida || vidas==0'),
        ('RastreandoBolaLenta', 'RecuperandoCentro', 'bola_afasta'),
        ('RecuperandoCentro', 'RastreandoBolaLenta', 'centralizou'),
        ('GameOver', 'EsperandoLançamento', 'reiniciar')
    ]

    for origem, destino, evento in transicoes:
        dot.edge(origem, destino, label=evento)

    dot.attr('node', shape='point')
    dot.node('start')
    dot.edge('start', 'EsperandoLançamento', label='início')

    dot.render('afd_arkanoid', format='png', cleanup=True)
    print("AFD Arkanoid salvo como afd_arkanoid.png!")

def gerar_diagrama_afn():
    dot = Digraph(comment='AFN Arkanoid')
    dot.attr(rankdir='LR')
    
    estados = [
        'EsperandoLançamento', 'RastreandoBolaLenta', 'RastreandoBolaRapida',
        'AjustandoFino', 'DesviandoDeBloco', 'RecuperandoCentro',
        'ColetandoPowerUp', 'Pânico', 'GameOver'
    ]
    finais = ['GameOver']

    for estado in estados:
        shape = 'doublecircle' if estado in finais else 'ellipse'
        dot.node(estado, shape=shape)

    # AFN: Transições não determinísticas (com múltiplos destinos possíveis)
    transicoes = [
        ('EsperandoLançamento', 'RastreandoBolaLenta', 'bola_lançada'),
        ('EsperandoLançamento', 'ColetandoPowerUp', 'powerup&&!perigo'),
        ('RastreandoBolaLenta', 'RastreandoBolaRapida', 'bola_rápida'),
        ('RastreandoBolaLenta', 'ColetandoPowerUp', 'powerup'),
        ('RastreandoBolaLenta', 'Pânico', 'random() < 0.1'),
        ('RastreandoBolaRapida', 'AjustandoFino', 'bola_perto_paddle'),
        ('RastreandoBolaRapida', 'ColetandoPowerUp', 'powerup && random() < 0.2'),
        ('ColetandoPowerUp', 'RastreandoBolaLenta', 'powerup_coletado'),
        ('AjustandoFino', 'RastreandoBolaLenta', 'ajuste_feito'),
        ('DesviandoDeBloco', 'RastreandoBolaLenta', 'bloco_livre'),
        ('RastreandoBolaLenta', 'GameOver', 'perdeu_vida || vidas==0'),
        ('RastreandoBolaLenta', 'Pânico', 'perdeu_vida && random() < 0.2'),
        ('ColetandoPowerUp', 'GameOver', 'vidas==0'),
        ('ColetandoPowerUp', 'RastreandoBolaLenta', 'random() < 0.7'),
        ('Pânico', 'GameOver', 'vidas==0'),
        ('RecuperandoCentro', 'GameOver', 'vidas==0'),
        ('Pânico', 'RastreandoBolaLenta', 'normaliza'),
        ('RecuperandoCentro', 'RastreandoBolaLenta', 'centralizou'),
        ('GameOver', 'EsperandoLançamento', 'reiniciar'),
        ('RastreandoBolaLenta', 'Pânico', 'vidas==1'),
        ('RastreandoBolaLenta', 'Pânico', 'random()<0.08'),          # 8% de chance de pânico espontâneo
        ('ColetandoPowerUp', 'Pânico', 'len(powerups)>1'),
        ('RastreandoBolaRapida', 'Pânico', 'vidas==1'),
        ('AjustandoFino', 'Pânico', 'random()<0.04'),                # hesitação súbita
        # ---- Pânico pode voltar para vários estados ----
        ('Pânico', 'RastreandoBolaLenta', 'vidas>1 && random()<0.7'), # 70% das vezes volta ao rastreamento
        ('Pânico', 'ColetandoPowerUp', 'len(powerups)>0 && random()<0.3'), # 30% tenta coletar powerup mesmo em pânico
    ]

    for origem, destino, evento in transicoes:
        dot.edge(origem, destino, label=evento)

    dot.attr('node', shape='point')
    dot.node('start')
    dot.edge('start', 'EsperandoLançamento', label='início')

    dot.render('afn_arkanoid', format='png', cleanup=True)
    print("AFN Arkanoid salvo como afn_arkanoid.png!")

if __name__ == "__main__":
    gerar_diagrama_afd()
    gerar_diagrama_afn()
