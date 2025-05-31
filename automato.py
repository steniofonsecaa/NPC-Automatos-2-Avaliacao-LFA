import random
import config

class AutomatoAFD:
    def __init__(self, paddle, ball, blocks, powerups=None):
        self.paddle = paddle
        self.ball = ball
        self.blocks = blocks
        self.powerups = powerups if powerups else []
        self.estado = "esperando_lancamento"
        self.centralizado = False

    def decidir_acao(self, score, vidas):
        # ESTADO 1: Esperando lançamento (paddle vai para o centro)
        if self.estado == "esperando_lancamento":
            if self.ball.lancada:
                self.estado = "rastreando_bola"
            centro = config.SCREEN_WIDTH // 2
            paddle_centro = self.paddle.x + self.paddle.width // 2
            LIMIAR = 6
            diff = centro - paddle_centro
            if abs(diff) > LIMIAR:
                return 1 if diff > 0 else -1
            else:
                return 0

        # ESTADO 2: Rastreando bola (paddle tenta ir para o ponto de impacto previsto)
        elif self.estado == "rastreando_bola":
            if self.ball.perdeu:
                self.estado = "esperando_lancamento"
                return 0
            destino_x = self.prever_impacto_x()
            paddle_centro = self.paddle.x + self.paddle.width // 2
            LIMIAR = 6
            diff = destino_x - paddle_centro
            if abs(diff) > LIMIAR:
                return 2 if diff > 0 else -2  # Move mais rápido
            else:
                return 0

        # fallback (deve ser raro)
        return 0

    def prever_impacto_x(self):
        x, y = self.ball.x, self.ball.y
        dx, dy = self.ball.dx, self.ball.dy
        max_iter = 1000  # Limite de segurança
        iters = 0
        if dy <= 0:
            return self.paddle.x + self.paddle.width // 2
        while y < self.paddle.y and iters < max_iter:
            x += dx
            y += dy
            if x - self.ball.radius <= 0 or x + self.ball.radius >= config.SCREEN_WIDTH:
                dx *= -1
            iters += 1
        return x


class AutomatoAFN:
    def __init__(self, paddle, ball, blocks, powerups=None):
        self.paddle = paddle
        self.ball = ball
        self.blocks = blocks
        self.powerups = powerups if powerups else []
        self.estado = "esperando_lancamento"
        self.centralizado = False

    def decidir_acao(self, score, vidas):
        # AFN: Transições probabilísticas nos estados

        # ESTADO 1: Esperando lançamento (vai para o centro)
        if self.estado == "esperando_lancamento":
            if self.ball.lancada:
                # 50% de ir para rastrear, 50% de continuar centralizando
                self.estado = "rastreando_bola" if random.random() < 0.5 else "esperando_lancamento"
            centro = config.SCREEN_WIDTH // 2
            paddle_centro = self.paddle.x + self.paddle.width // 2
            LIMIAR = 6
            diff = centro - paddle_centro
            if abs(diff) > LIMIAR:
                return 1 if diff > 0 else -1
            else:
                return 0

        # ESTADO 2: Rastreando bola (paddle tenta ir para o ponto de impacto previsto, mas pode "se distrair")
        elif self.estado == "rastreando_bola":
            # 10% de chance de ir para estado "esperando_lancamento" (simula erro ou distração)
            if random.random() < 0.1 or self.ball.perdeu:
                self.estado = "esperando_lancamento"
                return 0
            destino_x = self.prever_impacto_x()
            paddle_centro = self.paddle.x + self.paddle.width // 2
            LIMIAR = 6
            diff = destino_x - paddle_centro
            if abs(diff) > LIMIAR:
                return 2 if diff > 0 else -2
            else:
                return 0

        # fallback
        return 0

    def prever_impacto_x(self):
        x, y = self.ball.x, self.ball.y
        dx, dy = self.ball.dx, self.ball.dy
        max_iter = 1000
        iters = 0
        if dy <= 0:
            return self.paddle.x + self.paddle.width // 2
        while y < self.paddle.y and iters < max_iter:
            x += dx
            y += dy
            if x - self.ball.radius <= 0 or x + self.ball.radius >= config.SCREEN_WIDTH:
                dx *= -1
            iters += 1
        return x