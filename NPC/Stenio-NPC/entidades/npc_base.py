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
                
                # Esta é a linha que deu erro (aproximadamente linha 112 na sua versão)
                if item_key_para_formatacao and item_key_para_formatacao in ITEM_DATA:
                    item_config = ITEM_DATA[item_key_para_formatacao]
                    player_qty_str = str(self.player_in_dialogue.inventory.get(item_key_para_formatacao, 0)) if self.player_in_dialogue else "N/A"
                    try:
                        formatted_message = raw_message.format(
                            item_nome=item_config.get("nome_exibicao", item_key_para_formatacao),
                            preco_base=item_config.get("preco_base", "N/A"),
                            preco_desconto=item_config.get("preco_desconto", "N/A"),
                            preco_npc_paga=item_config.get("preco_npc_paga_jogador", "N/A"),
                            jogador_qtd=player_qty_str
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
                # ANTES de chamar o handler, se ele não for definir a msg final, resetamos a flag
                # Mas os handlers que definimos (ameaca, persuasao, tentativa_compra, tentativa_venda)
                # TODOS definem a mensagem final e a flag.
                # A flag é resetada no 'else' do 'if not self._message_is_final_from_handler'.
                # Então, está correto. O handler definirá a flag como True antes de chamar _update_dialogue_content.
                getattr(self, action_handler_name)() 
            else:
                print(f"AVISO CRÍTICO: Action handler '{action_handler_name}' definido para '{self.dialogue_state}' mas método NÃO existe em {self.__class__.__name__}!")
                self.dialogue_state = "INICIAL" 
                self._update_dialogue_content()


    def process_player_choice(self, choice_key):
        # ... (verificações iniciais como antes) ...
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton: return # ...
        current_state_info = self.automaton.get(self.dialogue_state) # ...
        if not current_state_info: self.end_dialogue(); return # ...

        next_state_key = None

        # Lógica para MENU_VENDA_ESCOLHER_ITEM (define active_transaction_item_key)
        if self.dialogue_state == "MENU_VENDA_ESCOLHER_ITEM" and \
           hasattr(self, '_temp_sell_option_map') and self._temp_sell_option_map and \
           choice_key in self._temp_sell_option_map:

            self.active_transaction_item_key = self._temp_sell_option_map[choice_key]
            next_state_key = "CONFIRMAR_VENDA_ITEM_GENERICO"
            # _temp_sell_option_map é limpo no início de generate_sell_options_for_player

        # Lógica para DETALHES_ITEM_X (compra - define active_transaction_item_key)
        elif self.dialogue_state.startswith("DETALHES_ITEM_"):
            item_key_do_estado_detalhes = current_state_info.get("item_key")
            if item_key_do_estado_detalhes:
                self.active_transaction_item_key = item_key_do_estado_detalhes
            # A transição normal pegará o next_state_key (ex: para PROCESSAR_COMPRA_X ou NEGOCIANDO_PRECO_X)

        # Lógica para NEGOCIANDO_PRECO_X (mantém active_transaction_item_key)
        elif self.dialogue_state.startswith("NEGOCIANDO_PRECO_") or \
             self.dialogue_state.startswith("DESCONTO_OFERECIDO_") or \
             self.dialogue_state.startswith("NEGOCIACAO_FALHOU_"):
            # Garante que active_transaction_item_key já está setado do estado DETALHES_ITEM_X
            if not self.active_transaction_item_key: # Se perdeu, tenta pegar do estado atual
                self.active_transaction_item_key = current_state_info.get("item_key")

        # Se não foi um caso especial acima, ou se foi mas precisamos da transição do automato:
        if next_state_key is None: # Se next_state_key ainda não foi definido pelos casos especiais
            transitions = current_state_info.get("transitions", {})
            if choice_key in transitions:
                next_state_key = transitions[choice_key]
            else:
                return # Escolha inválida

        # Limpar active_transaction_item_key se estamos voltando para menus principais ou terminando
        if next_state_key in ["INICIAL", "MENU_COMPRA_CATEGORIAS", "MENU_VENDA_ESCOLHER_ITEM", "FIM_DIALOGO", "FIM_DIALOGO_NPC_AUSENTE"]:
            self.active_transaction_item_key = None

        if next_state_key:
            self.dialogue_state = next_state_key
            self._update_dialogue_content()
        # ... (else para debug crítico como antes) ...

    #def end_dialogue(self):
        #super().end_dialogue() # Se NPCBase herdar de algo que tenha end_dialogue
        #self.active_transaction_item_key = None # Limpa ao finalizar o diálogo
        # Certifique-se que _message_is_final_from_handler também é resetado aqui ou no start_dialogue
        #self._message_is_final_from_handler = False
        # ... (resto do end_dialogue)

    def handle_tentativa_venda_jogador(self): # Este é chamado por PROCESSAR_VENDA_ITEM
        # Define a flag PRIMEIRO para garantir que a mensagem definida aqui seja final
        self._message_is_final_from_handler = True

        item_key_a_vender = self.active_transaction_item_key # Pega do contexto da transação

        if not item_key_a_vender or not self.player_in_dialogue:
            self.dialogue_message = "Algo deu errado com esta transação."
            self.dialogue_state = "MENU_VENDA_ESCOLHER_ITEM"
            self.active_transaction_item_key = None 
            self._update_dialogue_content() # Chamada recursiva, mas _message_is_final_from_handler será False na próxima iteração
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
            # O active_transaction_item_key pode ser limpo aqui ou quando voltar ao menu principal de venda/geral.
            # Se VENDA_SUCESSO tem a opção de "Vender Mais Itens" que volta para MENU_VENDA_ESCOLHER_ITEM,
            # então active_transaction_item_key será redefinido ou limpo por process_player_choice.
        else:
            self.dialogue_state = "VENDA_FALHOU_SEM_ITEM"
            self.dialogue_message = f"Oh! Parece que você não tem mais {item_nome_exibicao} para vender."
            
        self._update_dialogue_content()

    def end_dialogue(self):
        # ... (método end_dialogue como antes) ...
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None


        if hasattr(self, 'active_transaction_item_key'): # Verifica se o atributo existe antes de tentar deletar/resetar
            self.active_transaction_item_key = None
        if hasattr(self, '_message_is_final_from_handler'): # Verifica se o atributo existe
            self._message_is_final_from_handler = False

    #def end_dialogue(self):
        #self.is_dialogue_active = False
        #self.dialogue_state = None
        #self.dialogue_message = ""
        #self.dialogue_options_display = []
        #self.player_in_dialogue = None