import random
import config

class AutomatoAFD:
    def __init__(self, paddle, ball, blocks, powerups=None):
        self.paddle = paddle
        self.ball = ball
        self.blocks = blocks
        self.powerups = powerups if powerups else []
        self.estado = "esperando_lancamento"

    def decidir_acao(self, score, vidas):
        # 1. Game over
        if self.estado == "game_over":
            if vidas > 0:
                self.estado = "esperando_lancamento"
            return 0

        # 2. Prioridade: defender bola (só coleta power-up se não houver perigo)
        bola_descendo = self.ball.lancada and self.ball.dy > 0 and (self.ball.y < self.paddle.y)
        if self._tem_powerup() and not bola_descendo:
            self.estado = "coletando_powerup"
        elif self.estado == "coletando_powerup" and (not self._tem_powerup() or bola_descendo):
            self.estado = "rastreando_bola_lenta"

        # 3. Estado: coletando_powerup
        if self.estado == "coletando_powerup":
            if not self._tem_powerup():
                self.estado = "rastreando_bola_lenta"
                return 0
            return self._coletar_powerup()

        # 4. Esperando lançamento: centraliza paddle
        if self.estado == "esperando_lancamento":
            if self.ball.lancada:
                self.estado = "rastreando_bola_lenta"
            return self._centralizar()

        # 5. Rastreando bola lenta
        elif self.estado == "rastreando_bola_lenta":
            if self.ball.perdeu or vidas == 0:
                self.estado = "game_over"
                return 0
            if self.ball.dy <= 0:
                self.estado = "recuperando_centro"
                return self._centralizar()
            if abs(self.ball.dy) > 3:
                self.estado = "rastreando_bola_rapida"
                return 0
            return self._mover_para(self.prever_impacto_x(), speed=1)

        # 6. Rastreando bola rápida
        elif self.estado == "rastreando_bola_rapida":
            if self.ball.perdeu or vidas == 0:
                self.estado = "game_over"
                return 0
            if self.ball.dy <= 0:
                self.estado = "recuperando_centro"
                return self._centralizar()
            if abs(self.ball.dy) <= 3:
                self.estado = "rastreando_bola_lenta"
                return 0
            return self._mover_para(self.prever_impacto_x(), speed=2)

        # 7. Recuperando centro
        elif self.estado == "recuperando_centro":
            if self.ball.perdeu or vidas == 0:
                self.estado = "game_over"
                return 0
            if self.ball.dy > 0:
                self.estado = "rastreando_bola_lenta"
                return 0
            if self._esta_centralizado():
                return 0
            else:
                return self._centralizar()

        return 0

    # Métodos auxiliares
    def _clamp(self, valor, minimo, maximo):
        return max(min(valor, maximo), minimo)

    def _centralizar(self):
        centro = config.SCREEN_WIDTH // 2
        paddle_centro = self.paddle.x + self.paddle.width // 2
        LIMIAR = 8
        diff = centro - paddle_centro
        if abs(diff) > LIMIAR:
            return 1 if diff > 0 else -1
        return 0

    def _mover_para(self, alvo_x, speed=1):
        alvo_x = self._clamp(alvo_x, 0, config.SCREEN_WIDTH)
        paddle_centro = self.paddle.x + self.paddle.width // 2
        LIMIAR = 8
        diff = alvo_x - paddle_centro
        if abs(diff) > LIMIAR:
            return speed if diff > 0 else -speed
        return 0

    def _coletar_powerup(self):
        if not self.powerups:
            return 0
        # Vá até o centro do powerup ativo mais baixo
        pu = min(self.powerups, key=lambda p: p.y)
        alvo_x = pu.x + pu.width // 2
        return self._mover_para(alvo_x, speed=2)

    def _esta_centralizado(self):
        centro = config.SCREEN_WIDTH // 2
        paddle_centro = self.paddle.x + self.paddle.width // 2
        return abs(centro - paddle_centro) <= 8

    def _tem_powerup(self):
        return bool(self.powerups)

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
        return self._clamp(x, 0, config.SCREEN_WIDTH)


class AutomatoAFN:
    def __init__(self, paddle, ball, blocks, powerups=None):
        self.paddle = paddle
        self.ball = ball
        self.blocks = blocks
        self.powerups = powerups if powerups else []
        self.estado = "esperando_lancamento"

    def decidir_acao(self, score, vidas):
        # Estado: game_over
        if self.estado == "game_over":
            if vidas > 0 and random.random() < 0.96:
                self.estado = "esperando_lancamento"
            return 0

        # ----- DEFESA SEMPRE EM PRIMEIRO, MAS PODE FICAR TENTADO POR POWERUP -----
        bola_descendo = self.ball.lancada and self.ball.dy > 0 and (self.ball.y < self.paddle.y)
        if self._tem_powerup():
            # Se a bola está subindo, ou 20% de ousadia mesmo descendo:
            if not bola_descendo or random.random() < 0.2:
                self.estado = "coletando_powerup"
        elif self.estado == "coletando_powerup" and (not self._tem_powerup() or (bola_descendo and random.random() > 0.2)):
            self.estado = "rastreando_bola_lenta"

        # ----- Estado: coletando_powerup -----
        if self.estado == "coletando_powerup":
            if not self._tem_powerup():
                self.estado = "rastreando_bola_lenta"
                return 0
            # 10% de chance de andar meio errado:
            if random.random() < 0.1:
                return random.choice([-2, 0, 2])
            return self._coletar_powerup()

        # ----- Estado: esperando_lancamento -----
        if self.estado == "esperando_lancamento":
            if self.ball.lancada:
                self.estado = "rastreando_bola_lenta"
            # 7% de chance de hesitar/parar antes de centralizar:
            if random.random() < 0.07:
                return random.choice([-1, 0, 1])
            return self._centralizar()

        # ----- Estado: rastreando_bola_lenta -----
        elif self.estado == "rastreando_bola_lenta":
            if self.ball.perdeu or vidas == 0:
                self.estado = "game_over"
                return 0
            if self.ball.dy <= 0:
                self.estado = "recuperando_centro"
                return self._centralizar()
            if abs(self.ball.dy) > 3:
                self.estado = "rastreando_bola_rapida"
                return 0
            # 12% chance de hesitar:
            if random.random() < 0.12:
                return random.choice([-1, 0, 1])
            # Move para o impacto previsto, mas com ruído aleatório:
            alvo_x = self.prever_impacto_x() + random.randint(-8, 8)
            return self._mover_para(alvo_x, speed=1)

        # ----- Estado: rastreando_bola_rapida -----
        elif self.estado == "rastreando_bola_rapida":
            if self.ball.perdeu or vidas == 0:
                self.estado = "game_over"
                return 0
            if self.ball.dy <= 0:
                self.estado = "recuperando_centro"
                return self._centralizar()
            if abs(self.ball.dy) <= 3:
                self.estado = "rastreando_bola_lenta"
                return 0
            # 18% de erro/hesitação:
            if random.random() < 0.18:
                return random.choice([-2, 0, 2])
            alvo_x = self.prever_impacto_x() + random.randint(-16, 16)
            return self._mover_para(alvo_x, speed=2)

        # ----- Estado: recuperando_centro -----
        elif self.estado == "recuperando_centro":
            if self.ball.perdeu or vidas == 0:
                self.estado = "game_over"
                return 0
            if self.ball.dy > 0:
                self.estado = "rastreando_bola_lenta"
                return 0
            # 8% de chance de hesitar ou ficar parado:
            if self._esta_centralizado() or random.random() < 0.08:
                return 0
            else:
                if random.random() < 0.08:
                    return random.choice([-1, 0, 1])
                return self._centralizar()

        return 0

    # ---------- Métodos auxiliares ----------

    def _clamp(self, valor, minimo, maximo):
        return max(min(valor, maximo), minimo)

    def _centralizar(self):
        centro = config.SCREEN_WIDTH // 2
        paddle_centro = self.paddle.x + self.paddle.width // 2
        LIMIAR = 8
        diff = centro - paddle_centro
        if abs(diff) > LIMIAR:
            return 1 if diff > 0 else -1
        return 0

    def _mover_para(self, alvo_x, speed=1):
        alvo_x = self._clamp(alvo_x, 0, config.SCREEN_WIDTH)
        paddle_centro = self.paddle.x + self.paddle.width // 2
        LIMIAR = 8
        diff = alvo_x - paddle_centro
        if abs(diff) > LIMIAR:
            return speed if diff > 0 else -speed
        return 0

    def _coletar_powerup(self):
        if not self.powerups:
            return 0
        pu = min(self.powerups, key=lambda p: p.y)
        alvo_x = pu.x + pu.width // 2 + random.randint(-2, 2)  # com ruído leve
        return self._mover_para(alvo_x, speed=2)

    def _esta_centralizado(self):
        centro = config.SCREEN_WIDTH // 2
        paddle_centro = self.paddle.x + self.paddle.width // 2
        return abs(centro - paddle_centro) <= 8

    def _tem_powerup(self):
        return bool(self.powerups)

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
        return self._clamp(x, 0, config.SCREEN_WIDTH)