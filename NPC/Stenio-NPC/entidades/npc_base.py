# npc_rpg/entities/npc_base.py
import pyxel
from core.config import TILE_SIZE

class NPCBase: # Renomeado para NPCBase para evitar conflito se houver um módulo chamado npc
    def __init__(self, x, y, npc_type, label, color):
        self.x = x
        self.y = y
        self.type = npc_type # e.g., "shop", "info", "forge"
        self.label = label   # e.g., "L", "I", "F"
        self.color = color

        self.automaton = None # Será definido pela subclasse
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None

    def draw(self):
        pyxel.rect(self.x, self.y, TILE_SIZE, TILE_SIZE, self.color)
        pyxel.text(self.x + 2, self.y + 2, self.label, 0) # Cor do texto do label

    def get_pixel_pos(self): # Posição em pixels, útil para colisões e outras lógicas
        return self.x, self.y

    def start_dialogue(self, player_obj):
        if not self.automaton:
            print(f"DEBUG: NPC {self.type} ({self.label}) nao tem automato definido.")
            return False
        
        self.player_in_dialogue = player_obj
        self.is_dialogue_active = True
        # Assumindo que todos os autômatos começam com um estado "INICIAL"
        # Se não, cada subclasse de NPC precisaria definir seu estado inicial de diálogo.
        initial_dialogue_state = "INICIAL" 
        if initial_dialogue_state not in self.automaton:
            print(f"DEBUG: Estado inicial '{initial_dialogue_state}' nao encontrado no automato do NPC {self.type}.")
            self.end_dialogue()
            return False

        self.dialogue_state = initial_dialogue_state
        self._update_dialogue_content()
        return True

    def _update_dialogue_content(self):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info:
            print(f"DEBUG: Estado de dialogo '{self.dialogue_state}' invalido para NPC {self.type}. Encerrando dialogo.")
            self.end_dialogue()
            return

        self.dialogue_message = state_info.get("message", "...")
        self.dialogue_options_display = []
        for key, text in state_info.get("options", {}).items():
            self.dialogue_options_display.append(f"[{key}] {text}")
        
        # Lógica para lidar com estados que não têm opções (como o estado "FIM")
        if not state_info.get("options"):
             # Se é o estado final 'FIM', a lógica de fechar o diálogo é tratada no Game.update
             pass


    def process_player_choice(self, choice_key):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info:
            print(f"DEBUG: Estado de dialogo '{self.dialogue_state}' invalido ao processar escolha.")
            return

        transitions = state_info.get("transitions", {})
        if choice_key not in transitions:
            print(f"DEBUG: Escolha '{choice_key}' invalida para o estado '{self.dialogue_state}'.")
            return # Escolha inválida para o estado atual

        next_state_key = transitions[choice_key]

        # Lógica de transação para o vendedor deve ser aqui ou em um método sobrescrito
        # na classe NPCVendedor.
        if self.type == "shop" and self.dialogue_state == "MENU_COMPRA":
            item_cost = 0
            item_name = None
            item_display_name = "" # Para a mensagem

            if choice_key == "1": # Poção
                item_cost = 10
                item_name = "pocao"
                item_display_name = "Poção"
            elif choice_key == "2": # Espada
                item_cost = 50
                item_name = "espada"
                item_display_name = "Espada"

            if item_name and self.player_in_dialogue:
                if self.player_in_dialogue.gold >= item_cost:
                    self.player_in_dialogue.gold -= item_cost
                    self.player_in_dialogue.inventory[item_name] += 1
                    # A mensagem de "comprou" já está no estado de destino.
                    # Poderíamos alterar a mensagem do estado de destino dinamicamente,
                    # mas o autômato atual tem mensagens fixas para POCAO_COMPRADA/ESPADA_COMPRADA.
                    self.dialogue_state = next_state_key
                else:
                    # Ouro insuficiente. Precisamos de um estado para isso ou modificar a msg.
                    # Por agora, apenas impede a compra e permanece no menu de compra.
                    self.dialogue_message = f"Ouro insuficiente para {item_display_name}!"
                    # Não muda de estado, força _update_dialogue_content para mostrar a nova mensagem
                    # mas as opções ainda serão do MENU_COMPRA. Isso é um placeholder.
                    # O ideal seria um estado "SEM_OURO" no autômato.
                    self._update_dialogue_content() # Re-renderiza com a msg de erro
                    return # Impede a transição normal abaixo
            elif choice_key == "3": # Voltar
                self.dialogue_state = next_state_key
            else: # Caso inválido dentro de MENU_COMPRA que não seja item nem voltar
                return 
        else: # Transição normal para outros estados ou outros NPCs
            self.dialogue_state = next_state_key
        
        self._update_dialogue_content()


    def end_dialogue(self):
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None