import pyxel
import random

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 160
TILE_SIZE = 8

SHOP_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Ola! Bem-vindo, viajante. O que você deseja:",
        "options": {"1": "Comprar", "2": "Vender", "3": "Sair"},
        "transitions": {"1": "MENU_COMPRA", "2": "MENU_VENDA", "3": "FIM"}
    },
    "MENU_COMPRA": {
        "message": "Comprar: [1] Pocao (10g), [2] Espada (50g), [3] Voltar.",
        "options": {"1": "Poção", "2": "Espada", "3": "Voltar"},
        "transitions": {"1": "POCAO_COMPRADA", "2": "ESPADA_COMPRADA", "3": "INICIAL"}
    },
    "MENU_VENDA": {
        "message": "Vender ainda nao implementado. [1] Voltar.",
        "options": {"1": "Voltar"},
        "transitions": {"1": "INICIAL"}
    },
    "POCAO_COMPRADA": {
        "message": "Voce comprou uma Pocao! (10g). [1] Continuar.",
        "options": {"1": "Continuar"},
        "transitions": {"1": "MENU_COMPRA"} # Volta para o menu de compra
    },
    "ESPADA_COMPRADA": {
        "message": "Voce comprou uma Espada! (50g). [1] Continuar.",
        "options": {"1": "Continuar"},
        "transitions": {"1": "MENU_COMPRA"} # Volta para o menu de compra
    },
    "FIM": {
        "message": "Ate logo!",
        "options": {}, # Sem opções, finaliza o diálogo
        "transitions": {}
    }
}

# 0 = chão (verde), 1 = muro (marrom)
MAP = [
    [1]*20,
] + [
    [1] + [0]*18 + [1] for _ in range(18)
] + [
    [1]*20,
]

def is_blocked(x, y, blocked_positions):
    # Verifica colisão com paredes (baseado no grid)
    col = x // TILE_SIZE
    row = y // TILE_SIZE
    if not (0 <= row < len(MAP) and 0 <= col < len(MAP[0])):
        return True
    if MAP[row][col] == 1:
        return True

    # Verifica colisão com NPCs (pixel-perfect)
    player_rect = (x, y, TILE_SIZE, TILE_SIZE)
    for npc_x, npc_y in blocked_positions:
        npc_rect = (npc_x * TILE_SIZE, npc_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if (player_rect[0] < npc_rect[0] + npc_rect[2] and
            player_rect[0] + player_rect[2] > npc_rect[0] and
            player_rect[1] < npc_rect[1] + npc_rect[3] and
            player_rect[1] + player_rect[3] > npc_rect[1]):
            return True
    return False

class Player:
    def __init__(self):
        self.x = 40
        self.y = 40
        self.color = 12  # Azul claro para o jogador
        self.char = "P" # Não está sendo usado para desenhar, mas pode ser útil

        # Ouro e Inventário
        self.gold = random.randint(200, 500) # Ouro inicial entre 200 e 500
        self.inventory = {
            "madeira": random.randint(0, 10),
            "ferro": random.randint(0, 5),
            "tecido": random.randint(0, 9),
            "pocao": random.randint(0, 5), # Para "poções"
            "espada": 0 # Espadas compradas na loja, começa com 0
        }

    def update(self, blocked_positions):
        dx = dy = 0
        if pyxel.btn(pyxel.KEY_LEFT): dx = -1
        if pyxel.btn(pyxel.KEY_RIGHT): dx = 1
        if pyxel.btn(pyxel.KEY_UP): dy = -1
        if pyxel.btn(pyxel.KEY_DOWN): dy = 1

        new_x = self.x + dx
        new_y = self.y + dy

        # Colisão separada para X e Y para deslizar nas paredes
        if not is_blocked(new_x, self.y, blocked_positions):
            self.x = new_x
        if not is_blocked(self.x, new_y, blocked_positions):
            self.y = new_y

    def draw(self):
        pyxel.rect(self.x, self.y, TILE_SIZE, TILE_SIZE, self.color)
        # pyxel.text(self.x + 2, self.y + 2, self.char, 0)

class NPC:
    def __init__(self, x, y, npc_type, label):
        self.x = x
        self.y = y
        self.type = npc_type
        self.label = label
        self.color = {"shop": 8, "forge": 10, "info": 7}[npc_type]

        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None # Referência ao jogador

        if self.type == "shop":
            self.automaton = SHOP_NPC_AUTOMATON
        else:
            self.automaton = None

    # ... (draw e get_tile_pos permanecem iguais) ...
    def draw(self):
        pyxel.rect(self.x, self.y, TILE_SIZE, TILE_SIZE, self.color)
        pyxel.text(self.x + 2, self.y + 2, self.label, 0)

    def get_tile_pos(self):
        return self.x // TILE_SIZE, self.y // TILE_SIZE
    
    def start_dialogue(self, player_obj): # Modificado para aceitar o jogador
        if not self.automaton:
            return False
        
        self.player_in_dialogue = player_obj # Armazena o jogador
        self.is_dialogue_active = True
        self.dialogue_state = "INICIAL"
        self._update_dialogue_content()
        return True

    def _update_dialogue_content(self):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info:
            self.end_dialogue()
            return

        # --- LÓGICA DE COMPRA/VENDA (A SER IMPLEMENTADA AQUI OU EM PROCESS_PLAYER_CHOICE) ---
        # Exemplo de como o autômato pode se tornar dinâmico com base no jogador:
        current_message = state_info["message"]
        if self.dialogue_state == "POCAO_COMPRADA": # Supondo que a transação já ocorreu (precisaria de mais lógica)
            # Este é apenas um exemplo, a lógica de transação real (verificar ouro, etc.)
            # seria mais complexa e provavelmente ocorreria ANTES de chegar neste estado "BOUGHT_POTION"
            # ou o estado "BOUGHT_POTION" seria alcançado APÓS uma transação bem-sucedida.
            # current_message = f"Pocao adicionada! Ouro: {self.player_in_dialogue.gold}"
            pass # A lógica de transação real é mais complexa

        self.dialogue_message = current_message
        self.dialogue_options_display = []
        for key, text in state_info["options"].items():
            self.dialogue_options_display.append(f"[{key}] {text}")

    def process_player_choice(self, choice_key):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info or choice_key not in state_info["transitions"]:
            return

        # --- LÓGICA DE TRANSAÇÃO (EXEMPLO PARA QUANDO O JOGADOR ESCOLHE COMPRAR ALGO) ---
        next_state_key = state_info["transitions"][choice_key]
        
        # Se a escolha leva a um estado de "compra efetivada"
        if self.dialogue_state == "MENU_COMPRA":
            item_cost = 0
            item_name = None
            if choice_key == "1": # Escolheu Poção
                item_cost = 10 # Definido no autômato visualmente, mas precisa estar na lógica
                item_name = "pocao"
            elif choice_key == "2": # Escolheu Espada
                item_cost = 50
                item_name = "espada"

            if item_name and self.player_in_dialogue:
                if self.player_in_dialogue.gold >= item_cost:
                    # Transição para o estado de item comprado (BOUGHT_POTION, BOUGHT_SWORD)
                    self.dialogue_state = next_state_key 
                    # Ação de compra (seria melhor em um método separado ou no novo estado)
                    # self.player_in_dialogue.gold -= item_cost
                    # self.player_in_dialogue.inventory[item_name] += 1
                    # A mensagem de "Você comprou X" já está no estado BOUGHT_POTION/SWORD
                else:
                    # Ouro insuficiente, poderia ir para um estado "NO_GOLD" ou apenas mostrar msg
                    # Por enquanto, vamos apenas impedir a transição para "BOUGHT_X" e voltar ao BUY_MENU
                    # ou mostrar uma mensagem temporária (mais complexo sem alterar muito o autômato atual).
                    # Vamos simplificar: o autômato atual AINDA não lida com a falha na compra.
                    # A mensagem de "comprou" aparecerá mesmo sem ouro. ISSO PRECISA SER CORRIGIDO.
                    self.dialogue_state = next_state_key # Transita mesmo sem ouro por enquanto
            else: # Escolheu "Voltar" ou outra opção
                 self.dialogue_state = next_state_key
        else: # Transição normal para outros estados
            self.dialogue_state = next_state_key
            
        self._update_dialogue_content()


    def end_dialogue(self):
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []
        self.player_in_dialogue = None # Limpa a referência

class Game:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="NPC com Automato e Mochila")
        self.player = Player()
        self.npcs = [
            NPC(16, 16, "shop", "L"),
            NPC(136, 16, "info", "I"),
            NPC(16, 136, "forge", "F"),
        ]
        self.active_npc_interaction = None
        self.show_inventory_ui = False # Nova flag para a UI da mochila
        pyxel.run(self.update, self.draw)

    def update(self):
        # Tecla para mostrar/esconder a mochila
        if pyxel.btnp(pyxel.KEY_M):
            self.show_inventory_ui = not self.show_inventory_ui

        # Se a mochila estiver visível ou diálogo ativo, pausamos outras ações
        if self.show_inventory_ui:
            # Nenhuma outra atualização de jogo enquanto a mochila estiver aberta
            # (exceto fechar a mochila com 'M' novamente, já tratado acima)
            return # Pula o resto do update

        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # Modo de Diálogo Ativo
            # ... (lógica do diálogo permanece a mesma) ...
            if pyxel.btnp(pyxel.KEY_1):
                self.active_npc_interaction.process_player_choice("1")
            elif pyxel.btnp(pyxel.KEY_2):
                self.active_npc_interaction.process_player_choice("2")
            elif pyxel.btnp(pyxel.KEY_3):
                self.active_npc_interaction.process_player_choice("3")

            if self.active_npc_interaction.dialogue_state == "FIM":
                # Para sair do estado END (despedida), o jogador pode pressionar qualquer tecla de opção ou E/Q
                # Ou podemos ter um pequeno delay antes de fechar automaticamente.
                # Por agora, vamos manter a lógica de pressionar uma tecla para fechar após a msg "END"
                if pyxel.btnp(pyxel.KEY_1) or pyxel.btnp(pyxel.KEY_2) or pyxel.btnp(pyxel.KEY_3) or pyxel.btnp(pyxel.KEY_E) or pyxel.btnp(pyxel.KEY_Q):
                    self.active_npc_interaction.end_dialogue()
                    self.active_npc_interaction = None
        else:
            # Modo de Exploração
            blocked_positions = [npc.get_tile_pos() for npc in self.npcs]
            self.player.update(blocked_positions)

            current_near_npc = None
            for npc in self.npcs:
                if is_near(self.player, npc):
                    current_near_npc = npc
                    break
            
            if current_near_npc and pyxel.btnp(pyxel.KEY_E):
                if current_near_npc.type == "shop":
                    # --- INÍCIO DA LÓGICA DE COMPRA (PRECISA SER EXPANDIDA) ---
                    # Antes de iniciar o diálogo da loja, poderíamos verificar o ouro,
                    # mas a verificação real acontece ao tentar comprar um item específico.
                    # O autômato da loja agora precisa de acesso ao jogador para verificar/modificar ouro/inventário.
                    # Passaremos o objeto player para o NPC quando o diálogo começar ou para processar escolhas.
                    # Por ora, apenas iniciamos o diálogo. A integração virá no autômato.
                    # --- FIM DA LÓGICA DE COMPRA ---
                    self.active_npc_interaction = current_near_npc
                    # Passamos o jogador para o NPC para que o autômato possa interagir com o inventário/ouro
                    self.active_npc_interaction.start_dialogue(self.player) # Modificado para passar o jogador
                else:
                    print(f"Interagindo com {self.get_npc_name(current_near_npc)} (ainda sem automato complexo)")

            if self.active_npc_interaction and not current_near_npc:
                 if not self.active_npc_interaction.is_dialogue_active:
                    self.active_npc_interaction = None
    
    # ... (get_npc_name permanece o mesmo) ...
    def get_npc_name(self, npc):
        return {
            "shop": "Vendedor",
            "forge": "Ferreiro",
            "info": "Informante"
        }.get(npc.type, "NPC")

    def draw(self):
        pyxel.cls(0)
        # Desenha o mapa
        for row_idx, row in enumerate(MAP):
            for col_idx, tile in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                color = 6 if tile == 1 else 3
                pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, color)

        # Desenha NPCs
        for npc in self.npcs:
            npc.draw()

        # Desenha Player
        self.player.draw()

        # Exibe Ouro do Jogador
        gold_text = f"Ouro: {self.player.gold}"
        pyxel.text(SCREEN_WIDTH - len(gold_text) * pyxel.FONT_WIDTH - 5, 5, gold_text, 7) # 7 = Branco

        # Lógica de UI de Interação (Diálogo ou Mochila)
        if self.show_inventory_ui:
            # Desenha a UI da Mochila
            box_w = 100
            box_h = 80
            box_x = (SCREEN_WIDTH - box_w) // 2
            box_y = (SCREEN_HEIGHT - box_h) // 2
            
            pyxel.rect(box_x, box_y, box_w, box_h, 1) # Fundo azul escuro
            pyxel.rectb(box_x, box_y, box_w, box_h, 7) # Borda branca
            pyxel.text(box_x + 5, box_y + 5, "Mochila:", 7)

            item_y_offset = box_y + 15
            for i, (item_name, quantity) in enumerate(self.player.inventory.items()):
                display_name = item_name.capitalize()
                pyxel.text(box_x + 5, item_y_offset + (i * 10), f"- {display_name}: {quantity}", 7)
            
            pyxel.text(box_x + 5, box_y + box_h - 10, "[M] Fechar", 7)

        elif self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # Desenha a UI de Diálogo
            # ... (lógica de desenhar diálogo permanece a mesma) ...
            npc = self.active_npc_interaction
            dialog_box_y = SCREEN_HEIGHT - 40
            pyxel.rect(5, dialog_box_y - 2, SCREEN_WIDTH - 10, 32, 1)
            pyxel.rectb(5, dialog_box_y - 2, SCREEN_WIDTH - 10, 32, 7)
            pyxel.text(10, dialog_box_y, npc.dialogue_message, 7)
            opt_y_start = dialog_box_y + 10
            for i, opt_text in enumerate(npc.dialogue_options_display):
                pyxel.text(10, opt_y_start + (i * 8), opt_text, 7)
        else:
            # Mostra "Pressione E para interagir"
            # ... (lógica de mostrar "E para interagir" permanece a mesma) ...
            temp_near_npc = None
            for npc_check in self.npcs:
                if is_near(self.player, npc_check):
                    temp_near_npc = npc_check
                    break
            if temp_near_npc:
                pyxel.text(5, SCREEN_HEIGHT - 15, f"[E] Interagir com {self.get_npc_name(temp_near_npc)}", 7)

def is_near(player, npc, distance=10):
    """
    Verifica se o jogador está próximo o suficiente do NPC para interagir.
    """
    dx = player.x - npc.x
    dy = player.y - npc.y
    return (dx * dx + dy * dy) <= (distance * distance)

Game()