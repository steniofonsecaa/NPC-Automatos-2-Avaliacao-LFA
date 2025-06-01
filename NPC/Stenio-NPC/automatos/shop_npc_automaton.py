# npc_rpg/automata/shop_npc_automaton.py
SHOP_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Ola! Bem-vindo, viajante. O que você deseja:",
        "options": {"1": "Comprar", "2": "Vender", "3": "Sair"},
        "transitions": {"1": "MENU_COMPRA", "2": "MENU_VENDA", "3": "FIM"}
    },
    "MENU_COMPRA": {
        "message": "Comprar: [1] Pocao (10g), [2] Espada (50g), [3] Voltar.",
        "options": {"1": "Poção", "2": "Espada", "3": "Voltar"},
        "transitions": {"1": "POCAO_COMPRADA", "2": "ESPADA_COMPRADA", "3": "INICIAL"}
    },
    "MENU_VENDA": {
        "message": "Vender ainda nao implementado. [1] Voltar.",
        "options": {"1": "Voltar"},
        "transitions": {"1": "INICIAL"}
    },
    "POCAO_COMPRADA": {
        "message": "Voce comprou uma Pocao! (10g). [1] Continuar.",
        "options": {"1": "Continuar"},
        "transitions": {"1": "MENU_COMPRA"}
    },
    "ESPADA_COMPRADA": {
        "message": "Voce comprou uma Espada! (50g). [1] Continuar.",
        "options": {"1": "Continuar"},
        "transitions": {"1": "MENU_COMPRA"}
    },
    "FIM": {
        "message": "Ate logo!",
        "options": {},
        "transitions": {}
    }
}