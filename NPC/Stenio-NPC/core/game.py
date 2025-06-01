# npc_rpg/core/game.py
import pyxel
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MAP_DATA, COLOR_WALL, COLOR_FLOOR, COLOR_GOLD_TEXT, COLOR_INVENTORY_TEXT, COLOR_DIALOG_BG, COLOR_DIALOG_BORDER
from .map_utils import is_near # is_blocked é usado pelo Player
from entidades.player import Player

COLOR_BLACK = 0  # Adiciona definição para preto (Pyxel: 0)
COLOR_WHITE = 7  # Adiciona definição para branco (Pyxel: 7)
# Importe as classes de NPC específicas
from entidades.npc_vendedor import NPCVendedor
from entidades.npc_informante import NPCInformante # Exemplo
# from entities.npc_ferreiro import NPCFerreiro # Exemplo
from entidades.npc_base import NPCBase  # Adiciona importação do NPCBase

class Game:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Meu RPG com NPCs")
        self.player = Player(start_x=SCREEN_WIDTH // 2, start_y=SCREEN_HEIGHT // 2)
        
        # Instanciando os NPCs específicos
        self.npcs = [
            NPCVendedor(TILE_SIZE * 3, TILE_SIZE * 3),        # (x=24, y=24)
            NPCInformante(SCREEN_WIDTH - TILE_SIZE * 4, TILE_SIZE * 3, label="I"), # (x=128, y=24)
            # NPCFerreiro(TILE_SIZE * 3, SCREEN_HEIGHT - TILE_SIZE * 4, label="F"), # Exemplo
            # Temporariamente, um NPC genérico para o ferreiro se a classe não existir:
            NPCBase(TILE_SIZE * 3, SCREEN_HEIGHT - TILE_SIZE * 4, npc_type="forge", label="F", color=10) 
        ]
        
        self.active_npc_interaction = None
        self.show_inventory_ui = False
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_M):
            self.show_inventory_ui = not self.show_inventory_ui
            # Se abriu o inventário, e estava em diálogo, encerra o diálogo
            if self.show_inventory_ui and self.active_npc_interaction:
                self.active_npc_interaction.end_dialogue()
                self.active_npc_interaction = None


        if self.show_inventory_ui:
            return 

        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # Modo de Diálogo
            npc = self.active_npc_interaction
            if pyxel.btnp(pyxel.KEY_1):
                npc.process_player_choice("1")
            elif pyxel.btnp(pyxel.KEY_2):
                npc.process_player_choice("2")
            elif pyxel.btnp(pyxel.KEY_3):
                npc.process_player_choice("3")
            # Adicione mais teclas se necessário (4, 5, etc.)

            # Verifica se o diálogo terminou (chegou ao estado "FIM")
            if npc.dialogue_state == "FIM":
                # Permite fechar a janela de diálogo final pressionando uma tecla de ação
                if pyxel.btnp(pyxel.KEY_1) or pyxel.btnp(pyxel.KEY_2) or pyxel.btnp(pyxel.KEY_3) or pyxel.btnp(pyxel.KEY_E) or pyxel.btnp(pyxel.KEY_Q):
                    npc.end_dialogue()
                    self.active_npc_interaction = None
        else:
            # Modo de Exploração
            # Passa as posições em PIXELS dos NPCs para a checagem de colisão do jogador
            blocked_npc_pixel_positions = [npc.get_pixel_pos() for npc in self.npcs]
            self.player.update(blocked_npc_pixel_positions)

            # Verifica interação com NPCs
            current_near_npc = None
            for npc_entity in self.npcs:
                if is_near(self.player, npc_entity, distance=TILE_SIZE * 1.5): # Aumenta um pouco a distância
                    current_near_npc = npc_entity
                    break
            
            if current_near_npc and pyxel.btnp(pyxel.KEY_E):
                # Inicia o diálogo se o NPC tiver um autômato, ou faz uma ação padrão
                self.active_npc_interaction = current_near_npc
                if not self.active_npc_interaction.start_dialogue(self.player):
                    # Se start_dialogue falhar (ex: sem autômato), limpa a interação
                    print(f"NPC {current_near_npc.type} ({current_near_npc.label}) nao iniciou dialogo complexo.")
                    # Poderia ter uma msg padrão aqui
                    self.active_npc_interaction = None 
            
            # Lógica para sair do "foco" do NPC se o jogador se afastar e não estiver em diálogo ativo
            # (Esta lógica pode ser complexa e precisa de cuidado para não interromper diálogos indesejadamente)
            # Se active_npc_interaction existe, mas não está mais próximo e não está em diálogo ativo, limpa.
            if self.active_npc_interaction and \
               not self.active_npc_interaction.is_dialogue_active and \
               not is_near(self.player, self.active_npc_interaction, distance=TILE_SIZE * 1.5):
                 self.active_npc_interaction = None


    def get_npc_display_name(self, npc): # Renomeado para evitar confusão
        # Mapeia o tipo do NPC para um nome mais amigável
        if isinstance(npc, NPCVendedor): return "Vendedor"
        if isinstance(npc, NPCInformante): return "Informante"
        # if isinstance(npc, NPCFerreiro): return "Ferreiro"
        if npc.type == "forge": return "Ferreiro" # Fallback para tipo
        return "NPC"

    def draw(self):
        pyxel.cls(COLOR_BLACK)
        
        # Desenha o mapa
        for row_idx, row_val in enumerate(MAP_DATA):
            for col_idx, tile_val in enumerate(row_val):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                color = COLOR_WALL if tile_val == 1 else COLOR_FLOOR
                pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, color)

        # Desenha NPCs
        for npc_entity in self.npcs:
            npc_entity.draw()

        # Desenha Player
        self.player.draw()

        # Exibe Ouro do Jogador
        gold_text = f"Ouro: {self.player.gold}"
        # Desenha texto com sombra simples para melhor legibilidade
        pyxel.text(SCREEN_WIDTH - len(gold_text) * pyxel.FONT_WIDTH - 6, 6, gold_text, COLOR_BLACK)
        pyxel.text(SCREEN_WIDTH - len(gold_text) * pyxel.FONT_WIDTH - 5, 5, gold_text, COLOR_GOLD_TEXT)


        if self.show_inventory_ui:
            box_w, box_h = 120, 100
            box_x, box_y = (SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2
            
            pyxel.rect(box_x, box_y, box_w, box_h, COLOR_DIALOG_BG)
            pyxel.rectb(box_x, box_y, box_w, box_h, COLOR_DIALOG_BORDER)
            pyxel.text(box_x + 5, box_y + 5, "Mochila:", COLOR_INVENTORY_TEXT)

            item_y_offset = box_y + 15
            for i, (item_name, quantity) in enumerate(self.player.inventory.items()):
                display_name = item_name.replace("_", " ").capitalize()
                pyxel.text(box_x + 5, item_y_offset + (i * 10), f"- {display_name}: {quantity}", COLOR_INVENTORY_TEXT)
            
            pyxel.text(box_x + 5, box_y + box_h - 10, "[M] Fechar", COLOR_INVENTORY_TEXT)

        elif self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            npc = self.active_npc_interaction
            dialog_box_h = 38
            dialog_box_y = SCREEN_HEIGHT - dialog_box_h - 5 # Posição da caixa de diálogo
            
            pyxel.rect(5, dialog_box_y, SCREEN_WIDTH - 10, dialog_box_h, COLOR_DIALOG_BG)
            pyxel.rectb(5, dialog_box_y, SCREEN_WIDTH - 10, dialog_box_h, COLOR_DIALOG_BORDER)
            
            # Quebra de linha simples para mensagem do NPC (rudimentar)
            # Para mensagens mais longas, você precisaria de uma função de quebra de linha mais robusta.
            max_chars_per_line = (SCREEN_WIDTH - 20) // pyxel.FONT_WIDTH
            msg_line1 = npc.dialogue_message[:max_chars_per_line]
            msg_line2 = npc.dialogue_message[max_chars_per_line:] if len(npc.dialogue_message) > max_chars_per_line else ""

            pyxel.text(10, dialog_box_y + 4, msg_line1, COLOR_INVENTORY_TEXT)
            if msg_line2:
                 pyxel.text(10, dialog_box_y + 4 + 8, msg_line2, COLOR_INVENTORY_TEXT)

            opt_y_start = dialog_box_y + 16 + (8 if msg_line2 else 0) # Ajusta Y das opções se msg tem 2 linhas
            for i, opt_text in enumerate(npc.dialogue_options_display):
                pyxel.text(10, opt_y_start + (i * 8), opt_text, COLOR_INVENTORY_TEXT)
        else:
            # Mostra "Pressione E para interagir"
            temp_near_npc = None
            for npc_entity in self.npcs:
                if is_near(self.player, npc_entity, distance=TILE_SIZE * 1.5):
                    temp_near_npc = npc_entity
                    break
            if temp_near_npc:
                # Sombra para o texto de interação
                interact_msg = f"[E] Interagir com {self.get_npc_display_name(temp_near_npc)}"
                pyxel.text(6, SCREEN_HEIGHT - 14, interact_msg, COLOR_BLACK)
                pyxel.text(5, SCREEN_HEIGHT - 15, interact_msg, COLOR_WHITE)