# npc_rpg/entities/npc_base.py
import pyxel
from core.config import TILE_SIZE, ITEM_DATA


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
            self.dialogue_message = ""
            self.dialogue_options_display = []
            if not self.automaton and self.is_dialogue_active:
                print(f"DEBUG: NPC {self.type} ({self.label}) em diálogo mas sem autômato. Encerrando.")
                self.end_dialogue()
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info:
            print(f"DEBUG: Estado de dialogo '{self.dialogue_state}' invalido para NPC {self.type} ({self.label}). Encerrando.")
            self.end_dialogue()
            return

        # 1. Formatar a mensagem do estado
        raw_message = state_info.get("message", "...")
        
        # Tenta pegar item_key do estado; se não houver, usa o _context_item_key (se existir)
        item_key_para_formatacao = state_info.get("item_key")
        if not item_key_para_formatacao and hasattr(self, '_context_item_key'):
            item_key_para_formatacao = self._context_item_key
        
        formatted_message = raw_message
        if "{item_nome}" in raw_message or \
           "{preco_base}" in raw_message or \
           "{preco_desconto}" in raw_message:
            
            if item_key_para_formatacao and item_key_para_formatacao in ITEM_DATA:
                item_config = ITEM_DATA[item_key_para_formatacao]
                try:
                    formatted_message = raw_message.format(
                        item_nome=item_config.get("nome_exibicao", item_key_para_formatacao),
                        preco_base=item_config.get("preco_base", "N/A"),
                        preco_desconto=item_config.get("preco_desconto", "N/A")
                    )
                except KeyError as e:
                    print(f"DEBUG: Erro ao formatar mensagem para estado '{self.dialogue_state}'. Placeholder ausente: {e}")
            else:
                # Só imprime o DEBUG se a mensagem realmente precisava de formatação e não conseguiu
                if "{item_nome}" in raw_message or "{preco_base}" in raw_message or "{preco_desconto}" in raw_message:
                    print(f"DEBUG: Estado '{self.dialogue_state}' tem mensagem formatavel mas falta item_key ou item_key='{item_key_para_formatacao}' é inválido.")
        
        self.dialogue_message = formatted_message

        # Limpa a chave de contexto depois de usada para que não afete o próximo estado independentemente.
        if hasattr(self, '_context_item_key'):
            del self._context_item_key

        # 2. Montar as opções para o jogador (lógica de formatação de opções como antes)
        self.dialogue_options_display = []
        current_player_options = state_info.get("options", {})
        for key, text_option_raw in current_player_options.items():
            text_option_formatted = text_option_raw
            # Reutiliza item_key_para_formatacao para as opções também
            if item_key_para_formatacao and item_key_para_formatacao in ITEM_DATA:
                if "{item_nome}" in text_option_raw or \
                   "{preco_base}" in text_option_raw or \
                   "{preco_desconto}" in text_option_raw:
                    item_config = ITEM_DATA[item_key_para_formatacao]
                    try:
                        text_option_formatted = text_option_raw.format(
                            item_nome=item_config.get("nome_exibicao", item_key_para_formatacao),
                            preco_base=item_config.get("preco_base", "N/A"),
                            preco_desconto=item_config.get("preco_desconto", "N/A")
                        )
                    except KeyError:
                        pass 
            self.dialogue_options_display.append(f"[{key}] {text_option_formatted}")
        
        # 3. Chamar 'action_handler' se o estado for de processamento automático
        action_handler_name = state_info.get("action_handler")
        if action_handler_name and not current_player_options: 
            if hasattr(self, action_handler_name):
                getattr(self, action_handler_name)() 
            else:
                print(f"AVISO CRÍTICO: Action handler '{action_handler_name}' definido para '{self.dialogue_state}' mas o método NÃO existe em {self.__class__.__name__}!")
                self.dialogue_state = "INICIAL" 
                self._update_dialogue_content()


    def process_player_choice(self, choice_key):
        """
        Processa a escolha feita pelo jogador durante o diálogo.
        'choice_key' é a string da tecla pressionada (ex: "1", "2").
        """
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            print("DEBUG: process_player_choice chamado mas o diálogo não está ativo ou falta autômato.")
            return

        current_state_info = self.automaton.get(self.dialogue_state)
        if not current_state_info:
            print(f"DEBUG: Estado de diálogo atual '{self.dialogue_state}' não encontrado no autômato ao processar escolha.")
            self.end_dialogue()
            return

        transitions = current_state_info.get("transitions", {})
        if choice_key not in transitions:
            # Se a tecla não corresponde a uma transição válida para as opções atuais, ignora.
            # Isso pode acontecer se o jogador apertar uma tecla que não é uma opção válida.
            # print(f"DEBUG: Escolha '{choice_key}' inválida ou não mapeada para transição no estado '{self.dialogue_state}'. Opções disponíveis: {current_state_info.get('options', {}).keys()}")
            return 

        # Obtém o próximo estado definido no autômato para a escolha do jogador
        next_state_key = transitions[choice_key]
        
        # Define o novo estado do diálogo
        self.dialogue_state = next_state_key
        
        # Atualiza a mensagem e as opções com base no novo estado.
        # Se o 'next_state_key' for um estado de processamento com um 'action_handler'
        # e sem opções, _update_dialogue_content (Passo 3) o chamará.
        # O action_handler então definirá o estado final e chamará _update_dialogue_content novamente.
        self._update_dialogue_content()

    def end_dialogue(self):
        # ... (método end_dialogue como antes) ...
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None


    def end_dialogue(self):
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None