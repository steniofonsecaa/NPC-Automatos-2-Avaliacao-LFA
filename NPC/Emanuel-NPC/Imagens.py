import pyxel
class ImagensNPC:
    def __init__(self):
        pyxel.load("my_resource.pyxres")  # Carrega o pyxres no início

    def get_retrato(self, npc_type):
        if npc_type == "shop":
            return  {"banco": 0, "u": 0, "v": 0, "w": 24, "h": 24}
        elif npc_type == "forge":
            return {"banco": 0, "u": 32, "v": 0, "w": 24, "h": 24}
        elif npc_type == "info":
            return {"banco": 0, "u": 0, "v": 64, "w": 24, "h": 24}
        else:
            return {"banco": 0, "u": 0, "v": 32, "w": 24, "h": 24}
