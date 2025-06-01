import random # Adicione esta importação se ainda não estiver lá
from .npc_base import NPCBase
from automatos.shop_npc_automaton import SHOP_NPC_AUTOMATON
from core.config import COLOR_SHOP_NPC # Importa a cor específica
from core.config import ITEM_DATA # Importa os dados dos itens

class NPCVendedor(NPCBase):
    def __init__(self, x, y, label="L"):
        super().__init__(x, y, npc_type="shop", label=label, color=COLOR_SHOP_NPC)
        self.automaton = SHOP_NPC_AUTOMATON # Atribui o autômato específico do vendedor

        # Atributos para controlar o comportamento dinâmico do vendedor
        self.chance_recusar_venda_aleatoria = 0.1 # 10% de chance de simplesmente não querer vender o item
        self.chance_conceder_desconto_persuasao = 0.6 # 60% de chance de dar desconto se o jogador persuadir
        self.chance_npc_fugir_ameaca = 0.4 # 40% de chance do NPC fugir se ameaçado
        #self.chance_ameaca_falhar_e_npc_irritar = 0.6 # 60% (do restante) chance do NPC se irritar se a ameaça não o fizer fugir
        
        # Você pode adicionar mais atributos aqui, como um pequeno "humor" que pode
        # influenciar essas chances ou os preços, mas vamos manter simples por enquanto.

    # ... (outros métodos do NPCVendedor, como os action_handlers, virão aqui depois) ...
    def handle_ameaca(self):
        """Lógica para processar a ameaça do jogador."""
        # print("DEBUG: NPCVendedor - Entrou em handle_ameaca")
        if random.random() < self.chance_npc_fugir_ameaca:
            self.dialogue_state = "FUGINDO"
            # Aqui você poderia adicionar lógica de jogo mais complexa, como:
            # - Marcar o NPC como "fugiu" para que ele desapareça do mapa.
            # - Impedir interações futuras por um tempo.
        else:
            # Se não fugiu, ele se irrita e expulsa o jogador.
            self.dialogue_state = "AMEACA_FRACASSADA"
        
        self._update_dialogue_content() # Atualiza a UI para o novo estado ("FUGINDO" ou "AMEACA_FRACASSADA")

    # npc_rpg/entities/npc_vendedor.py
# ... (imports e __init__ como antes) ...
# from core.config import ITEM_DATA # Certifique-se que ITEM_DATA está acessível se precisar de detalhes do item aqui

class NPCVendedor(NPCBase):
    def __init__(self, x, y, label="L"):
        # ... (seu __init__ existente com as chances) ...
        super().__init__(x, y, npc_type="shop", label=label, color=COLOR_SHOP_NPC)
        self.automaton = SHOP_NPC_AUTOMATON

        self.chance_recusar_venda_aleatoria = 0.1 
        self.chance_conceder_desconto_persuasao = 0.6 
        self.chance_npc_fugir_ameaca = 0.4

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

        # Guarda o item_key para _update_dialogue_content usar na formatação da msg do próximo estado
        self._context_item_key = item_key 

        if not item_key or preco_final is None or not self.player_in_dialogue:
            print(f"DEBUG: Erro em handle_tentativa_compra para estado '{self.dialogue_state}'. Dados incompletos.")
            # Define uma mensagem de erro direta e vai para um estado seguro
            self.dialogue_message = "Algo deu errado com minha loja!" # Mensagem direta
            self.dialogue_state = "INICIAL" 
            self._context_item_key = None # Limpa o contexto se houve erro
            self._update_dialogue_content()
            return

        item_config = ITEM_DATA.get(item_key)
        if not item_config:
            print(f"DEBUG: Item '{item_key}' não encontrado em ITEM_DATA durante handle_tentativa_compra.")
            self.dialogue_message = "Não reconheço esse item..." # Mensagem direta
            self.dialogue_state = "INICIAL"
            self._context_item_key = None # Limpa o contexto
            self._update_dialogue_content()
            return
        
        # item_nome_exibicao = item_config.get("nome_exibicao", item_key) # Não precisa mais aqui

        if self.player_in_dialogue.gold >= preco_final:
            if hasattr(self, 'chance_recusar_venda_aleatoria') and random.random() < self.chance_recusar_venda_aleatoria:
                self.dialogue_state = "RECUSANDO_VENDA_ALEATORIA"
                # A mensagem será formatada por _update_dialogue_content usando self._context_item_key
            else:
                self.player_in_dialogue.gold -= preco_final
                self.player_in_dialogue.inventory[item_key] = self.player_in_dialogue.inventory.get(item_key, 0) + 1
                self.dialogue_state = "COMPRA_SUCESSO"
                # A mensagem será formatada por _update_dialogue_content
        else:
            self.dialogue_state = "SEM_OURO"
            # A mensagem será formatada por _update_dialogue_content

        self._update_dialogue_content()