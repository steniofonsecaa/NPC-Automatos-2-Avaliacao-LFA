import random
import config

class AutomatoIA:
    def __init__(self, paddle, ball, blocks, powerups=None):
        self.paddle = paddle
        self.ball = ball
        self.centralizado = False
        self.blocks = blocks
        self.powerups = powerups if powerups else []
        self.estado = "esperando_lancamento"
        self.delay_counter = 0
        self.nivel_erro = 0.1  # probabilidade de erro (10%)
        self.vidas_baixas = False

    def decidir_acao(self, score, vidas):
        # Comportamento humano: aumenta erro com menos vidas
        if vidas <= 1:
            self.nivel_erro = 0.02  # mais conservador (2% de erro)
            self.vidas_baixas = True
        else:
            self.nivel_erro = 0.1
            self.vidas_baixas = False

        # Se poucos blocos, IA fica agressiva (menos delay, menos erro)
        if sum(not b.destruido for b in self.blocks) <= 5:
            self.nivel_erro = 0.01

        # Se há powerup caindo, prioriza buscar
        if self.powerups:
            alvo_x = self.powerups[0].x
            return self._mover_para(alvo_x, speed=2)

        # Delay de reação (comportamento humano)
        if self.delay_counter > 0:
            self.delay_counter -= 1
            return 0

        # Lógica de estados
        if self.estado == "esperando_lancamento":
            if self.ball.lancada:
                self.estado = "rastreando_lenta"
            centro = config.SCREEN_WIDTH // 2
            paddle_centro = self.paddle.x + self.paddle.width // 2

            # Se ainda não centralizou, mova até centralizar
            if not self.centralizado:
                if abs(paddle_centro - centro) > 2:
                    return 1 if paddle_centro < centro else -1
                else:
                    self.centralizado = True
                    return 0
            else:
                return 0  # Já centralizou, fica parado

        elif self.estado == "rastreando_lenta":
            if abs(self.ball.dy) > 3:
                self.estado = "rastreando_rapida"
            elif abs(self.ball.y - self.paddle.y) < 24:
                self.estado = "ajustando_fino"
            # Se a bola sumiu ou perdeu vida
            if self.ball.perdeu:
                self.estado = "esperando_lancamento"
                return self._centralizar()
            # Se bloco logo acima do paddle, desvia
            if self._bloco_acima():
                self.estado = "desviando_de_bloco"
                return self._desviar_bloco()
            return self._prever_impacto()

        elif self.estado == "rastreando_rapida":
            if abs(self.ball.dy) <= 3:
                self.estado = "rastreando_lenta"
            elif abs(self.ball.y - self.paddle.y) < 24:
                self.estado = "ajustando_fino"
            if self.ball.perdeu:
                self.estado = "esperando_lancamento"
                return self._centralizar()
            return self._prever_impacto(speed=2)  # acelera

        elif self.estado == "ajustando_fino":
            if abs(self.ball.y - self.paddle.y) >= 24:
                self.estado = "rastreando_lenta"
            if self.ball.perdeu:
                self.estado = "esperando_lancamento"
                return self._centralizar()
            return self._prever_impacto(speed=1, fino=True)  # micro-ajustes

        elif self.estado == "desviando_de_bloco":
            # Se já desviou ou bloco sumiu, volta para rastreamento
            if not self._bloco_acima():
                self.estado = "rastreando_lenta"
                return self._prever_impacto()
            return self._desviar_bloco()

        elif self.estado == "recuperando_centro":
            if abs(self.paddle.x + self.paddle.width // 2 - config.SCREEN_WIDTH // 2) < 4:
                self.estado = "rastreando_lenta"
                return 0
            return self._centralizar()

        else:
            # fallback seguro
            return self._centralizar()

    # -------- Métodos auxiliares para cada comportamento --------
    def _centralizar(self):
        centro = config.SCREEN_WIDTH // 2
        paddle_centro = self.paddle.x + self.paddle.width // 2
        if paddle_centro < centro - 2:
            return 1
        elif paddle_centro > centro + 2:
            return -1
        else:
            return 0

    def _prever_impacto(self, speed=1, fino=False):
        """Prevê onde a bola vai atingir o paddle e move para lá."""
        destino_x = self.prever_impacto_x()
        paddle_centro = self.paddle.x + self.paddle.width // 2

        # Comportamento humano: chance de erro
        if random.random() < self.nivel_erro:
            destino_x += random.randint(-16, 16)  # erra intencionalmente

        # Ajuste fino
        passo = 1 if fino else speed

        if paddle_centro < destino_x - 2:
            return passo
        elif paddle_centro > destino_x + 2:
            return -passo
        else:
            return 0

    def prever_impacto_x(self):
        """Simula a trajetória da bola até a linha do paddle."""
        x, y = self.ball.x, self.ball.y
        dx, dy = self.ball.dx, self.ball.dy
        while y < self.paddle.y:
            x += dx
            y += dy
            if x - self.ball.radius <= 0 or x + self.ball.radius >= config.SCREEN_WIDTH:
                dx *= -1
        return x

    def _desviar_bloco(self):
        # Move para a direção oposta ao bloco imediatamente acima do paddle
        for b in self.blocks:
            if not b.destruido and abs((b.x + b.width // 2) - (self.paddle.x + self.paddle.width // 2)) < b.width:
                if b.x + b.width // 2 < self.paddle.x + self.paddle.width // 2:
                    return 1
                else:
                    return -1
        return 0

    def _bloco_acima(self):
        """Verifica se existe bloco logo acima do paddle."""
        for b in self.blocks:
            if not b.destruido and \
               b.y + b.height < self.paddle.y and \
               abs((b.x + b.width // 2) - (self.paddle.x + self.paddle.width // 2)) < b.width:
                return True
        return False

    def _mover_para(self, alvo_x, speed=1):
        paddle_centro = self.paddle.x + self.paddle.width // 2
        if paddle_centro < alvo_x - 2:
            return speed
        elif paddle_centro > alvo_x + 2:
            return -speed
        else:
            return 0
        


class AutomatoAFN:
    def __init__(self, paddle, ball, blocks, powerups=None):
        self.paddle = paddle
        self.ball = ball
        self.centralizado = False
        self.blocks = blocks
        self.powerups = powerups if powerups else []
        self.estado = "esperando_lancamento"
        self.delay_counter = 0
        self.nivel_erro = 0.12  # Um pouco maior que AFD
        self.vidas_baixas = False

    def decidir_acao(self, score, vidas):
        # Comportamento humano: aumenta erro com menos vidas
        if vidas <= 1:
            self.nivel_erro = 0.04  # mais conservador (4% de erro)
            self.vidas_baixas = True
        else:
            self.nivel_erro = 0.12
            self.vidas_baixas = False

        # Se poucos blocos, IA fica agressiva (menos delay, menos erro)
        if sum(not b.destruido for b in self.blocks) <= 5:
            self.nivel_erro = 0.02

        # Se há powerup caindo, pode escolher entre ir ou ignorar
        if self.powerups and random.random() < 0.7:  # 70% chance de priorizar
            alvo_x = self.powerups[0].x
            return self._mover_para(alvo_x, speed=2)

        # Delay de reação (comportamento humano)
        if self.delay_counter > 0:
            self.delay_counter -= 1
            return 0

        # --- Lógica de Estados Não Determinística ---
        if self.estado == "esperando_lancamento":
            if self.ball.lancada:
                # 80% de ir para "centralizando", 20% para "rastreando_bola_lenta" direto
                if random.random() < 0.6:
                    self.estado = "centralizando"
                else:
                    self.estado = "rastreando_bola_lenta"
            return self._centralizar()

        elif self.estado == "centralizando":
            # 85% chance de reconhecer centralização, 15% continua centralizando
            if abs(self.paddle.x + self.paddle.width // 2 - config.SCREEN_WIDTH // 2) < 4:
                if random.random() < 0.85:
                    self.estado = "rastreando_bola_lenta"
            return self._centralizar()

        elif self.estado == "rastreando_bola_lenta":
            # Não determinístico: 60% de ir para bola rápida se velocidade alta, 40% permanece
            if abs(self.ball.dy) > 3 and random.random() < 0.6:
                self.estado = "rastreando_bola_rapida"
            # 50% de ir para ajuste fino se bola perto, 50% fica
            elif abs(self.ball.y - self.paddle.y) < 24 and random.random() < 0.5:
                self.estado = "ajustando_posicao_fina"
            # Se perdeu vida, sempre vai para Game Over
            if self.ball.perdeu:
                self.estado = "game_over"
                return 0
            # 30% de tentar desviar de bloco, 70% ignora
            if self._bloco_acima() and random.random() < 0.3:
                self.estado = "desviando_de_bloco"
                return self._desviar_bloco()
            return self._prever_impacto()

        elif self.estado == "rastreando_bola_rapida":
            # 60% de voltar para lenta se velocidade caiu, 40% permanece
            if abs(self.ball.dy) <= 3 and random.random() < 0.6:
                self.estado = "rastreando_bola_lenta"
            # 60% ir para ajuste fino se perto, 40% fica
            elif abs(self.ball.y - self.paddle.y) < 24 and random.random() < 0.6:
                self.estado = "ajustando_posicao_fina"
            if self.ball.perdeu:
                self.estado = "game_over"
                return 0
            return self._prever_impacto(speed=2)

        elif self.estado == "ajustando_posicao_fina":
            # 70% de sair para rastreamento se bola afastou, 30% permanece
            if abs(self.ball.y - self.paddle.y) >= 24 and random.random() < 0.7:
                self.estado = "rastreando_bola_lenta"
            if self.ball.perdeu:
                self.estado = "game_over"
                return 0
            return self._prever_impacto(speed=1, fino=True)

        elif self.estado == "desviando_de_bloco":
            # 80% de voltar ao rastreamento se já desviou/bloco sumiu
            if not self._bloco_acima() and random.random() < 0.8:
                self.estado = "rastreando_bola_lenta"
                return self._prever_impacto()
            return self._desviar_bloco()

        elif self.estado == "game_over":
            # Só volta ao início se reiniciar, ou permanece aqui
            return 0

        else:
            return self._centralizar()

    # -------- Métodos auxiliares são idênticos ao AFD, mas usados pelo AFN --------
    def _centralizar(self):
        centro = config.SCREEN_WIDTH // 2
        paddle_centro = self.paddle.x + self.paddle.width // 2
        if paddle_centro < centro - 8:
            return 1
        elif paddle_centro > centro + 8:
            return -1
        else:
            return 0

    def _prever_impacto(self, speed=1, fino=False):
        destino_x = self.prever_impacto_x()
        paddle_centro = self.paddle.x + self.paddle.width // 2

        # Erro intencional mais alto
        if random.random() < self.nivel_erro:
            destino_x += random.randint(-20, 20)  # erro intencional maior

        passo = 1 if fino else speed
        if paddle_centro < destino_x - 8:
            return passo
        elif paddle_centro > destino_x + 8:
            return -passo
        else:
            return 0

    def prever_impacto_x(self):
        x, y = self.ball.x, self.ball.y
        dx, dy = self.ball.dx, self.ball.dy
        while y < self.paddle.y:
            x += dx
            y += dy
            if x - self.ball.radius <= 0 or x + self.ball.radius >= config.SCREEN_WIDTH:
                dx *= -1
        return x

    def _desviar_bloco(self):
        for b in self.blocks:
            if not b.destruido and abs((b.x + b.width // 2) - (self.paddle.x + self.paddle.width // 2)) < b.width:
                if b.x + b.width // 2 < self.paddle.x + self.paddle.width // 2:
                    return 1
                else:
                    return -1
        return 0

    def _bloco_acima(self):
        for b in self.blocks:
            if not b.destruido and \
               b.y + b.height < self.paddle.y and \
               abs((b.x + b.width // 2) - (self.paddle.x + self.paddle.width // 2)) < b.width:
                return True
        return False

    def _mover_para(self, alvo_x, speed=1):
        paddle_centro = self.paddle.x + self.paddle.width // 2
        if paddle_centro < alvo_x - 8:
            return speed
        elif paddle_centro > alvo_x + 8:
            return -speed
        else:
            return 0
