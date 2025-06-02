from .npc_base import NPCBase
from automatos.informante_npc_automato import INFORMANTE_NPC_AUTOMATON, PERGUNTAS_DISPONIVEIS_INFORMANTE, RESPOSTAS_INFORMANTE
from core.config import COLOR_INFO_NPC 

class NPCInformante(NPCBase):
    def __init__(self, x, y, label="I"):
        super().__init__(x, y, npc_type="info", label=label, color=COLOR_INFO_NPC)
        
        self.automaton = INFORMANTE_NPC_AUTOMATON
        self.perguntas_disponiveis = PERGUNTAS_DISPONIVEIS_INFORMANTE
        self.respostas_perguntas = RESPOSTAS_INFORMANTE

        self._temp_question_option_map = {}
    
    def generate_informant_questions(self):
        # print("DEBUG: Informante - Entrou em generate_informant_questions")
        self.dialogue_options_display = []
        self._temp_question_option_map = {}

        if not self.player_in_dialogue:
            current_state_info = self.automaton.get(self.dialogue_state, {})
            fixed_options = current_state_info.get("options", {})
            for key, text in fixed_options.items():
                self.dialogue_options_display.append(f"[{key}] {text}")
            return

        question_option_count = 0
        for topic_key in self.perguntas_disponiveis:
            question_option_count += 1
            option_key_str = str(question_option_count)
            
            display_text = topic_key.replace("_", " ").capitalize()
            
            self.dialogue_options_display.append(f"[{option_key_str}] Sobre: {display_text}")
            self._temp_question_option_map[option_key_str] = topic_key
            
            if question_option_count >= 8: # Permite opções de 1 a 8
                break 
        
        if question_option_count == 0:
            self.dialogue_options_display.append("(Parece que esgotei meus tópicos por enquanto.)")

        current_state_info = self.automaton.get(self.dialogue_state, {})
        fixed_options = current_state_info.get("options", {})
        for key, text in fixed_options.items():
            if key not in self._temp_question_option_map: 
                self.dialogue_options_display.append(f"[{key}] {text}")
    
    def handle_escolha_pergunta(self):
        # print(f"DEBUG: Informante - Entrou em handle_escolha_pergunta. Tópico ativo: {self.active_transaction_item_key}")
        self._message_is_final_from_handler = True

        chosen_topic_key = self.active_transaction_item_key

        if chosen_topic_key and chosen_topic_key in self.respostas_perguntas:
            self.dialogue_message = self.respostas_perguntas[chosen_topic_key]
        else:
            self.dialogue_message = "Hmm, sobre isso eu não tenho muita informação no momento."
            print(f"AVISO: Tópico '{chosen_topic_key}' não encontrado em self.respostas_perguntas.")

        self.dialogue_state = "EXIBINDO_RESPOSTA"
        
        self._update_dialogue_content()
