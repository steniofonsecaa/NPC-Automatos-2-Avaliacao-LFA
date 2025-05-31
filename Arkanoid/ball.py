import pyxel
import config

class Ball:
    def __init__(self, x, y, speed=2):
        self.x = x
        self.y = y
        self.radius = config.BALL_RADIUS
        self.dx = speed    # Velocidade inicial horizontal
        self.dy = -speed   # Velocidade inicial vertical (sobe)
        self.perdeu = False   # True se bola saiu da tela
        self.lancada = False  # Pode mudar para False se quiser paddle "lançar" a bola

    def update(self):
        if not self.lancada:
            return  # Bola fica "grudada" no paddle até lançamento

        self.x += self.dx
        self.y += self.dy

        # Colisão com paredes
        if self.x - self.radius <= 0 or self.x + self.radius >= config.SCREEN_WIDTH:
            self.dx *= -1

        if self.y - self.radius <= 0:
            self.dy *= -1

        # Caiu abaixo do paddle?
        if self.y - self.radius > config.SCREEN_HEIGHT:
            self.perdeu = True

    def reset(self, x, y):
        """Reposiciona a bola após perder vida"""
        self.x = x
        self.y = y
        self.dx = 2
        self.dy = -2
        self.perdeu = False
        self.lancada = False
        
    def check_collisions(self, paddle, blocks):
        # Colisão com o paddle
        if (
            paddle.x < self.x < paddle.x + paddle.width and
            paddle.y < self.y + self.radius < paddle.y + paddle.height
        ):
            self.dy *= -1
            # Opcional: Modifica dx baseado em onde bateu no paddle (efeito "spin")
            centro_paddle = paddle.x + paddle.width / 2
            dist = (self.x - centro_paddle) / (paddle.width / 2)
            self.dx += dist  # Mais longe do centro, mais "efeito"
            # Limita a velocidade máxima:
            self.dx = max(-4, min(self.dx, 4))

        # Colisão com blocos
        for block in blocks:
            if not block.destruido and block.x < self.x < block.x + block.width and block.y < self.y < block.y + block.height:
                self.dy *= -1
                block.destruido = True
                break

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, config.BALL_COLOR)
