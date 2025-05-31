import pyxel

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 160
TILE_SIZE = 8

SHOP_NPC_AUTOMATON = {
    "INITIAL": {
        "message": "Ola! Bem-vindo. Deseja:",
        "options": {"1": "Comprar", "2": "Vender", "3": "Sair"},
        "transitions": {"1": "BUY_MENU", "2": "SELL_MENU", "3": "END"}
    },
    "BUY_MENU": {
        "message": "Comprar: [1] Pocao (10g), [2] Espada (50g), [3] Voltar.",
        "options": {"1": "Poção", "2": "Espada", "3": "Voltar"},
        "transitions": {"1": "BOUGHT_POTION", "2": "BOUGHT_SWORD", "3": "INITIAL"}
    },
    "SELL_MENU": {
        "message": "Vender ainda nao implementado. [1] Voltar.",
        "options": {"1": "Voltar"},
        "transitions": {"1": "INITIAL"}
    },
    "BOUGHT_POTION": {
        "message": "Voce comprou uma Pocao! (10g). [1] Continuar.",
        "options": {"1": "Continuar"},
        "transitions": {"1": "BUY_MENU"} # Volta para o menu de compra
    },
    "BOUGHT_SWORD": {
        "message": "Voce comprou uma Espada! (50g). [1] Continuar.",
        "options": {"1": "Continuar"},
        "transitions": {"1": "BUY_MENU"} # Volta para o menu de compra
    },
    "END": {
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
        self.color = 12
        self.char = "P"

    def update(self, blocked_positions):
        dx = dy = 0
        if pyxel.btn(pyxel.KEY_LEFT): dx = -1  # Movimento de 1 pixel para a esquerda
        if pyxel.btn(pyxel.KEY_RIGHT): dx = 1   # Movimento de 1 pixel para a direita
        if pyxel.btn(pyxel.KEY_UP): dy = -1     # Movimento de 1 pixel para cima
        if pyxel.btn(pyxel.KEY_DOWN): dy = 1    # Movimento de 1 pixel para baixo

        new_x = self.x + dx
        new_y = self.y + dy

        if not is_blocked(new_x, self.y, blocked_positions):
            self.x = new_x
        if not is_blocked(self.x, new_y, blocked_positions):
            self.y = new_y

    def draw(self):
        pyxel.rect(self.x, self.y, TILE_SIZE, TILE_SIZE, self.color)
        pyxel.text(self.x + 2, self.y + 2, self.char, 0)

class NPC:
    def __init__(self, x, y, npc_type, label):
        self.x = x
        self.y = y
        self.type = npc_type
        self.label = label
        self.color = {"shop": 8, "forge": 10, "info": 7}[npc_type]

        # Atributos para o autômato de diálogo
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = [] # Lista de strings formatadas para exibição

        if self.type == "shop":
            self.automaton = SHOP_NPC_AUTOMATON
        else:
            self.automaton = None # Outros NPCs não usam este autômato por enquanto

    def draw(self):
        pyxel.rect(self.x, self.y, TILE_SIZE, TILE_SIZE, self.color)
        pyxel.text(self.x + 2, self.y + 2, self.label, 0)

    def get_tile_pos(self):
        return self.x // TILE_SIZE, self.y // TILE_SIZE

    def start_dialogue(self):
        if not self.automaton:
            return False # Não há autômato definido para este NPC
        
        self.is_dialogue_active = True
        self.dialogue_state = "INITIAL" # Estado inicial do autômato
        self._update_dialogue_content()
        return True

    def _update_dialogue_content(self):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info:
            self.end_dialogue() # Estado inválido, encerra
            return

        self.dialogue_message = state_info["message"]
        self.dialogue_options_display = []
        for key, text in state_info["options"].items():
            self.dialogue_options_display.append(f"[{key}] {text}")

        if not state_info["options"]: # Se não há opções, é um estado final de fala
            # Poderia ter uma lógica para auto-avançar ou esperar um "continuar" genérico
            # Por enquanto, se não há opções, o jogador precisará sair manualmente ou o estado precisa transitar para END
            if self.dialogue_state == "END": # Se chegou ao estado END, o diálogo efetivamente acabou.
                 pass # A flag is_dialogue_active será controlada pelo Game para realmente sair.


    def process_player_choice(self, choice_key):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info or choice_key not in state_info["transitions"]:
            return # Escolha inválida para o estado atual

        self.dialogue_state = state_info["transitions"][choice_key]
        self._update_dialogue_content()

        if self.dialogue_state == "END":
            # O Game vai verificar isso para desativar o modo de diálogo.
            # A mensagem de "END" será exibida, e na próxima interação o diálogo recomeça.
            # Ou podemos fazer com que end_dialogue() seja chamado externamente.
            pass

    def end_dialogue(self):
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []

def is_near(a, b, distance=8):
    return abs(a.x - b.x) <= distance and abs(a.y - b.y) <= distance

class Game:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="NPC com Automato") # Adicionado title aqui
        # pyxel.title = "NPC Interação por Proximidade" # Removido pois é melhor no init
        self.player = Player()
        self.npcs = [
            NPC(16, 16, "shop", "L"),    # Vendedor
            NPC(136, 16, "info", "I"),   # Informante
            NPC(16, 136, "forge", "F"),  # Ferreiro
        ]
        self.active_npc_interaction = None # NPC com quem o jogador está interagindo (em diálogo)
        # self.message = "" # Removido, pois o diálogo do NPC controlará as mensagens principais
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # Modo de Diálogo Ativo
            # O jogador não se move, apenas interage com o diálogo
            if pyxel.btnp(pyxel.KEY_1):
                self.active_npc_interaction.process_player_choice("1")
            elif pyxel.btnp(pyxel.KEY_2):
                self.active_npc_interaction.process_player_choice("2")
            elif pyxel.btnp(pyxel.KEY_3):
                self.active_npc_interaction.process_player_choice("3")
            # Adicione mais teclas se suas opções usarem (ex: 4, 5...)

            # Se o diálogo do NPC chegou ao estado final "END"
            if self.active_npc_interaction.dialogue_state == "END":
                 # Damos um pequeno tempo para ler a msg de despedida, ou podemos ter um btn p/ fechar
                 # Por agora, se apertar uma tecla de opção novamente (ou uma tecla 'sair' dedicada) ele sai
                 # Vamos simplificar: se o estado é END e alguma tecla de opção é pressionada, sai
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
                if current_near_npc.type == "shop": # Apenas o shop usa o novo sistema por enquanto
                    self.active_npc_interaction = current_near_npc
                    self.active_npc_interaction.start_dialogue()
                else:
                    # Lógica antiga para outros NPCs (se houver)
                    # self.message = f"Falando com {self.get_npc_name(current_near_npc)} (simples)"
                    print(f"Interagindo com {self.get_npc_name(current_near_npc)} (ainda sem automato complexo)")


            # Limpar diálogo se o jogador se afastar e não estiver em modo de interação
            if self.active_npc_interaction and not current_near_npc:
                 if not self.active_npc_interaction.is_dialogue_active: # Garante que não estamos no meio de um diálogo ativo
                    self.active_npc_interaction = None


    def get_npc_name(self, npc): # Mantido para referências futuras ou outros NPCs
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
                color = 6 if tile == 1 else 3 # marrom para muro, verde para chão
                pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, color)

        # Desenha NPCs
        for npc in self.npcs:
            npc.draw()

        # Desenha Player
        self.player.draw()

        # Lógica de UI de Interação
        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # Desenha a UI de Diálogo
            npc = self.active_npc_interaction
            
            # Caixa de diálogo simples no rodapé
            dialog_box_y = SCREEN_HEIGHT - 40
            pyxel.rect(5, dialog_box_y - 2, SCREEN_WIDTH - 10, 32, 1) # Caixa de fundo azul escuro
            pyxel.rectb(5, dialog_box_y - 2, SCREEN_WIDTH - 10, 32, 7) # Borda branca

            pyxel.text(10, dialog_box_y, npc.dialogue_message, 7) # Mensagem do NPC
            
            opt_y_start = dialog_box_y + 10
            for i, opt_text in enumerate(npc.dialogue_options_display):
                pyxel.text(10, opt_y_start + (i * 8), opt_text, 7) # Opções do jogador

        else:
            # Mostra "Pressione E para interagir" se perto de algum NPC
            temp_near_npc = None
            for npc_check in self.npcs:
                if is_near(self.player, npc_check):
                    temp_near_npc = npc_check
                    break
            if temp_near_npc:
                pyxel.text(5, SCREEN_HEIGHT - 15, f"[E] Interagir com {self.get_npc_name(temp_near_npc)}", 7)

        # Mensagem global (se ainda quiser usar para algo, como compras)
        # if self.message:
        # pyxel.text(5, SCREEN_HEIGHT - 8, self.message, 10)

Game()