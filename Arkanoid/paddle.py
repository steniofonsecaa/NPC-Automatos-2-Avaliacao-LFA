import pyxel
import config

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = config.PADDLE_WIDTH
        self.height = config.PADDLE_HEIGHT
        self.speed = 3

    def update(self, movimento):
        """
        Atualiza a posição da barra com base em um comando de movimento.
        movimento < 0: move para a esquerda
        movimento > 0: move para a direita
        movimento == 0: permanece parada
        """
        self.x += movimento * self.speed
        # Garante que a barra não saia da tela
        self.x = max(0, min(self.x, config.SCREEN_WIDTH - self.width))

    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, config.PADDLE_COLOR)
