# npc_rpg/core/game.py
import pyxel
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MAP_DATA, COLOR_WALL, COLOR_FLOOR, COLOR_GOLD_TEXT, COLOR_INVENTORY_TEXT, COLOR_DIALOG_BG, COLOR_DIALOG_BORDER
from .map_utils import is_near
from entidades.player import Player

COLOR_BLACK = 0 
COLOR_WHITE = 7  

from entidades.npc_vendedor import NPCVendedor
from entidades.npc_informante import NPCInformante 
from entidades.npc_base import NPCBase

TARGET_GAME_FPS = 60


class Game:
    def __init__(self):
        # Use TARGET_GAME_FPS na inicialização do Pyxel
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Meu RPG com NPCs", fps=TARGET_GAME_FPS) 
        
        self.player = Player(start_x=SCREEN_WIDTH // 2, start_y=SCREEN_HEIGHT // 2)
        self.npcs = [
            NPCVendedor(TILE_SIZE * 3, TILE_SIZE * 3),
            NPCInformante(SCREEN_WIDTH - TILE_SIZE * 4, TILE_SIZE * 3, label="I"), # Ajuste a cor se necessário
            NPCBase(TILE_SIZE * 3, SCREEN_HEIGHT - TILE_SIZE * 4, npc_type="forge", label="F", color=10) 
        ]
        
        self.active_npc_interaction = None
        self.show_inventory_ui = False

        self.dialogue_end_timer_start_frame = None
        self.DIALOGUE_AUTOCLOSE_DELAY_SECONDS = 2
        # Use TARGET_GAME_FPS para calcular os frames
        self.dialogue_autoclose_delay_frames = self.DIALOGUE_AUTOCLOSE_DELAY_SECONDS * TARGET_GAME_FPS
        
        pyxel.run(self.update, self.draw)


    def update(self):
        if pyxel.btnp(pyxel.KEY_M):
            self.show_inventory_ui = not self.show_inventory_ui
            if self.show_inventory_ui and self.active_npc_interaction:
                # Se abrir o inventário durante um diálogo, encerra o diálogo e o timer
                self.active_npc_interaction.end_dialogue()
                self.active_npc_interaction = None
                self.dialogue_end_timer_start_frame = None # Reseta o timer

        if self.show_inventory_ui:
            return 

        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # --- MODO DE DIÁLOGO ATIVO ---
            npc = self.active_npc_interaction
            
            # 1. Processar escolhas do jogador se o estado atual tiver opções
            player_made_choice_this_frame = False
            if npc.automaton.get(npc.dialogue_state, {}).get("options"):
                if pyxel.btnp(pyxel.KEY_1):
                    npc.process_player_choice("1")
                    player_made_choice_this_frame = True
                elif pyxel.btnp(pyxel.KEY_2):
                    npc.process_player_choice("2")
                    player_made_choice_this_frame = True
                elif pyxel.btnp(pyxel.KEY_3):
                    npc.process_player_choice("3")
                    player_made_choice_this_frame = True
                elif pyxel.btnp(pyxel.KEY_4):
                    npc.process_player_choice("4")
                    player_made_choice_this_frame = True
            
            # 2. Avaliar o estado do NPC (pode ter mudado devido à escolha ou action_handler)
            is_current_state_final = (npc.dialogue_state == "FIM_DIALOGO" or \
                                      npc.dialogue_state == "FIM_DIALOGO_NPC_AUSENTE")

            if is_current_state_final:
                # Se o NPC acabou de entrar em um estado final, inicia o timer
                if self.dialogue_end_timer_start_frame is None:
                    self.dialogue_end_timer_start_frame = pyxel.frame_count
                
                # Verifica se o timer expirou
                if pyxel.frame_count - self.dialogue_end_timer_start_frame >= self.dialogue_autoclose_delay_frames:
                    should_npc_disappear = (npc.dialogue_state == "FIM_DIALOGO_NPC_AUSENTE")
                    
                    npc.end_dialogue()
                    self.active_npc_interaction = None
                    self.dialogue_end_timer_start_frame = None # Reseta o timer

                    if should_npc_disappear:
                        print(f"DEBUG: NPC {npc.label if hasattr(npc, 'label') else 'Desconhecido'} auto-desapareceu após timer.")
                        # TODO: Lógica para NPC desaparecer (ex: self.npcs.remove(npc) ou npc.is_active = False)
                # else: Mensagem final está sendo exibida, aguardando timer expirar.
            
            elif player_made_choice_this_frame:
                # Se o jogador fez uma escolha que NÃO levou a um estado final,
                # qualquer timer de despedida anterior deve ser cancelado.
                self.dialogue_end_timer_start_frame = None
            
            # Se o diálogo se tornou inativo por outra razão (ex: erro interno no NPC)
            elif not npc.is_dialogue_active and self.active_npc_interaction: # Checa se o active_npc_interaction ainda é este npc
                 print(f"DEBUG: Diálogo com NPC {npc.label} tornou-se inativo internamente. Encerrando no Game.")
                 self.active_npc_interaction.end_dialogue() # Garante que o NPC também limpe seu estado
                 self.active_npc_interaction = None
                 self.dialogue_end_timer_start_frame = None # Reseta o timer

        else: 
            # --- MODO DE EXPLORAÇÃO ---
            blocked_npc_pixel_positions = [n.get_pixel_pos() for n in self.npcs]
            self.player.update(blocked_npc_pixel_positions)

            current_near_npc = None
            for npc_entity in self.npcs:
                if is_near(self.player, npc_entity, distance=TILE_SIZE * 1.5):
                    current_near_npc = npc_entity
                    break
            
            if current_near_npc and pyxel.btnp(pyxel.KEY_E):
                self.active_npc_interaction = current_near_npc
                self.dialogue_end_timer_start_frame = None # Reseta timer ao iniciar novo diálogo
                if not self.active_npc_interaction.start_dialogue(self.player):
                    print(f"NPC {current_near_npc.type} ({current_near_npc.label}) nao iniciou dialogo complexo.")
                    self.active_npc_interaction = None 
            
            if self.active_npc_interaction and \
               (not hasattr(self.active_npc_interaction, 'is_dialogue_active') or \
                not self.active_npc_interaction.is_dialogue_active) and \
               not is_near(self.player, self.active_npc_interaction, distance=TILE_SIZE * 1.5):
                self.active_npc_interaction = None
                self.dialogue_end_timer_start_frame = None # Reseta timer se sair de perto


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
        pyxel.cls(COLOR_BLACK)
        
        for row_idx, row_val in enumerate(MAP_DATA):
            for col_idx, tile_val in enumerate(row_val):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                color = COLOR_WALL if tile_val == 1 else COLOR_FLOOR
                pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, color)

        for npc_entity in self.npcs:
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
            # --- UI DE DIÁLOGO DO NPC (MODIFICADO PARA CENTRALIZAR) ---
            npc = self.active_npc_interaction
            
            # Define dimensões e posição da caixa de diálogo centralizada
            dialog_box_w = SCREEN_WIDTH - 40 # Largura (ex: tela - 20 pixels de cada lado)
            # Altura pode ser baseada no conteúdo ou fixa. Vamos usar uma altura fixa maior.
            num_options = len(npc.dialogue_options_display)
            # Altura base: 2 linhas para mensagem + espaço para cada opção + preenchimento
            dialog_box_h = 20 + (num_options * 10) + 10 
            if npc.dialogue_message.count('\n') > 0: # Se a mensagem tiver quebras de linha (não temos auto-wrap ainda)
                 dialog_box_h += (npc.dialogue_message.count('\n')) * 8 # Adiciona espaço para mais linhas de mensagem

            dialog_box_h = max(dialog_box_h, 50) # Altura mínima
            dialog_box_h = min(dialog_box_h, SCREEN_HEIGHT - 40) # Altura máxima para não sair da tela


            dialog_box_x = (SCREEN_WIDTH - dialog_box_w) // 2
            dialog_box_y = (SCREEN_HEIGHT - dialog_box_h) // 2
            
            # Desenha a caixa de diálogo
            pyxel.rect(dialog_box_x, dialog_box_y, dialog_box_w, dialog_box_h, COLOR_DIALOG_BG)
            pyxel.rectb(dialog_box_x, dialog_box_y, dialog_box_w, dialog_box_h, COLOR_DIALOG_BORDER)
            
            # Desenha a mensagem do NPC
            # (Ainda usando a quebra de linha simples. Para um wrap melhor, seria mais complexo)
            padding = 5 # Espaçamento interno da caixa
            text_x = dialog_box_x + padding
            text_y_start = dialog_box_y + padding
            
            # Simples quebra de linha manual para a mensagem do NPC
            # Você pode querer uma função mais robusta para quebrar linhas longas automaticamente
            # baseada na largura da dialog_box_w.
            # Por agora, vamos assumir que as mensagens do autômato são curtas ou você pode
            # adicionar '\n' manualmente nelas se precisar de múltiplas linhas.
            
            # Tentativa de quebra de linha simples (melhorar depois se necessário)
            current_y = text_y_start
            lines = npc.dialogue_message.split('\n') # Se já tivermos quebras manuais
            if len(lines) == 1 and len(npc.dialogue_message) * pyxel.FONT_WIDTH > dialog_box_w - padding*2 : # Tenta quebrar se for uma linha longa
                # Lógica de quebra de linha muito básica (apenas exemplo, pode não ser ideal)
                words = npc.dialogue_message.split(' ')
                line1_words = []
                current_line_len = 0
                for word in words:
                    if current_line_len + len(word)*pyxel.FONT_WIDTH + pyxel.FONT_WIDTH > dialog_box_w - padding*2:
                        break
                    line1_words.append(word)
                    current_line_len += len(word)*pyxel.FONT_WIDTH + pyxel.FONT_WIDTH
                
                msg_line1 = " ".join(line1_words)
                remaining_words = words[len(line1_words):]
                msg_line2 = " ".join(remaining_words) if remaining_words else ""

                pyxel.text(text_x, current_y, msg_line1, COLOR_INVENTORY_TEXT)
                current_y += 8 # Espaço para próxima linha
                if msg_line2:
                    pyxel.text(text_x, current_y, msg_line2[:(dialog_box_w - padding*2)//pyxel.FONT_WIDTH], COLOR_INVENTORY_TEXT) # Corta a segunda linha se muito longa
                    current_y += 8 
            else: # Se já tem \n ou é curta
                for line in lines:
                    pyxel.text(text_x, current_y, line, COLOR_INVENTORY_TEXT)
                    current_y += 8 # Espaço entre linhas da mensagem
            
            # Desenha as opções do jogador
            opt_y_start = current_y + 4 # Adiciona um pequeno espaço após a mensagem do NPC
            for i, opt_text in enumerate(npc.dialogue_options_display):
                pyxel.text(text_x, opt_y_start + (i * 10), opt_text, COLOR_INVENTORY_TEXT) # Aumentei o espaçamento entre opções para 10

        else: # Modo de Exploração - Mostrar "[E] Interagir"
            temp_near_npc = None
            for npc_entity in self.npcs:
                if is_near(self.player, npc_entity, distance=TILE_SIZE * 1.5):
                    temp_near_npc = npc_entity
                    break
            if temp_near_npc:
                interact_msg = f"[E] Interagir com {self.get_npc_display_name(temp_near_npc)}"
                # Calcula a largura da mensagem para centralizar ou alinhar
                msg_width = len(interact_msg) * pyxel.FONT_WIDTH
                prompt_x = (SCREEN_WIDTH - msg_width) // 2 # Centraliza a mensagem de interação
                prompt_y = SCREEN_HEIGHT - 15

                pyxel.text(prompt_x + 1, prompt_y + 1, interact_msg, COLOR_BLACK) # Sombra
                pyxel.text(prompt_x, prompt_y, interact_msg, COLOR_WHITE)