# npc_rpg/core/config.py
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 160
TILE_SIZE = 8

# Cores (exemplo, você pode adicionar mais)
COLOR_PLAYER = 12
COLOR_SHOP_NPC = 8
COLOR_INFO_NPC = 7
COLOR_FORGE_NPC = 10
COLOR_WALL = 6
COLOR_FLOOR = 3
COLOR_WHITE = 7
COLOR_BLACK = 0
COLOR_DIALOG_BG = 1
COLOR_DIALOG_BORDER = 7
COLOR_GOLD_TEXT = 7
COLOR_INVENTORY_TEXT = 7


# 0 = chão, 1 = muro
MAP_DATA = [ 
    [1]*20,
] + [
    [1] + [0]*18 + [1] for _ in range(18)
] + [
    [1]*20,
]