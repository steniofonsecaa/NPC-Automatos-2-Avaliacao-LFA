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

ITEM_DATA = {
    "pocao": {
        "nome_exibicao": "Poção de Cura", 
        "preco_base": 10, 
        "preco_desconto": 8,
        "tipo": "consumivel" # Você pode usar 'tipo' para outras lógicas no futuro
    },
    "espada": {
        "nome_exibicao": "Espada Curta", 
        "preco_base": 50, 
        "preco_desconto": 45, # Exemplo de preço com desconto para a espada
        "tipo": "equipamento"
    },
    # Adicione mais itens aqui se o vendedor for comercializá-los
}

# 0 = chão, 1 = muro
MAP_DATA = [ 
    [1]*20,
] + [
    [1] + [0]*18 + [1] for _ in range(18)
] + [
    [1]*20,
]