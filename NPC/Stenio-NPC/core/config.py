# npc_rpg/core/config.py
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 240
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
    "pocao":  {"nome_exibicao": "Poção de Cura",    "preco_base": 10, "preco_desconto": 8,  "preco_venda_jogador_paga_npc": 10, "preco_npc_paga_jogador": 4, "tipo": "consumivel"},
    "espada": {
        "nome_exibicao": "Espada Curta",   
        "preco_base": 50, 
        "preco_desconto": 45, 
        "preco_venda_jogador_paga_npc": 50, 
        "tipo": "equipamento",
        "melhoravel": True,
        "custo_melhoria_ouro": 20,
        "custo_melhoria_material": {"ferro": 2}},
    "madeira":{"nome_exibicao": "Madeira",                                                 "preco_npc_paga_jogador": 10, "tipo": "material"},
    "ferro":  {"nome_exibicao": "Ferro",                                                   "preco_npc_paga_jogador": 15, "tipo": "material"},
    "tecido": {"nome_exibicao": "Tecido",                                                  "preco_npc_paga_jogador": 5, "tipo": "material"},
}

MAP_COLS = 38 
MAP_ROWS = 30 

MAP_DATA = [
    [1]*MAP_COLS, # Linha superior de muros
] + [
    [1] + [0]*(MAP_COLS - 2) + [1] for _ in range(MAP_ROWS - 2) # Linhas do meio com chão e muros laterais
] + [
    [1]*MAP_COLS, # Linha inferior de muros
]