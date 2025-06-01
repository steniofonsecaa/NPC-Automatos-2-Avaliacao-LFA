# npc_rpg/entities/player.py
import pyxel
import random
from core.config import TILE_SIZE, COLOR_PLAYER
from core.map_utils import is_blocked # Importa a função

class Player:
    def __init__(self, start_x=40, start_y=40):
        self.x = start_x
        self.y = start_y
        self.color = COLOR_PLAYER
        
        self.gold = random.randint(200, 500)
        self.inventory = {
            "madeira": random.randint(0, 10),
            "ferro": random.randint(0, 5),
            "tecido": random.randint(0, 9),
            "pocao": random.randint(0, 5),
            "espada": 0
        }

    def update(self, blocked_npc_pixel_positions): # Parâmetro atualizado
        dx = dy = 0
        if pyxel.btn(pyxel.KEY_LEFT): dx = -1
        if pyxel.btn(pyxel.KEY_RIGHT): dx = 1
        if pyxel.btn(pyxel.KEY_UP): dy = -1
        if pyxel.btn(pyxel.KEY_DOWN): dy = 1

        new_x = self.x + dx
        new_y = self.y + dy

        if not is_blocked(new_x, self.y, blocked_npc_pixel_positions):
            self.x = new_x
        if not is_blocked(self.x, new_y, blocked_npc_pixel_positions):
            self.y = new_y

    def draw(self):
        pyxel.rect(self.x, self.y, TILE_SIZE, TILE_SIZE, self.color)