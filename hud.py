import pyxel
import config

class HUD:
    @staticmethod
    def draw(score, vidas, fase=1, game_over=False, paused=False, powerups=None, instrucoes=False, high_score=0):
        # Fundo superior do HUD
        pyxel.rect(0, 0, config.SCREEN_WIDTH, 14, config.HUD_BG_COLOR)
        
        # Placar (score) destacado
        pyxel.text(6, 4, f"SCORE:", config.HUD_LABEL_COLOR)
        pyxel.text(40, 4, f"{score:06}", config.HUD_SCORE_COLOR)
        
        # High Score ao lado
        #pyxel.text(92, 4, f"HIGH:", config.HUD_LABEL_COLOR)
        #pyxel.text(124, 4, f"{high_score:06}", config.HUD_HISCORE_COLOR)
        
        # Vidas como corações
        for i in range(vidas):
            HUD._draw_coracao(config.SCREEN_WIDTH - 10 - 10*i, 4, config.HEART_COLOR)
        pyxel.text(config.SCREEN_WIDTH - 58, 4, "VIDAS:", config.HUD_LABEL_COLOR)
        
        # Fase centralizada com borda
        # Fase centralizada com borda (no rodapé)
        fase_text = f"FASE {fase}"
        x_fase = config.SCREEN_WIDTH // 2 - len(fase_text)*2
        y_fase = config.SCREEN_HEIGHT + 12  # Ajuste a altura conforme o visual desejado
        pyxel.rectb(x_fase-4, y_fase-3, len(fase_text)*5+8, 12, config.HUD_BORDER_COLOR)
        pyxel.text(x_fase, y_fase, fase_text, config.HUD_PHASE_COLOR)
        
        # Exibir powerups ativos
        if powerups:
            px = 8
            pyxel.text(px, 16, "Power-ups:", config.POWERUP_LABEL_COLOR)
            for i, p in enumerate(powerups):
                pyxel.text(px + 70 + i*32, 16, p.obj.nome.upper(), config.POWERUP_ACTIVE_COLOR)
        
        # Instruções (opcional no início do jogo)
        if instrucoes:
            HUD._caixa_central("ESPAÇO para lançar bola\n←/→ para mover (modo jogador)\nESC para pausar", 3)
        
        # Pausa e game over
        if paused:
            HUD._caixa_central("PAUSADO\nPressione ESC para voltar", 12)
        if game_over:
            HUD._caixa_central("GAME OVER!\nPressione R para reiniciar", 8)
    
    @staticmethod
    def _draw_coracao(x, y, cor):
        # Coração em pixel art
        pyxel.pset(x+1, y, cor)
        pyxel.pset(x+2, y, cor)
        pyxel.pset(x, y+1, cor)
        pyxel.pset(x+3, y+1, cor)
        for i in range(4):
            pyxel.pset(x+i, y+2, cor)
        pyxel.pset(x+1, y+3, cor)
        pyxel.pset(x+2, y+3, cor)
        
    @staticmethod
    def _caixa_central(mensagem, cor):
        linhas = mensagem.split('\n')
        largura = max(len(l) for l in linhas) * 6 + 12
        altura = len(linhas) * 10 + 12
        x = config.SCREEN_WIDTH // 2 - largura // 2
        y = config.SCREEN_HEIGHT // 2 - altura // 2
        pyxel.rect(x, y, largura, altura, cor)
        pyxel.rectb(x, y, largura, altura, config.HUD_BORDER_COLOR)
        for i, l in enumerate(linhas):
            pyxel.text(x+8, y+8 + i*10, l, config.TEXT_COLOR)
