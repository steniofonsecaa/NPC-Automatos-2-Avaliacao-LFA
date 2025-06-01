# npc_rpg/entities/npc_vendedor.py
from .npc_base import NPCBase
from automatos.shop_npc_automaton import SHOP_NPC_AUTOMATON
from core.config import COLOR_SHOP_NPC # Importa a cor específica

class NPCVendedor(NPCBase):
    def __init__(self, x, y, label="L"):
        super().__init__(x, y, npc_type="shop", label=label, color=COLOR_SHOP_NPC)
        self.automaton = SHOP_NPC_AUTOMATON
        # A lógica de process_player_choice para transações já está na base,
        # mas poderia ser sobrescrita aqui para comportamento mais específico do vendedor se necessário.