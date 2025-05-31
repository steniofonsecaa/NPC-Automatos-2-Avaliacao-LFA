import pyxel
import config
from paddle import Paddle
from ball import Ball
from block import Block
from hud import HUD
import random
from automato import AutomatoAFD, AutomatoAFN
from collections import namedtuple
# ---- NOVO: Classe PowerUpAtivo ----# Classe mutável para PowerUp ativo na HUD
class PowerUpAtivo:
    def __init__(self, obj, frames):
        self.obj = obj
        self.frames = frames
# ---- NOVO: Classe PowerUp ----
class PowerUp:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        tipos_pu = ["expand_paddle", "extra_life", "slow_motion", "multiball"]
        self.tipo = tipo
        self.nome = tipo
        self.width = 8
        self.height = 8
        self.vy = 1  # Velocidade de descida
        self.coletado = False

    def update(self):
        self.y += self.vy

    def draw(self):
        cor = {
            "expand_paddle": 10,
            "extra_life": 11,
            "slow_motion": 12,
            "multiball": 8,
        }[self.tipo]
        pyxel.rect(self.x, self.y, self.width, self.height, cor)
        pyxel.text(self.x+1, self.y+2, self.tipo[0].upper(), 7)

    def colide_com_paddle(self, paddle):
        return (self.x + self.width > paddle.x and
                self.x < paddle.x + paddle.width and
                self.y + self.height > paddle.y and
                self.y < paddle.y + paddle.height)
# ---- GAME ----

class Game:
    def __init__(self):
        pyxel.init(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        pyxel.title = "Arkanoid IA/AFN"
        self.menu = True
        self.afn_mode = False
        self.high_score = 0
        self.modo_jogador = False  # Começa no modo IA
        self.reset_game()
        self.powerups_ativos = []  # Agora irá guardar objetos PowerUpAtivo
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.score = 0
        self.lives = config.START_LIVES
        self.fase = 1
        self.paused = False
        self.game_over = False
        self.exibir_instrucoes = True
        self.powerups_caindo = []
        self.powerups_ativos = []
        self.init_board()
        self.automato.centralizado = False

    def init_board(self):
        tipos_pu = ["expand_paddle", "extra_life", "slow_motion", "multiball"]
        self.blocks = []
        # Paddle centralizado
        self.paddle = Paddle(
            config.SCREEN_WIDTH // 2 - config.PADDLE_WIDTH // 2,
            config.PADDLE_Y
        )
        # Bola sobre o paddle
        self.ball = Ball(
            self.paddle.x + self.paddle.width // 2,
            self.paddle.y - config.BALL_RADIUS - 1
        )
        self.ball.lancada = False

        # Blocos (alguns com power-ups aleatórios)
        tipos_pu = ["expand_paddle", "extra_life", "slow_motion", "multiball"]
        self.blocks = []
        for row in range(config.BLOCK_ROWS):
            for col in range(config.BLOCK_COLS):
                x = col * config.BLOCK_WIDTH + 4
                y = 24 + row * config.BLOCK_HEIGHT
                if (row + col) % 8 == 0:
                    tipo = "powerup"
                elif (row + col) % 4 == 0:
                    tipo = "resistente"
                else:
                    tipo = "normal"
                block = Block(x, y, tipo=tipo)
                if tipo == "powerup":
                    block.tipo_powerup = random.choice(tipos_pu)
                else:
                    block.tipo_powerup = None
                self.blocks.append(block)

        # IA escolhida pelo usuário
        if self.afn_mode:
            self.automato = AutomatoAFN(self.paddle, self.ball, self.blocks)
        else:
            self.automato = AutomatoAFD(self.paddle, self.ball, self.blocks)

    def update(self):
        if pyxel.btnp(pyxel.KEY_TAB):
            self.modo_jogador = not self.modo_jogador  # Alterna IA/jogador ao pressionar TAB
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if self.menu:
            if pyxel.btnp(pyxel.KEY_1):
                self.afn_mode = False
                self.menu = False
            if pyxel.btnp(pyxel.KEY_2):
                self.afn_mode = True
                self.menu = False
            return
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.high_score = max(self.high_score, self.score)
                self.reset_game()
            return
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.paused = not self.paused
            return
        if self.paused:
            return
        # Sempre permite lançar a bola, independente do modo
        if not self.ball.lancada and pyxel.btnp(pyxel.KEY_SPACE):
            self.ball.lancada = True
            self.exibir_instrucoes = False
        # Lançamento da bola
        if self.modo_jogador:
            movimento = 0
            if pyxel.btn(pyxel.KEY_LEFT):
                movimento = -1
            elif pyxel.btn(pyxel.KEY_RIGHT):
                movimento = 1
        else:
            movimento = self.automato.decidir_acao(self.score, self.lives)
        self.paddle.update(movimento)

        self.ball.update()

        # Power-ups caindo
        for pu in self.powerups_caindo:
            pu.update()
            if pu.colide_com_paddle(self.paddle):
                self.aplicar_powerup(pu.tipo)
                pu.coletado = True

        self.powerups_caindo = [
        p for p in self.powerups_caindo if not p.coletado and p.y < config.SCREEN_HEIGHT
        ]
        # Atualiza power-ups ativos
        for pu in self.powerups_ativos:
            pu.frames -= 1
        self.powerups_ativos = [
            pu for pu in self.powerups_ativos if pu.frames > 0
        ]

        # Colisões e blocos
        self.ball.check_collisions(self.paddle, self.blocks)
        for block in self.blocks:
            if block.destruido and not hasattr(block, "contabilizado"):
                block.contabilizado = True
                self.score += config.POINTS_PER_BLOCK
                if block.tem_powerup and block.tipo_powerup:
                    self.powerups_caindo.append(PowerUp(
                        block.x + block.width//2 - 4, block.y + block.height//2 - 4, block.tipo_powerup))

        # Vida perdida?
        if self.ball.perdeu:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.high_score = max(self.high_score, self.score)
            else:
                self.ball.reset(
                    self.paddle.x + self.paddle.width // 2,
                    self.paddle.y - config.BALL_RADIUS - 1
                )
                self.ball.lancada = False
                self.exibir_instrucoes = True

        # Todos blocos destruídos? Próxima fase!
        if all(b.destruido for b in self.blocks):
            self.fase += 1
            self.init_board()

    def aplicar_powerup(self, tipo):
        # Aplica os efeitos dos powerups
        if tipo == "expand_paddle":
            self.paddle.width = min(self.paddle.width + 16, config.SCREEN_WIDTH // 2)
            self.powerups_ativos.append(PowerUpAtivo(PowerUp(4, 32, "expand_paddle"), 120))  # 120 frames = 2 segundos

        elif tipo == "extra_life":
            self.lives += 1
            self.powerups_ativos.append(PowerUpAtivo(PowerUp(20, 32, "extra_life"), 120))
        elif tipo == "slow_motion":
            self.ball.dx = self.ball.dx * 0.6
            self.ball.dy = self.ball.dy * 0.6
            self.powerups_ativos.append(PowerUpAtivo(PowerUp(36, 32, "slow_motion"), 120))
        elif tipo == "multiball":
            # Exemplo simples: só aumenta score e mostra ativo
            self.score += 30
            self.powerups_ativos.append(PowerUpAtivo(PowerUp(52, 32, "multiball"), 120))

    def draw(self):
        pyxel.cls(config.COR_FUNDO)
        if self.menu:
            pyxel.rect(14, 40, config.SCREEN_WIDTH-28, 60, 1)
            pyxel.rectb(14, 40, config.SCREEN_WIDTH-28, 60, 10)
            pyxel.text(config.SCREEN_WIDTH//2-32, 50, "ARKANOID IA", 7)
            pyxel.text(config.SCREEN_WIDTH//2-56, 66, "1 = IA Determinística (AFD)", 10)
            pyxel.text(config.SCREEN_WIDTH//2-56, 76, "2 = IA Não Determinística (AFN)", 8)
            pyxel.text(config.SCREEN_WIDTH//2-42, 92, "Escolha o modo para iniciar", 7)
            return

        for block in self.blocks:
            block.draw()
        self.paddle.draw()
        self.ball.draw()
        for pu in self.powerups_caindo:
            pu.draw()
        self.powerups_ativos = [
                                 PowerUpAtivo(pu.obj, pu.frames - 1) for pu in self.powerups_ativos if pu.frames > 1
                                ]   
        HUD.draw(
            score=self.score,
            vidas=self.lives,
            fase=self.fase,
            game_over=self.game_over,
            paused=self.paused,
            powerups=[p for p in self.powerups_ativos],
            instrucoes=self.exibir_instrucoes,
            high_score=self.high_score
        )
        modo_texto = "Jogador" if self.modo_jogador else "IA"
        pyxel.text(8, config.SCREEN_HEIGHT - 12, f"Modo: {modo_texto} (Tab para alternar)", 7)  

if __name__ == "__main__":
    Game()
