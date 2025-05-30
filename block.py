import pyxel
import config

class Block:
    def __init__(self, x, y, tipo="normal", tipo_powerup=None):
        self.x = x
        self.y = y
        self.width = config.BLOCK_WIDTH
        self.height = config.BLOCK_HEIGHT
        self.tipo = tipo  # "normal", "resistente", "powerup"
        self.destruido = False
        self.tipo_powerup = tipo_powerup

        if self.tipo == "resistente":
            self.vidas = 2
        else:
            self.vidas = 1

        self.tem_powerup = (self.tipo == "powerup")

    def levar_impacto(self):
        self.vidas -= 1
        if self.vidas <= 0:
            self.destruido = True
            # Retorna o tipo do power-up se este bloco tiver
            if self.tem_powerup:
                return self.tipo_powerup
        return None

    def levar_impacto(self):
        """Chamada quando a bola acerta o bloco."""
        self.vidas -= 1
        if self.vidas <= 0:
            self.destruido = True
            # Aqui você pode acionar um efeito ou gerar um power-up na game.py
            return self.tem_powerup
        return False

    def draw(self):
        if self.destruido:
            return
        # Escolha de cor pelo tipo e vida restante
        if self.tipo == "normal":
            cor = config.BLOCK_COLOR
        elif self.tipo == "resistente":
            cor = config.BLOCK_COLOR if self.vidas == 2 else config.BLOCK_COLOR_2
        elif self.tipo == "powerup":
            cor = config.BLOCK_POWERUP_COLOR
        else:
            cor = config.BLOCK_COLOR
        pyxel.rect(self.x, self.y, self.width, self.height, cor)
