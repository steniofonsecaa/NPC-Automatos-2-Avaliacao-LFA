import random 
from .npc_base import NPCBase
from automatos.vendedor_npc_automato import VENDEDOR_NPC_AUTOMATO
from core.config import COLOR_SHOP_NPC
from core.config import ITEM_DATA

class NPCVendedor(NPCBase):
    def __init__(self, x, y, label="L"):
        super().__init__(x, y, npc_type="shop", label=label, color=COLOR_SHOP_NPC)
        self.automaton = VENDEDOR_NPC_AUTOMATO

        self.chance_recusar_venda_aleatoria = 0.1 
        self.chance_conceder_desconto_persuasao = 0.6 
        self.chance_npc_fugir_ameaca = 0.4
        self._message_is_final_from_handler = False

        self._temp_sell_option_map = {}

    def handle_ameaca(self):
        if random.random() < self.chance_npc_fugir_ameaca:
            self.dialogue_state = "FUGINDO"
        else:
            self.dialogue_state = "AMEACA_FRACASSADA"
        self._update_dialogue_content()

    def handle_persuasao_desconto(self):

        current_state_info = self.automaton.get(self.dialogue_state)
        item_key = current_state_info.get("item_key")

        if not item_key:
            print(f"AVISO: handle_persuasao_desconto chamado sem 'item_key' no estado {self.dialogue_state}")
            self.dialogue_state = "INICIAL"
            self._update_dialogue_content()
            return

        if random.random() < self.chance_conceder_desconto_persuasao:

            next_state_name = f"DESCONTO_OFERECIDO_{item_key.upper()}"
            if next_state_name not in self.automaton:
                print(f"AVISO: Estado de desconto '{next_state_name}' não encontrado no autômato. Falhando persuasão.")
                next_state_name = f"NEGOCIACAO_FALHOU_{item_key.upper()}"
                if next_state_name not in self.automaton:
                    print(f"AVISO CRÍTICO: Estado de falha '{next_state_name}' também não encontrado!")
                    self.dialogue_state = "INICIAL"
                    self._update_dialogue_content()
                    return
            self.dialogue_state = next_state_name
        else:
            next_state_name = f"NEGOCIACAO_FALHOU_{item_key.upper()}"
            if next_state_name not in self.automaton:
                print(f"AVISO CRÍTICO: Estado de falha '{next_state_name}' não encontrado no autômato após falha na persuasão!")
                self.dialogue_state = "INICIAL"
                self._update_dialogue_content()
                return
            self.dialogue_state = next_state_name
            
        self._update_dialogue_content()

    def handle_tentativa_compra(self):
        current_state_info = self.automaton.get(self.dialogue_state)
        item_key = current_state_info.get("item_key")
        preco_final = current_state_info.get("preco_final_compra_jogador")
        self._message_is_final_from_handler = True

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
        self.dialogue_options_display = [] 
        self._temp_sell_option_map = {}
        
        if not self.player_in_dialogue:
            current_state_info = self.automaton.get(self.dialogue_state, {})
            fixed_options = current_state_info.get("options", {})
            for key, text in fixed_options.items():
                self.dialogue_options_display.append(f"[{key}] {text}")
            return

        sellable_items_count = 0
        potential_sell_items = ["madeira", "ferro", "tecido", "pocao"] 

        for item_key in potential_sell_items:
            if item_key in self.player_in_dialogue.inventory and \
               self.player_in_dialogue.inventory[item_key] > 0:
                
                item_details_config = ITEM_DATA.get(item_key, {})
                npc_buy_price = item_details_config.get("preco_npc_paga_jogador")

                if npc_buy_price and npc_buy_price > 0:
                    sellable_items_count += 1
                    option_key_str = str(sellable_items_count)
                    item_name_display = item_details_config.get("nome_exibicao", item_key)
                    player_quantity = self.player_in_dialogue.inventory[item_key]
                    
                    option_text = f"{item_name_display} (Você tem: {player_quantity}) - Vender por {npc_buy_price}g"
                    self.dialogue_options_display.append(f"[{option_key_str}] {option_text}")
                    self._temp_sell_option_map[option_key_str] = item_key
        
        if sellable_items_count == 0:
            self.dialogue_options_display.append("(Você não tem nada que eu queira comprar agora.)")
        
        current_state_info = self.automaton.get(self.dialogue_state, {}) 
        fixed_options = current_state_info.get("options", {}) 
        for key, text in fixed_options.items():
            if key not in self._temp_sell_option_map: 
                self.dialogue_options_display.append(f"[{key}] {text}")

        #self._update_dialogue_content()