from PIL import Image
import os

def redimensionar_imagem(arquivo_entrada, arquivo_saida, tamanho=(64, 64)):
    imagem = Image.open(arquivo_entrada)
    imagem_redimensionada = imagem.resize(tamanho, Image.NEAREST)
    imagem_redimensionada.save(arquivo_saida)
    print(f"Imagem {arquivo_entrada} redimensionada para {tamanho} e salva como {arquivo_saida}")

# Exemplo de uso:
#redimensionar_imagem("/mnt/data/Idle.png", "Idle_64x64.png")
import pyxel

class VisualizadorPyxres:
    def __init__(self, arquivo_pyxres, img_bank=0):
        self.arquivo_pyxres = arquivo_pyxres
        self.img_bank = img_bank

        # Tamanho da tela: 256x256 (tamanho máximo Pyxel)
        pyxel.init(256, 256, title="Visualizador de Pyxres")
        pyxel.load(self.arquivo_pyxres)

        # Fator de zoom inicial
        self.zoom = 1

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_UP):
            self.zoom = min(self.zoom + 1, 8)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.zoom = max(self.zoom - 1, 1)

        # Alternar banco de imagens (LEFT/RIGHT)
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.img_bank = max(self.img_bank - 1, 0)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.img_bank = min(self.img_bank + 1, 2)


    def draw(self):
        pyxel.cls(0)
        tile_size = 8 * self.zoom

        for y in range(0, 256, 8):
            for x in range(0, 256, 8):
                px = (x // 8) * tile_size
                py = (y // 8) * tile_size
                pyxel.blt(px, py, self.img_bank, x, y, 8, 8)

        pyxel.text(5, 5, f"Arquivo: {self.arquivo_pyxres}", 7)
        pyxel.text(5, 15, f"Zoom: {self.zoom}x (UP/DOWN)", 7)

# Exemplo de uso
if __name__ == "__main__":
    VisualizadorPyxres("my_resource.pyxres")
    # Desenha o sprite na tela


