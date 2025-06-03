import random
from .npc_base import NPCBase
from automatos.ferreiro_npc_automato import FERREIRO_NPC
from core.config import COLOR_FORGE_NPC, ITEM_DATA

class NPCFerreiro(NPCBase):
    def __init__(self, x, y, label="F"):
        super().__init__(x, y, npc_type="forge", label=label, color=COLOR_FORGE_NPC)
        self.automaton = FERREIRO_NPC

        self._nenhum_item_para_melhorar_flag = False

        self.chance_aceitar_forja_direto = 0.6  
        self.chance_negociar_preco_forja = 0.3 
        self.chance_aceitar_melhoria = 0.8
        self.chance_sucesso_trabalho = 0.75
        self.chance_aceitar_barganha_forja = 0.4
        self.chance_aceitar_desafio = 0.5
        self.chance_jogador_vencer_desafio = 0.4
        self.custo_forjar_nova_arma_base = 100 
        self.custo_melhorar_arma_base = 50 
    
    def handle_pedido_forjar(self):
        rand_num = random.random()
    
        if rand_num < self.chance_aceitar_forja_direto:
            self.dialogue_state = "FORJANDO_ARMA"
        elif rand_num < self.chance_aceitar_forja_direto + self.chance_negociar_preco_forja:
            self.dialogue_state = "NEGOCIANDO_PRECO_FORJA"
        else:
            self.dialogue_state = "RECUSANDO_SERVICO_GERAL"
    
        self._message_is_final_from_handler = False
        self._update_dialogue_content()

    def handle_resultado_forja(self):
        if random.random() < self.chance_sucesso_trabalho:
            self.dialogue_state = "SUCESSO_FORJA_MELHORIA_DESAFIO"
        else:
            self.dialogue_state = "FALHA_FORJA_MELHORIA_DESAFIO"
        self._message_is_final_from_handler = False
        self._update_dialogue_content()
        
    def handle_pedido_melhorar(self):
        if random.random() < self.chance_aceitar_melhoria:
            self.dialogue_state = "ESCOLHER_ITEM_MELHORIA"
        else:
            self.dialogue_state = "RECUSANDO_SERVICO_GERAL"

        self._message_is_final_from_handler = False
        self._update_dialogue_content()
        
    def generate_melhoria_options_for_player(self):
        self.dialogue_options_display = []
        self._temp_upgrade_option_map = {}
        self._nenhum_item_para_melhorar_flag = False
            
        if not self.player_in_dialogue:
            current_state_info = self.automaton.get(self.dialogue_state, {})
            fixed_options = current_state_info.get("options", {})
            for key, text in fixed_options.items(): 
                self.dialogue_options_display.append(f"[{key}] {text}")
            return

        upgradable_items_count = 0
        potential_upgrade_items = ["espada"]
        for item_key in self.player_in_dialogue.inventory:
            if self.player_in_dialogue.inventory[item_key] > 0:
                item_details_config = ITEM_DATA.get(item_key, {})
                if item_details_config.get("melhoravel"):
                    upgradable_items_count += 1
                    option_key_str = str(upgradable_items_count)
                    item_name_display = item_details_config.get("nome_exibicao", item_key)
                    player_quantity = self.player_in_dialogue.inventory[item_key]
                    
                    option_text = f"Melhorar {item_name_display} (Você tem: {player_quantity})"
                    self.dialogue_options_display.append(f"[{option_key_str}] {option_text}")
                    self._temp_upgrade_option_map[option_key_str] = item_key
        
        current_state_info = self.automaton.get(self.dialogue_state, {})
        fixed_options = current_state_info.get("options", {})

        if upgradable_items_count == 0:
            self.dialogue_options_display.append("(Você não tem equipamentos melhoráveis no momento.)")
            self._nenhum_item_para_melhorar_flag = True
            #print(f"DEBUG_FERREIRO (generate_melhoria): Nenhum item. Flag = {self._nenhum_item_para_melhorar_flag}")
            for key, text in fixed_options.items():
                if key == "9":
                    self.dialogue_options_display.append(f"[{key}] Despedir-se")
                else: 
                    self.dialogue_options_display.append(f"[{key}] {text}")
        else:
            self._nenhum_item_para_melhorar_flag = False # Garante que está False se há itens
            #print(f"DEBUG_FERREIRO (generate_melhoria): Itens encontrados. Flag = {self._nenhum_item_para_melhorar_flag}") # DEBUG
            for key, text in fixed_options.items():
                if key not in self._temp_upgrade_option_map: 
                    self.dialogue_options_display.append(f"[{key}] {text}")
    
    def handle_resultado_melhoria(self):
        self._message_is_final_from_handler = True

        item_key_para_melhorar = self.active_transaction_item_key

        if not item_key_para_melhorar or not self.player_in_dialogue:
            self.dialogue_message = "Houve um erro ao tentar melhorar o item."
            self.dialogue_state = "ESCOLHER_ITEM_MELHORIA"
            self.active_transaction_item_key = None
            self._update_dialogue_content()
            return

        item_config = ITEM_DATA.get(item_key_para_melhorar)
        if not item_config or not item_config.get("melhoravel"):
            self.dialogue_message = f"Não sei como melhorar um(a) {item_config.get('nome_exibicao', item_key_para_melhorar)}."
            self.dialogue_state = "ESCOLHER_ITEM_MELHORIA"
            self._update_dialogue_content()
            return

        custo_ouro = item_config.get("custo_melhoria_ouro", 0)
        materiais_necessarios = item_config.get("materiais_melhoria", {})
        item_nome_exibicao = item_config.get("nome_exibicao", item_key_para_melhorar)

        tem_ouro_suficiente = self.player_in_dialogue.gold >= custo_ouro
        tem_materiais_suficientes = True
        materiais_faltando_str = []

        for mat_key, qtd_necessaria in materiais_necessarios.items():
            if self.player_in_dialogue.inventory.get(mat_key, 0) < qtd_necessaria:
                tem_materiais_suficientes = False
                mat_nome_display = ITEM_DATA.get(mat_key, {}).get("nome_exibicao", mat_key)
                materiais_faltando_str.append(f"{qtd_necessaria} {mat_nome_display}")
        
        if not tem_ouro_suficiente or not tem_materiais_suficientes:
            self.dialogue_state = "RECURSOS_INSUFICIENTES_MELHORIA"
            msg_erro = f"Para melhorar {item_nome_exibicao}, você precisa de: "
            if not tem_ouro_suficiente:
                msg_erro += f"{custo_ouro}g (Você tem {self.player_in_dialogue.gold}g). "
            if materiais_faltando_str:
                msg_erro += "Materiais: " + ", ".join(materiais_faltando_str) + "."
            self.dialogue_message = msg_erro.strip()
            self._update_dialogue_content()
            return

        self.player_in_dialogue.gold -= custo_ouro
        for mat_key, qtd_necessaria in materiais_necessarios.items():
            self.player_in_dialogue.inventory[mat_key] -= qtd_necessaria

        if random.random() < self.chance_sucesso_trabalho:
            self.dialogue_state = "SUCESSO_FORJA_MELHORIA_DESAFIO"
            self.dialogue_message = f"Consegui! Sua {item_nome_exibicao} foi aprimorada com maestria!"
            # print(f"DEBUG: {item_nome_exibicao} melhorada para o jogador (lógica de upgrade real a ser implementada).")
        else:
            self.dialogue_state = "FALHA_FORJA_MELHORIA_DESAFIO"
            self.dialogue_message = f"Maldição! A melhoria da sua {item_nome_exibicao} falhou. Os materiais foram perdidos, mas seu equipamento está intacto."

        self._update_dialogue_content()

    def handle_aceitar_desafio(self):
        if random.random() < self.chance_aceitar_desafio:
            self.dialogue_state = "ACEITANDO_DESAFIO"
        else:
            self.dialogue_state = "RECUSANDO_SERVICO_GERAL"

        self._message_is_final_from_handler = False
        self._update_dialogue_content()
    
    def handle_resultado_luta_desafio(self):
        self._message_is_final_from_handler = True 
        if random.random() < self.chance_jogador_vencer_desafio:
            self.dialogue_state = "SUCESSO_FORJA_MELHORIA_DESAFIO"
            self.dialogue_message = "Você luta bem! Admito a derrota. É forte como meu aço!"
            print(f"DEBUG: Jogador venceu o desafio contra o Ferreiro.")
        else:
            self.dialogue_state = "FALHA_FORJA_MELHORIA_DESAFIO"
            self.dialogue_message = "Hah! Precisa de mais treino para superar minhas habilidades! Volte quando for mais forte."
            print(f"DEBUG: Jogador perdeu o desafio contra o Ferreiro.")

        self._update_dialogue_content()