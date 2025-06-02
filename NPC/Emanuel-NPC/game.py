import pyxel
import NpcMercante
import NpcFerreiro
import NpcInformante
import random
import Imagens
def converter_ap_para_dialogo(estados, transicoes, mensagens_customizadas):
    ap_dict = {}

    # Usa as perguntas do arquivo do NPC
    perguntas_possiveis = NpcInformante.perguntas_possiveis

    for estado in estados:
        ap_dict[estado] = {
            "message": mensagens_customizadas.get(estado, f"Você está no estado {estado}."),
            "options": {},
            "transitions": {}
        }

        # Se for um estado de resposta ou espera, adiciona as opções de perguntas
        if estado in ['Respondendo', 'Esperando']:
            for i, pergunta in enumerate(perguntas_possiveis, start=1):
                ap_dict[estado]["options"][str(i)] = f"perguntar sobre {pergunta}"
                ap_dict[estado]["transitions"][str(i)] = 'Respondendo'

            # Adiciona a opção de sair
            idx = str(len(perguntas_possiveis) + 1)
            ap_dict[estado]["options"][idx] = "sair"
            ap_dict[estado]["transitions"][idx] = 'Encerrado'

        elif estado == 'Encerrado':
            ap_dict[estado]["options"] = {}
            ap_dict[estado]["transitions"] = {}

    return ap_dict
def converter_afn_para_dialogo(estados, transicoes, mensagens_customizadas):
    afn_dict = {}

    for estado in estados:
        afn_dict[estado] = {
            "message": mensagens_customizadas.get(estado, f"Você está no estado {estado}."),
            "options": {},
            "transitions": {},
        }

    for (origem, entrada), destinos in transicoes.items():
        # Gera a chave de opção (1, 2, 3...)
        option_key = str(len(afn_dict[origem]["options"]) + 1)
        afn_dict[origem]["options"][option_key] = entrada
        afn_dict[origem]["transitions"][option_key] = destinos  # Mantém como lista de estados!

    return afn_dict
def converter_afd_para_dialogo(estados, transicoes, mensagens_customizadas):
    automato = {}
    for estado in estados:
        automato[estado] = {
            "message": mensagens_customizadas.get(estado, f"Você está no estado {estado}."),
            "options": {},
            "transitions": {}
        }
    for origem, destino, entrada in transicoes:
        option_key = str(len(automato[origem]["options"]) + 1)
        automato[origem]["options"][option_key] = entrada
        automato[origem]["transitions"][option_key] = destino
    return automato

SCREEN_WIDTH = 180
SCREEN_HEIGHT = 200
TILE_SIZE = 10
def text_width(text):
    return len(text) * 4  # 4 pixels por caractere

def wrap_text(text, max_width):
    lines = []
    current_line = ""
    for word in text.split():
        if text_width(current_line + " " + word) <= max_width:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def blt_scale2x(x, y, banco, u, v, w, h):
    for i in range(w):
        for j in range(h):
            color = pyxel.images[banco].pget(u + i, v + j)
            if color != 0:  # Ignora cor 0 (transparente)
                pyxel.pset(x + i * 2, y + j * 2, color)
                pyxel.pset(x + i * 2 + 1, y + j * 2, color)
                pyxel.pset(x + i * 2, y + j * 2 + 1, color)
                pyxel.pset(x + i * 2 + 1, y + j * 2 + 1, color)
            
# Carregar AFDs de NPCs
NPC_AUTOMATONS = {
    NpcMercante.tipo: converter_afd_para_dialogo(
        NpcMercante.estados,
        NpcMercante.transicoes,
        NpcMercante.mensagens
    ),
        NpcFerreiro.tipo: converter_afn_para_dialogo(
        NpcFerreiro.estados,
        NpcFerreiro.transicoes,
        NpcFerreiro.mensagens_customizadas
    ),
    NpcInformante.tipo: converter_ap_para_dialogo(
    NpcInformante.estados,
    NpcInformante.transicoes,
    NpcInformante.mensagens_customizadas
    ),
    # "info": ...
}
# Definindo o autômato de diálogo do NPC mercante

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
        self.resumo_final = ""
        self.dialogue_end_timer = 0
        self.type = npc_type
        self.label = label
        self.color = {"shop": 8, "forge": 10, "info": 7}.get(npc_type, 9)

        # Atributos para o autômato de diálogo
        self.is_dialogue_active = False
        self.dialogue_state = None
        self.dialogue_message = ""
        self.dialogue_options_display = []

        self.automaton = NPC_AUTOMATONS.get(npc_type)
        if not self.automaton:
            print(f"Erro: Autômato não definido para o NPC do tipo '{npc_type}'")

    def draw(self):
        pyxel.rect(self.x, self.y, TILE_SIZE, TILE_SIZE, self.color)
        pyxel.text(self.x + 2, self.y + 2, self.label, 0)
        if self.type == "shop":
            npc_nome = NpcMercante.nome
            pyxel.text(self.x, self.y - 8, npc_nome, 7)
        elif self.type == "forge":
            npc_nome = NpcFerreiro.nome
            pyxel.text(self.x, self.y - 8, npc_nome, 7)
        elif self.type == "info":
            npc_nome = "Informante"
            pyxel.text(self.x, self.y - 8, npc_nome, 7)

    def get_tile_pos(self):
        return self.x // TILE_SIZE, self.y // TILE_SIZE

    def start_dialogue(self):
        if not self.automaton:
            return False  # Não há autômato definido para este NPC

        self.is_dialogue_active = True
        self.dialogue_state = list(self.automaton.keys())[0]  # Pega o primeiro estado do AFD
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

        if not state_info["options"]:
            self.dialogue_end_timer = 60  # 60 frames (~2 segundos) # Se não há opções, é um estado final de fala
            # Poderia ter uma lógica para auto-avançar ou esperar um "continuar" genérico
            # Por enquanto, se não há opções, o jogador precisará sair manualmente ou o estado precisa transitar para END
            if self.dialogue_state == "END": # Se chegou ao estado END, o diálogo efetivamente acabou.
                 pass # A flag is_dialogue_active será controlada pelo Game para realmente sair.


    def process_player_choice(self, choice_key):
        if not self.is_dialogue_active or not self.dialogue_state or not self.automaton:
            return

        state_info = self.automaton.get(self.dialogue_state)
        if not state_info or choice_key not in state_info["transitions"]:
            return

        proximo_estado = state_info["transitions"][choice_key]
        self.dialogue_state = proximo_estado

        if self.type == "info":
            opcao_texto = state_info["options"].get(choice_key, "")
            if opcao_texto.startswith("perguntar sobre"):
                tema = opcao_texto.replace("perguntar sobre ", "")
                NpcInformante.empilhar(tema)
                # Aqui buscamos a resposta específica e colocamos no diálogo:
                explicacao = NpcInformante.respostas_perguntas.get(tema, "Informação desconhecida.")
                self.dialogue_message = f"{tema.capitalize()}: {explicacao}"
            elif opcao_texto == "sair":
                self.dialogue_message = "Você perguntou sobre: " + ", ".join(NpcInformante.pilha)

        else:
            self.dialogue_message = self.automaton[self.dialogue_state]["message"]

        self.dialogue_options_display = [
            f"[{k}] {v}" for k, v in self.automaton[self.dialogue_state]["options"].items()
        ]

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
        self.imagens = Imagens.ImagensNPC()
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.active_npc_interaction and self.active_npc_interaction.dialogue_end_timer > 0:
            self.active_npc_interaction.dialogue_end_timer -= 1
            if self.active_npc_interaction.dialogue_end_timer <= 0:
                self.active_npc_interaction.end_dialogue()
                self.active_npc_interaction = None

        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # Modo de Diálogo Ativo
            # O jogador não se move, apenas interage com o diálogo
            if pyxel.btnp(pyxel.KEY_1):
                self.active_npc_interaction.process_player_choice("1")
            elif pyxel.btnp(pyxel.KEY_2):
                self.active_npc_interaction.process_player_choice("2")
            elif pyxel.btnp(pyxel.KEY_3):
                self.active_npc_interaction.process_player_choice("3")
            elif pyxel.btnp(pyxel.KEY_4):
                self.active_npc_interaction.process_player_choice("4")
            elif pyxel.btnp(pyxel.KEY_5):
                self.active_npc_interaction.process_player_choice("5")
            elif pyxel.btnp(pyxel.KEY_6):
                self.active_npc_interaction.process_player_choice("6")
            elif pyxel.btnp(pyxel.KEY_7):
                self.active_npc_interaction.process_player_choice("7")
            elif pyxel.btnp(pyxel.KEY_8):
                self.active_npc_interaction.process_player_choice("8")
            elif pyxel.btnp(pyxel.KEY_9):
                self.active_npc_interaction.process_player_choice("9")
            # Adicione mais teclas se suas opções usarem (ex: 4, 5...)

            # Se o diálogo do NPC chegou ao estado final "Encerrado"
            if self.active_npc_interaction.dialogue_state == "Encerrado":
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
                self.active_npc_interaction = current_near_npc
                if self.active_npc_interaction.start_dialogue():
                    print(f"Iniciando diálogo com {self.get_npc_name(current_near_npc)}.")
                else:
                    print(f"Interagindo com {self.get_npc_name(current_near_npc)} (sem diálogo complexo).")


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

        if self.active_npc_interaction and self.active_npc_interaction.is_dialogue_active:
            # Desenha a UI de Diálogo
            npc = self.active_npc_interaction

            # Caixa de diálogo no rodapé
            # Caixa de diálogo dinâmica
            texto_x = 50  # Posição inicial do texto
            texto_y = None  # Vamos calcular depois

            # Calcular linhas do diálogo
            max_text_width = SCREEN_WIDTH - texto_x - 10
            wrapped_lines = wrap_text(npc.dialogue_message, max_text_width)
            num_text_lines = len(wrapped_lines)

            # Calcular altura total: linhas do texto + linhas das opções
            num_options = len(npc.dialogue_options_display)
            line_height = 8
            padding = 10

            conteudo_altura = (num_text_lines + num_options) * line_height + padding

            # Caixa ajustada
            dialog_box_h = conteudo_altura + 10
            dialog_box_y = SCREEN_HEIGHT - dialog_box_h - 5

            pyxel.rect(5, dialog_box_y, SCREEN_WIDTH - 10, dialog_box_h, 1)   # Caixa azul escuro
            pyxel.rectb(5, dialog_box_y, SCREEN_WIDTH - 10, dialog_box_h, 7)  # Borda branca

            # Desenha o retrato do NPC (se houver)
            retrato = self.imagens.get_retrato(npc.type)
            retrato_x = -5
            retrato_y = dialog_box_y - retrato["h"] + 10  # Suba o retrato 8 pixels acima da caixa
            blt_scale2x(retrato_x, retrato_y, retrato["banco"], retrato["u"], retrato["v"], retrato["w"], retrato["h"])

            # Texto do diálogo e opções ao lado do retrato
            texto_x = 50  # Largura do retrato + margem
            texto_y = dialog_box_y + 5

            max_text_width = SCREEN_WIDTH - texto_x - 10  # Ajuste conforme sua caixa, a mensagem no NPC
            wrapped_lines = wrap_text(npc.dialogue_message, max_text_width)
            for i, line in enumerate(wrapped_lines):
                pyxel.text(texto_x, texto_y + i * 8, line, 7)

            opt_y_start = texto_y + len(wrapped_lines) * 8 + 8
            for i, opt_text in enumerate(npc.dialogue_options_display):
                pyxel.text(texto_x, opt_y_start + (i * 8), opt_text, 7)  # Opções do jogador
            

        else:
            # Mostra "Pressione E para interagir" se perto de algum NPC
            temp_near_npc = None
            for npc_check in self.npcs:
                if is_near(self.player, npc_check):
                    temp_near_npc = npc_check
                    break
            if temp_near_npc:
                pyxel.text(5, SCREEN_HEIGHT - 15, f"[E] Interagir com {self.get_npc_name(temp_near_npc)}", 7)

Game()