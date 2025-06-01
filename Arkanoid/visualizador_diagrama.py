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
        # Início
        ('EsperandoLançamento', 'RastreandoBolaLenta', 'bola_lançada'),
        # Prioridade powerup (se visível e não perigoso)
        ('EsperandoLançamento', 'ColetandoPowerUp', 'powerup_visível && !perigo'),
        # Bola lenta <-> rápida
        ('RastreandoBolaLenta', 'RastreandoBolaRapida', 'bola_rápida'),
        ('RastreandoBolaRapida', 'RastreandoBolaLenta', 'bola_lenta'),
        # Microajuste perto do paddle
        ('RastreandoBolaLenta', 'AjustandoFino', 'bola_perto_paddle'),
        ('RastreandoBolaRapida', 'AjustandoFino', 'bola_perto_paddle'),
        # Microajuste terminado
        ('AjustandoFino', 'RastreandoBolaLenta', 'ajuste_feito'),
        # Desviar bloco
        ('RastreandoBolaLenta', 'DesviandoDeBloco', 'bloco_acima'),
        ('DesviandoDeBloco', 'RastreandoBolaLenta', 'bloco_livre'),
        # Power-up visível e seguro
        ('RastreandoBolaLenta', 'ColetandoPowerUp', 'powerup_visível && !perigo'),
        ('RastreandoBolaRapida', 'ColetandoPowerUp', 'powerup_visível && !perigo'),
        # Power-up coletado volta ao rastreamento
        ('ColetandoPowerUp', 'RastreandoBolaLenta', 'powerup_coletado'),
        # Estado de pânico (vidas==1 ou múltiplos powerups simultâneos)
        ('RastreandoBolaLenta', 'Pânico', 'vidas==1 || multi_powerups'),
        ('RastreandoBolaRapida', 'Pânico', 'vidas==1 || multi_powerups'),
        ('ColetandoPowerUp', 'Pânico', 'multi_powerups'),
        # Pânico pode normalizar (vidas>1 && len(powerups)<=1)
        ('Pânico', 'RastreandoBolaLenta', 'vidas>1 && powerups<=1'),
        # Bola perdida ou vidas zeradas em qualquer estado relevante
        ('RastreandoBolaLenta', 'GameOver', 'perdeu_vida || vidas==0'),
        ('RastreandoBolaRapida', 'GameOver', 'perdeu_vida || vidas==0'),
        ('RecuperandoCentro', 'GameOver', 'perdeu_vida || vidas==0'),
        ('ColetandoPowerUp', 'GameOver', 'perdeu_vida || vidas==0'),
        ('Pânico', 'GameOver', 'vidas==0'),
        # Recuperando centro
        ('RastreandoBolaLenta', 'RecuperandoCentro', 'bola_afasta'),
        ('RecuperandoCentro', 'RastreandoBolaLenta', 'centralizou'),
        # Reinício
        ('GameOver', 'EsperandoLançamento', 'reiniciar'),
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