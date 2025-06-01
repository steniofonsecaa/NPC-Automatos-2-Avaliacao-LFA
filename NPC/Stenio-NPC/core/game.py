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
            if self.show_inventory_ui and self.active_npc_interaction:
                self.active_npc_interaction.end_dialogue()
                self.active_npc_interaction = None

        if self.show_inventory_ui:
            return 

        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # --- MODO DE DIÁLOGO ATIVO ---
            npc = self.active_npc_interaction # Alias para facilitar

            # 1. Processar escolhas do jogador se o estado atual tiver opções
            # (Os estados FIM_DIALOGO e FIM_DIALOGO_NPC_AUSENTE não terão opções,
            # então as teclas 1,2,3 não farão transições a partir deles via process_player_choice)
            if npc.automaton.get(npc.dialogue_state, {}).get("options"): # Verifica se o estado ATUAL tem opções
                if pyxel.btnp(pyxel.KEY_1):
                    npc.process_player_choice("1")
                elif pyxel.btnp(pyxel.KEY_2):
                    npc.process_player_choice("2")
                elif pyxel.btnp(pyxel.KEY_3):
                    npc.process_player_choice("3")
                # Adicione mais elif para KEY_4, KEY_5 etc., se seu autômato usar.
            
            # 2. Verificar se o diálogo deve terminar (após uma escolha ou se o estado é terminal)
            # O estado pode ter mudado devido à process_player_choice ou a um action_handler.
            # Os action_handlers já chamam _update_dialogue_content, então npc.dialogue_state está atualizado.
            
            # Se o estado atual do NPC é um dos estados finais de diálogo
            if npc.dialogue_state == "FIM_DIALOGO" or \
               npc.dialogue_state == "FIM_DIALOGO_NPC_AUSENTE":
                
                # O NPC exibirá sua mensagem final (configurada por _update_dialogue_content).
                # Esperamos que o jogador pressione uma tecla para dispensar/fechar esta mensagem.
                # Usaremos 'E' (interagir), 'Q' (comum para sair/cancelar), Espaço, ou '1' (genérico)
                if pyxel.btnp(pyxel.KEY_E) or pyxel.btnp(pyxel.KEY_Q) or \
                   pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_1): # Tecla '1' como um "ok" genérico

                    should_npc_disappear = (npc.dialogue_state == "FIM_DIALOGO_NPC_AUSENTE")
                    
                    npc.end_dialogue()  # Limpa o estado de diálogo interno do NPC
                    self.active_npc_interaction = None  # Sai do modo de diálogo no jogo

                    if should_npc_disappear:
                        # TODO: Implementar a lógica para o NPC realmente desaparecer ou se tornar não interativo.
                        # Por enquanto, apenas um print para indicar a ação.
                        # Se for remover da lista self.npcs, cuidado com iterações sobre ela.
                        # Uma abordagem mais segura é marcar o NPC: npc.is_active = False
                        print(f"DEBUG: NPC {npc.label if hasattr(npc, 'label') else 'Desconhecido'} deveria desaparecer/ficar inativo.")
                        # Exemplo de como você poderia marcar o NPC (requer adicionar 'is_interactive' à classe NPC):
                        # if hasattr(npc, 'is_interactive'):
                        # npc.is_interactive = False
            
            # Se por algum motivo o diálogo se tornou inativo dentro do NPC, mas o Game ainda acha que está ativo
            elif not npc.is_dialogue_active and self.active_npc_interaction:
                 print(f"DEBUG: Diálogo com NPC {npc.label} tornou-se inativo internamente. Encerrando no Game.")
                 self.active_npc_interaction = None


        else: # --- MODO DE EXPLORAÇÃO ---
            # ... (seu código de modo de exploração: player.update, checar proximidade com NPCs, iniciar diálogo com 'E') ...
            # Certifique-se que a parte de iniciar diálogo (com 'E') esteja aqui.
            blocked_npc_pixel_positions = [n.get_pixel_pos() for n in self.npcs] # Usando n para evitar conflito com npc acima
            self.player.update(blocked_npc_pixel_positions)

            current_near_npc = None
            for npc_entity in self.npcs:
                # if hasattr(npc_entity, 'is_interactive') and not npc_entity.is_interactive:
                # continue # Pula NPCs que não estão interativos (ex: fugiram)
                if is_near(self.player, npc_entity, distance=TILE_SIZE * 1.5):
                    current_near_npc = npc_entity
                    break
            
            if current_near_npc and pyxel.btnp(pyxel.KEY_E):
                # if hasattr(current_near_npc, 'is_interactive') and not current_near_npc.is_interactive:
                #    pass # Não interage se o NPC estiver marcado como não interativo
                # else:
                self.active_npc_interaction = current_near_npc
                if not self.active_npc_interaction.start_dialogue(self.player):
                    print(f"NPC {current_near_npc.type} ({current_near_npc.label}) nao iniciou dialogo complexo.")
                    self.active_npc_interaction = None 
            
            # Limpar foco do NPC se o jogador se afastar (apenas se não estiver em diálogo ativo)
            if self.active_npc_interaction and \
               (not hasattr(self.active_npc_interaction, 'is_dialogue_active') or \
                not self.active_npc_interaction.is_dialogue_active) and \
               not is_near(self.player, self.active_npc_interaction, distance=TILE_SIZE * 1.5): # Aumenta a distância para "desfocar"
                self.active_npc_interaction = None


    # ... (get_npc_display_name e draw como antes) ...
    def get_npc_display_name(self, npc_obj): # Renomeado parâmetro para evitar conflito
        if isinstance(npc_obj, NPCVendedor): return "Vendedor" # Certifique-se que NPCVendedor está importado
        # Adicione isinstance para outros tipos de NPC específicos
        # from entities.npc_vendedor import NPCVendedor # No topo de game.py
        if hasattr(npc_obj, 'type'): # Fallback para tipo genérico
            if npc_obj.type == "info": return "Informante"
            if npc_obj.type == "forge": return "Ferreiro"
        return "NPC"

    def draw(self):
        # ... (seu método draw permanece o mesmo, ele já lida com exibir
        # a UI de diálogo se self.active_npc_interaction estiver definido e ativo,
        # ou a UI da mochila se self.show_inventory_ui for true,
        # ou a mensagem de interação se nenhuma das UIs estiver ativa mas perto de um NPC) ...
        pyxel.cls(COLOR_BLACK)
        
        for row_idx, row_val in enumerate(MAP_DATA):
            for col_idx, tile_val in enumerate(row_val):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                color = COLOR_WALL if tile_val == 1 else COLOR_FLOOR
                pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, color)

        for npc_entity in self.npcs:
            # if hasattr(npc_entity, 'is_visible') and not npc_entity.is_visible:
            #    continue # Não desenha NPCs invisíveis
            npc_entity.draw()

        self.player.draw()

        gold_text = f"Ouro: {self.player.gold}"
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
            dialog_box_y = SCREEN_HEIGHT - dialog_box_h - 5
            
            pyxel.rect(5, dialog_box_y, SCREEN_WIDTH - 10, dialog_box_h, COLOR_DIALOG_BG)
            pyxel.rectb(5, dialog_box_y, SCREEN_WIDTH - 10, dialog_box_h, COLOR_DIALOG_BORDER)
            
            max_chars_per_line = (SCREEN_WIDTH - 20) // pyxel.FONT_WIDTH
            msg_line1 = npc.dialogue_message[:max_chars_per_line]
            msg_line2 = npc.dialogue_message[max_chars_per_line:] if len(npc.dialogue_message) > max_chars_per_line else ""

            pyxel.text(10, dialog_box_y + 4, msg_line1, COLOR_INVENTORY_TEXT)
            if msg_line2:
                pyxel.text(10, dialog_box_y + 4 + 8, msg_line2, COLOR_INVENTORY_TEXT)

            opt_y_start = dialog_box_y + 16 + (8 if msg_line2 else 0)
            for i, opt_text in enumerate(npc.dialogue_options_display):
                pyxel.text(10, opt_y_start + (i * 8), opt_text, COLOR_INVENTORY_TEXT)
        else:
            temp_near_npc = None
            for npc_entity in self.npcs:
                # if hasattr(npc_entity, 'is_interactive') and not npc_entity.is_interactive:
                #    continue
                if is_near(self.player, npc_entity, distance=TILE_SIZE * 1.5):
                    temp_near_npc = npc_entity
                    break
            if temp_near_npc:
                interact_msg = f"[E] Interagir com {self.get_npc_display_name(temp_near_npc)}"
                pyxel.text(6, SCREEN_HEIGHT - 14, interact_msg, COLOR_BLACK)
                pyxel.text(5, SCREEN_HEIGHT - 15, interact_msg, COLOR_WHITE)