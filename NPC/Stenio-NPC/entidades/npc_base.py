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
        self.active_transaction_item_key = None
        self._message_is_final_from_handler = False

        self.active_transaction_item_key = None

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
                self.end_dialogue()
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info:
            self.end_dialogue()
            return

        # 1. Lidar com a mensagem do estado
        if not self._message_is_final_from_handler: # Se a msg NÃO foi finalizada por um handler
            raw_message = state_info.get("message", "...")
            
            item_key_para_formatacao = None # Inicializa explicitamente como None
            
            state_defined_item_key = state_info.get("item_key")
            if state_defined_item_key:
                item_key_para_formatacao = state_defined_item_key
            elif hasattr(self, 'active_transaction_item_key') and self.active_transaction_item_key:
                item_key_para_formatacao = self.active_transaction_item_key
            
            formatted_message = raw_message 
            if "{item_nome}" in raw_message or \
               "{preco_base}" in raw_message or \
               "{preco_desconto}" in raw_message or \
               "{preco_npc_paga}" in raw_message or \
               "{jogador_qtd}" in raw_message:
                
                if item_key_para_formatacao and item_key_para_formatacao in ITEM_DATA:
                    item_config = ITEM_DATA[item_key_para_formatacao]
                    player_qty_str = str(self.player_in_dialogue.inventory.get(item_key_para_formatacao, 0)) if self.player_in_dialogue else "N/A"
                    materiais_str = ""
                    if "materiais_melhoria" in item_config:
                        materiais_list = []
                        for mat_key, mat_qty in item_config["materiais_melhoria"].items():
                            mat_nome = ITEM_DATA.get(mat_key, {}).get("nome_exibicao", mat_key)
                            materiais_list.append(f"{mat_qty} {mat_nome}")
                        materiais_str = ", ".join(materiais_list) if materiais_list else "Nenhum"
                    try:
                        formatted_message = raw_message.format(
                            item_nome=item_config.get("nome_exibicao", item_key_para_formatacao),
                            preco_base=item_config.get("preco_venda_jogador_paga_npc", "N/A"), # Ajustado para compra
                            preco_desconto=item_config.get("preco_desconto", "N/A"), # Ajustado para compra
                            preco_npc_paga=item_config.get("preco_npc_paga_jogador", "N/A"), # Para venda
                            jogador_qtd=player_qty_str,
                            custo_melhoria_ouro=item_config.get("custo_melhoria_ouro", "N/A"), # NOVO
                            materiais_melhoria=materiais_str # NOVO
                        )
                    except KeyError as e:
                        print(f"DEBUG: Erro ao formatar msg (template) para '{self.dialogue_state}'. Placeholder: {e}")
                else: 
                    if "{item_nome}" in raw_message: 
                         print(f"DEBUG:_UPDATE_CONTENT: Estado '{self.dialogue_state}' tem msg formatavel mas item_key_para_formatacao ('{item_key_para_formatacao}') é inválido ou não está em ITEM_DATA.")
            
            self.dialogue_message = formatted_message
        else:
            # A mensagem já foi definida pelo handler, apenas reseta a flag para a próxima vez que _update_dialogue_content for chamado para um NOVO estado.
            self._message_is_final_from_handler = False

        # 2. Montar as opções para o jogador (lógica como antes)
        self.dialogue_options_display = []
        options_generator_handler_name = state_info.get("options_generator_handler")

        if options_generator_handler_name and hasattr(self, options_generator_handler_name):
            getattr(self, options_generator_handler_name)()
        else:
            # (Lógica para montar opções estáticas como antes, usando item_key_para_formatacao se necessário para elas)
            current_player_options = state_info.get("options", {})
            item_key_for_options = state_info.get("item_key") #Pega do estado
            if not item_key_for_options and hasattr(self, 'active_transaction_item_key') and self.active_transaction_item_key:
                 item_key_for_options = self.active_transaction_item_key #Fallback para o de transação

            for key, text_option_raw in current_player_options.items():
                text_option_formatted = text_option_raw
                if item_key_for_options and item_key_for_options in ITEM_DATA:
                     if any(ph in text_option_raw for ph in ["{item_nome}", "{preco_base}", "{preco_desconto}", "{preco_npc_paga}"]):
                        item_config = ITEM_DATA[item_key_for_options]
                        try:
                            text_option_formatted = text_option_raw.format(
                                item_nome=item_config.get("nome_exibicao", item_key_for_options),
                                preco_base=item_config.get("preco_base", "N/A"),
                                preco_desconto=item_config.get("preco_desconto", "N/A"),
                                preco_npc_paga=item_config.get("preco_npc_paga_jogador", "N/A")
                            )
                        except KeyError: pass 
                self.dialogue_options_display.append(f"[{key}] {text_option_formatted}")
        
        # 3. Chamar 'action_handler' se o estado for de processamento automático (como antes)
        action_handler_name = state_info.get("action_handler")
        if action_handler_name and not self.dialogue_options_display: 
            if hasattr(self, action_handler_name):
                getattr(self, action_handler_name)() 
            else:
                print(f"AVISO CRÍTICO: Action handler '{action_handler_name}' definido para '{self.dialogue_state}' mas método NÃO existe em {self.__class__.__name__}!")
                self.dialogue_state = "INICIAL" 
                self._update_dialogue_content()


    def process_player_choice(self, choice_key):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton: return
        current_state_info = self.automaton.get(self.dialogue_state)
        if not current_state_info: self.end_dialogue(); return

        next_state_key = None
        
        if self.dialogue_state == "MENU_VENDA_ESCOLHER_ITEM" and \
           hasattr(self, '_temp_sell_option_map') and self._temp_sell_option_map and \
           choice_key in self._temp_sell_option_map:
            self.active_transaction_item_key = self._temp_sell_option_map[choice_key]
            next_state_key = "CONFIRMAR_VENDA_ITEM_GENERICO"
            
        elif self.dialogue_state == "ESCOLHER_ITEM_MELHORIA":
            if hasattr(self, '_temp_upgrade_option_map') and self._temp_upgrade_option_map and \
               choice_key in self._temp_upgrade_option_map:
                self.active_transaction_item_key = self._temp_upgrade_option_map[choice_key]
                next_state_key = "CONFIRMAR_MELHORIA_ITEM"
            elif choice_key == "9":
                flag_nenhum_item = getattr(self, '_nenhum_item_para_melhorar_flag', False) # Pega com segurança
                print(f"DEBUG_BASE (process_choice): ESCOLHER_ITEM_MELHORIA, choice '9'. Flag lida: {flag_nenhum_item}") # DEBUG

                if flag_nenhum_item: 
                    next_state_key = "ENCERRADO"
                    print(f"DEBUG_BASE (process_choice): Flag é TRUE. Tentando ir para ENCERRADO.") # DEBUG
                else:
                    transitions = current_state_info.get("transitions", {})
                    next_state_key = transitions.get(choice_key) 
                    print(f"DEBUG_BASE (process_choice): Flag é FALSE. Transição normal para: {next_state_key}") # DEBUG
                if hasattr(self, '_nenhum_item_para_melhorar_flag') and self._nenhum_item_para_melhorar_flag:
                    next_state_key = "ENCERRADO" 
                else:
                    transitions = current_state_info.get("transitions", {})
                    next_state_key = transitions.get(choice_key) 
            if hasattr(self, '_nenhum_item_para_melhorar_flag'):
                self._nenhum_item_para_melhorar_flag = False
                
        #Informante
        elif self.dialogue_state == "ESCOLHER_PERGUNTA" and \
             hasattr(self, '_temp_question_option_map') and self._temp_question_option_map and \
             choice_key in self._temp_question_option_map:
    
            self.active_transaction_item_key = self._temp_question_option_map[choice_key] 
            next_state_key = "PROCESSAR_ESCOLHA_PERGUNTA"
            # print(f"DEBUG_BASE (process_choice): Informante - Escolheu tópico '{self.active_transaction_item_key}', indo para '{next_state_key}'")

        elif self.dialogue_state.startswith("DETALHES_ITEM_") or \
             self.dialogue_state.startswith("CONFIRMAR_MELHORIA_ITEM"): 
            item_key_do_estado = current_state_info.get("item_key") or self.active_transaction_item_key
            if item_key_do_estado:
                self.active_transaction_item_key = item_key_do_estado

        if next_state_key is None:
            transitions = current_state_info.get("transitions", {})
            if choice_key in transitions:
                next_state_key = transitions[choice_key]
            else:
                return 

        
        if next_state_key in ["INICIAL", "MENU_COMPRA_CATEGORIAS", "MENU_VENDA_ESCOLHER_ITEM", 
                              "OFERECENDO_SERVICO", # Adicionado
                              "FIM_DIALOGO", "FIM_DIALOGO_NPC_AUSENTE", "ENCERRADO"]:
            self.active_transaction_item_key = None
            if hasattr(self, '_temp_sell_option_map'): self._temp_sell_option_map.clear()
            if hasattr(self, '_temp_upgrade_option_map'): self._temp_upgrade_option_map.clear()
            
        if next_state_key:
            self.dialogue_state = next_state_key
            self._update_dialogue_content()

    def handle_tentativa_venda_jogador(self): 
        self._message_is_final_from_handler = True

        item_key_a_vender = self.active_transaction_item_key

        if not item_key_a_vender or not self.player_in_dialogue:
            self.dialogue_message = "Algo deu errado com esta transação."
            self.dialogue_state = "MENU_VENDA_ESCOLHER_ITEM"
            self.active_transaction_item_key = None 
            self._update_dialogue_content()
            return

        item_config = ITEM_DATA.get(item_key_a_vender)
        player_quantity = self.player_in_dialogue.inventory.get(item_key_a_vender, 0)
        
        if not item_config or not item_config.get("preco_npc_paga_jogador"):
            item_nome_temp = item_config.get("nome_exibicao", item_key_a_vender) if item_config else item_key_a_vender
            self.dialogue_message = f"Na verdade, não estou comprando {item_nome_temp} hoje."
            self.dialogue_state = "NPC_NAO_COMPRA_ITEM"
            self._update_dialogue_content()
            return

        preco_que_npc_paga = item_config["preco_npc_paga_jogador"]
        item_nome_exibicao = item_config.get("nome_exibicao", item_key_a_vender)

        if player_quantity > 0:
            self.player_in_dialogue.inventory[item_key_a_vender] -= 1
            self.player_in_dialogue.gold += preco_que_npc_paga
            self.dialogue_state = "VENDA_SUCESSO"
            self.dialogue_message = f"Vendido! {item_nome_exibicao} por {preco_que_npc_paga}g. Ouro: {self.player_in_dialogue.gold}"
        else:
            self.dialogue_state = "VENDA_FALHOU_SEM_ITEM"
            self.dialogue_message = f"Oh! Parece que você não tem mais {item_nome_exibicao} para vender."
            
        self._update_dialogue_content()

    def end_dialogue(self):
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None


        if hasattr(self, 'active_transaction_item_key'): 
            self.active_transaction_item_key = None
        if hasattr(self, '_message_is_final_from_handler'):
            self._message_is_final_from_handler = False