# npc_rpg/core/map_utils.py
from .config import TILE_SIZE, MAP_DATA # Usando MAP_DATA daqui

def is_blocked(x, y, blocked_npc_positions): # Renomeado o parâmetro
    # Verifica colisão com paredes (baseado no grid)
    col = x // TILE_SIZE
    row = y // TILE_SIZE
    if not (0 <= row < len(MAP_DATA) and 0 <= col < len(MAP_DATA[0])):
        return True # Fora do mapa é bloqueado
    if MAP_DATA[row][col] == 1: # 1 é muro
        return True

    # Verifica colisão com NPCs
    # As posições dos NPCs são em pixels, TILE_SIZE é o tamanho deles
    player_rect = (x, y, TILE_SIZE, TILE_SIZE)
    for npc_x_pixel, npc_y_pixel in blocked_npc_positions: # Espera posições em pixels dos NPCs
        npc_rect = (npc_x_pixel, npc_y_pixel, TILE_SIZE, TILE_SIZE)
        if (player_rect[0] < npc_rect[0] + npc_rect[2] and
            player_rect[0] + player_rect[2] > npc_rect[0] and
            player_rect[1] < npc_rect[1] + npc_rect[3] and
            player_rect[1] + player_rect[3] > npc_rect[1]):
            return True
    return False

def is_near(player, npc_entity, distance=10): # Renomeado npc para npc_entity para clareza
    """
    Verifica se o jogador está próximo o suficiente do NPC para interagir.
    player e npc_entity devem ter atributos x, y.
    """
    dx = player.x - npc_entity.x
    dy = player.y - npc_entity.y
    return (dx * dx + dy * dy) <= (distance * distance)