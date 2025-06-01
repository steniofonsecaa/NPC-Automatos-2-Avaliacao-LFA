# npc_rpg/entities/npc_informante.py
from .npc_base import NPCBase
from core.config import COLOR_INFO_NPC # Supondo que você defina esta cor

# Futuramente, importe o autômato do informante:
# from automata.info_npc_automaton import INFO_NPC_AUTOMATON 

class NPCInformante(NPCBase):
    def __init__(self, x, y, label="I"):
        super().__init__(x, y, npc_type="info", label=label, color=COLOR_INFO_NPC)
        # self.automaton = INFO_NPC_AUTOMATON # Quando o autômato existir
        # Por enquanto, ele não terá um autômato complexo e usará a lógica base
        # ou uma interação simples definida no Game.py