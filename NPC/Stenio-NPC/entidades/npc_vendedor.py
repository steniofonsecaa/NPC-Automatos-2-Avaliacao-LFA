import random # Adicione esta importação se ainda não estiver lá
from .npc_base import NPCBase
from automatos.shop_npc_automaton import SHOP_NPC_AUTOMATON
from core.config import COLOR_SHOP_NPC # Importa a cor específica
from core.config import ITEM_DATA # Importa os dados dos itens

class NPCVendedor(NPCBase):
    def __init__(self, x, y, label="L"):
        # ... (seu __init__ existente com as chances) ...
        super().__init__(x, y, npc_type="shop", label=label, color=COLOR_SHOP_NPC)
        self.automaton = SHOP_NPC_AUTOMATON

        self.chance_recusar_venda_aleatoria = 0.1 
        self.chance_conceder_desconto_persuasao = 0.6 
        self.chance_npc_fugir_ameaca = 0.4
        self._message_is_final_from_handler = False

        self._temp_sell_option_map = {}

    def handle_ameaca(self):
        # ... (código do handle_ameaca) ...
        if random.random() < self.chance_npc_fugir_ameaca:
            self.dialogue_state = "FUGINDO"
        else:
            self.dialogue_state = "AMEACA_FRACASSADA"
        self._update_dialogue_content()

    # NOVO MÉTODO ABAIXO:
    def handle_persuasao_desconto(self):
        """
        Lógica para quando o jogador tenta persuadir por um desconto.
        Chamado por estados como 'PROCESSAR_PERSUASAO_POCAO'.
        O estado atual deve ter um 'item_key' definido no autômato.
        """
        # print("DEBUG: NPCVendedor - Entrou em handle_persuasao_desconto")
        current_state_info = self.automaton.get(self.dialogue_state)
        item_key = current_state_info.get("item_key")

        if not item_key:
            print(f"AVISO: handle_persuasao_desconto chamado sem 'item_key' no estado {self.dialogue_state}")
            self.dialogue_state = "INICIAL" # Fallback seguro
            self._update_dialogue_content()
            return

        if random.random() < self.chance_conceder_desconto_persuasao:
            # Concedeu o desconto!
            # Monta o nome do próximo estado dinamicamente. Ex: "DESCONTO_OFERECIDO_POCAO"
            next_state_name = f"DESCONTO_OFERECIDO_{item_key.upper()}"
            if next_state_name not in self.automaton: # Verifica se o estado de desconto existe
                print(f"AVISO: Estado de desconto '{next_state_name}' não encontrado no autômato. Falhando persuasão.")
                next_state_name = f"NEGOCIACAO_FALHOU_{item_key.upper()}" # Fallback para falha
                # Garante que o estado de falha existe
                if next_state_name not in self.automaton:
                    print(f"AVISO CRÍTICO: Estado de falha '{next_state_name}' também não encontrado!")
                    self.dialogue_state = "INICIAL" # Fallback final
                    self._update_dialogue_content()
                    return
            self.dialogue_state = next_state_name
        else:
            # Persuasão falhou.
            # Monta o nome do próximo estado. Ex: "NEGOCIACAO_FALHOU_POCAO"
            next_state_name = f"NEGOCIACAO_FALHOU_{item_key.upper()}"
            if next_state_name not in self.automaton: # Verifica se o estado de falha existe
                print(f"AVISO CRÍTICO: Estado de falha '{next_state_name}' não encontrado no autômato após falha na persuasão!")
                self.dialogue_state = "INICIAL" # Fallback final
                self._update_dialogue_content()
                return
            self.dialogue_state = next_state_name
            
        self._update_dialogue_content()

    def handle_tentativa_compra(self):
        current_state_info = self.automaton.get(self.dialogue_state)
        item_key = current_state_info.get("item_key")
        preco_final = current_state_info.get("preco_final")
        self._message_is_final_from_handler = True # Mensagem será definitiva

        if not item_key or preco_final is None or not self.player_in_dialogue:
            self.dialogue_message = "Algo deu errado com minha loja!"
            self.dialogue_state = "INICIAL" 
            self._update_dialogue_content()
            return

        item_config = ITEM_DATA.get(item_key)
        if not item_config:
            self.dialogue_message = "Não reconheço esse item..."
            self.dialogue_state = "INICIAL"
            self._update_dialogue_content()
            return
        
        item_nome_exibicao = item_config.get("nome_exibicao", item_key)

        if self.player_in_dialogue.gold >= preco_final:
            if hasattr(self, 'chance_recusar_venda_aleatoria') and \
               random.random() < self.chance_recusar_venda_aleatoria:
                self.dialogue_state = "RECUSANDO_VENDA_ALEATORIA"
                self.dialogue_message = f"Hmm... Quer saber? Hoje não estou a fim de vender esta {item_nome_exibicao} para você."
            else: 
                self.player_in_dialogue.gold -= preco_final
                self.player_in_dialogue.inventory[item_key] = self.player_in_dialogue.inventory.get(item_key, 0) + 1
                self.dialogue_state = "COMPRA_SUCESSO"
                self.dialogue_message = f"Negócio fechado! {item_nome_exibicao} ({preco_final}g) é seu. Ouro: {self.player_in_dialogue.gold}"
        else: 
            self.dialogue_state = "SEM_OURO"
            self.dialogue_message = f"Ah, que pena. Você precisa de {preco_final}g para {item_nome_exibicao}, mas só tem {self.player_in_dialogue.gold}g."

    def generate_sell_options_for_player(self):
        """
        Gera dinamicamente as opções de venda para o jogador com base no seu inventário
        e nos itens que o NPC compra.
        Este método POPULA self.dialogue_options_display e self._temp_sell_option_map.
        Ele NÃO deve chamar _update_dialogue_content().
        """
        # print("DEBUG: NPCVendedor - Entrou em generate_sell_options_for_player")
        self.dialogue_options_display = [] # Limpa para novas opções
        self._temp_sell_option_map = {}    # Limpa o mapa temporário
        
        if not self.player_in_dialogue:
            # Se não houver referência ao jogador, apenas preenche com a opção de voltar do autômato
            current_state_info = self.automaton.get(self.dialogue_state, {})
            fixed_options = current_state_info.get("options", {})
            for key, text in fixed_options.items():
                self.dialogue_options_display.append(f"[{key}] {text}")
            return

        sellable_items_count = 0
        # Iterar sobre os itens que o jogador PODE vender (madeira, ferro, tecido, pocao)
        # Ou iterar sobre ITEM_DATA e checar se o jogador tem e se o NPC compra
        
        # Vamos usar uma lista predefinida de itens que o jogador PODE tentar vender,
        # para garantir a ordem e quais itens são considerados.
        potential_sell_items = ["madeira", "ferro", "tecido", "pocao"] 

        for item_key in potential_sell_items:
            if item_key in self.player_in_dialogue.inventory and \
               self.player_in_dialogue.inventory[item_key] > 0:
                
                item_details_config = ITEM_DATA.get(item_key, {})
                npc_buy_price = item_details_config.get("preco_npc_paga_jogador")

                if npc_buy_price and npc_buy_price > 0: # NPC compra este item
                    sellable_items_count += 1
                    option_key_str = str(sellable_items_count)
                    item_name_display = item_details_config.get("nome_exibicao", item_key)
                    player_quantity = self.player_in_dialogue.inventory[item_key]
                    
                    option_text = f"{item_name_display} (Você tem: {player_quantity}) - Vender por {npc_buy_price}g"
                    self.dialogue_options_display.append(f"[{option_key_str}] {option_text}")
                    self._temp_sell_option_map[option_key_str] = item_key
        
        if sellable_items_count == 0:
            self.dialogue_options_display.append("(Você não tem nada que eu queira comprar agora.)")
        
        # Adiciona a opção fixa de voltar (definida no autômato para MENU_VENDA_ESCOLHER_ITEM)
        current_state_info = self.automaton.get(self.dialogue_state, {}) # Pega info do estado atual
        fixed_options = current_state_info.get("options", {}) # Pega as opções fixas (ex: {"9": "[Voltar...]"})
        for key, text in fixed_options.items():
            # Adiciona apenas se a chave numérica não colidir com as dinâmicas (improvável se usar '9')
            if key not in self._temp_sell_option_map: 
                self.dialogue_options_display.append(f"[{key}] {text}")

        #self._update_dialogue_content()