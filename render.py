import math

import numpy as np
from OpenGL.GL import *
from PIL import Image

from settings import ALTURA, GAME_OVER, LARGURA, TELA_INICIO


def carregar_textura(caminho):
    imagem = Image.open(caminho)
    if hasattr(Image, "Transpose"):
        imagem = imagem.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    else:
        imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(imagem.convert("RGBA"), dtype=np.uint8)

    id_textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, id_textura)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        imagem.width,
        imagem.height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        img_data,
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return id_textura


def configurar_opengl():
    glViewport(0, 0, LARGURA, ALTURA)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, LARGURA, 0, ALTURA, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def desenhar_quad_textura(textura, x, y, largura, altura):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textura)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y)
    glTexCoord2f(1, 0)
    glVertex2f(x + largura, y)
    glTexCoord2f(1, 1)
    glVertex2f(x + largura, y + altura)
    glTexCoord2f(0, 1)
    glVertex2f(x, y + altura)
    glEnd()
    glDisable(GL_TEXTURE_2D)


def desenhar_quad_cor(x, y, largura, altura, r, g, b):
    glDisable(GL_TEXTURE_2D)
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura)
    glVertex2f(x, y + altura)
    glEnd()


def desenhar_quad_rgba(x, y, largura, altura, r, g, b, a):
    glDisable(GL_TEXTURE_2D)
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura)
    glVertex2f(x, y + altura)
    glEnd()


def desenhar_circulo(x, y, raio, r, g, b, a=1.0, segmentos=24):
    glDisable(GL_TEXTURE_2D)
    glColor4f(r, g, b, a)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(segmentos + 1):
        angulo = (2.0 * math.pi * i) / segmentos
        glVertex2f(x + math.cos(angulo) * raio, y + math.sin(angulo) * raio)
    glEnd()


def desenhar_nuvem(x, y, escala, alpha=0.82):
    desenhar_circulo(x, y, 16 * escala, 1.0, 1.0, 1.0, alpha)
    desenhar_circulo(x + 18 * escala, y + 7 * escala, 22 * escala, 1.0, 1.0, 1.0, alpha)
    desenhar_circulo(x + 42 * escala, y, 18 * escala, 1.0, 1.0, 1.0, alpha)
    desenhar_quad_rgba(x - 4 * escala, y - 11 * escala, 56 * escala, 20 * escala, 1.0, 1.0, 1.0, alpha)


def desenhar_montanha(base_x, altura, largura, r, g, b):
    glDisable(GL_TEXTURE_2D)
    glColor3f(r, g, b)
    glBegin(GL_TRIANGLES)
    glVertex2f(base_x, 48)
    glVertex2f(base_x + largura / 2, altura)
    glVertex2f(base_x + largura, 48)
    glEnd()


def desenhar_fundo(textura_sky, camera_x, tempo):
    glClearColor(0.44, 0.73, 0.98, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    faixas = [
        (0.52, 0.80, 0.99),
        (0.47, 0.76, 0.99),
        (0.41, 0.71, 0.97),
        (0.36, 0.67, 0.95),
        (0.32, 0.61, 0.92),
        (0.28, 0.55, 0.88),
    ]
    faixa_altura = ALTURA / len(faixas)
    for indice, cor in enumerate(faixas):
        desenhar_quad_cor(0, indice * faixa_altura, LARGURA, faixa_altura + 1, *cor)

    sol_x = LARGURA - 160
    sol_y = ALTURA - 100
    pulsar = 1.0 + math.sin(tempo * 1.3) * 0.05
    desenhar_circulo(sol_x, sol_y, 112 * pulsar, 1.0, 0.93, 0.46, 0.06)
    desenhar_circulo(sol_x, sol_y, 74 * pulsar, 1.0, 0.90, 0.30, 0.16)
    desenhar_circulo(sol_x, sol_y, 32, 1.0, 0.94, 0.58, 0.95)

    inicio_nuvens_textura = int(camera_x * 0.25) % 260
    for indice in range(-1, 6):
        x = indice * 260 - inicio_nuvens_textura
        y = 354 + int(math.sin(tempo * 0.55 + indice) * 6)
        desenhar_quad_textura(textura_sky, x, y, 192, 112)

    inicio_nuvens = int(camera_x * 0.22) % 280
    for indice in range(-1, 7):
        x = indice * 280 - inicio_nuvens
        y = 352 + int(math.sin(tempo * 0.7 + indice * 0.8) * 7)
        desenhar_nuvem(x, y, 1.0, 0.78)

    deslocamento_montanhas = (camera_x * 0.12) % 320
    for indice in range(-2, 7):
        base_x = indice * 320 - deslocamento_montanhas
        desenhar_montanha(base_x, 240, 320, 0.24, 0.58, 0.31)
        desenhar_montanha(base_x + 90, 205, 220, 0.18, 0.49, 0.25)

    deslocamento_arbustos = (camera_x * 0.30) % 180
    for indice in range(-2, 9):
        x = indice * 180 - deslocamento_arbustos
        desenhar_quad_rgba(x, 34, 110, 16, 0.17, 0.45, 0.20, 1.0)
        desenhar_circulo(x + 26, 44, 18, 0.20, 0.54, 0.22, 1.0)
        desenhar_circulo(x + 55, 48, 22, 0.22, 0.58, 0.25, 1.0)
        desenhar_circulo(x + 84, 42, 18, 0.19, 0.49, 0.21, 1.0)

    desenhar_quad_rgba(0, 0, LARGURA, 24, 0.13, 0.36, 0.17, 1.0)
    desenhar_quad_rgba(0, 24, LARGURA, 8, 0.18, 0.48, 0.21, 1.0)


def desenhar_mapa(texturas, blocos, inimigos, moedas, objetivo, camera_x):
    for bloco in blocos:
        textura = texturas["ground"]
        if bloco[4] == 1:
            textura = texturas["block"]
        desenhar_quad_textura(textura, bloco[0] - camera_x, bloco[1], bloco[2], bloco[3])

    for moeda in moedas:
        desenhar_quad_textura(texturas["coin"], moeda[0] - camera_x, moeda[1], moeda[2], moeda[3])

    for inimigo in inimigos:
        desenhar_quad_textura(texturas["bee"], inimigo[0] - camera_x, inimigo[1], inimigo[2], inimigo[3])

    desenhar_quad_textura(texturas["chest"], objetivo[0] - camera_x, objetivo[1], objetivo[2], objetivo[3])


def desenhar_jogador(texturas, jogador, camera_x, invencivel, tempo):
    if invencivel and int(tempo * 12) % 2 == 0:
        return

    sombra_x = jogador[0] - camera_x + jogador[2] * 0.5
    sombra_y = jogador[1] - 4
    desenhar_circulo(sombra_x, sombra_y, jogador[2] * 0.48, 0.0, 0.0, 0.0, 0.18)
    if invencivel:
        desenhar_circulo(sombra_x, sombra_y + 18, jogador[2] * 0.85, 1.0, 0.95, 0.40, 0.12)

    desenhar_quad_textura(texturas["player"], jogador[0] - camera_x, jogador[1], jogador[2], jogador[3])


def desenhar_segmento(x, y, w, h):
    desenhar_quad_cor(x, y, w, h, 1.0, 0.92, 0.25)


def desenhar_digito(numero, x, y, escala):
    segmentos = [
        [1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 0, 1],
        [0, 1, 1, 0, 0, 1, 1],
        [1, 0, 1, 1, 0, 1, 1],
        [1, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 1],
    ]
    s = segmentos[numero]
    t = 4 * escala
    l = 22 * escala
    a = 38 * escala
    if s[0]:
        desenhar_segmento(x + t, y + a, l, t)
    if s[1]:
        desenhar_segmento(x + l + t, y + a / 2 + t, t, a / 2)
    if s[2]:
        desenhar_segmento(x + l + t, y + t, t, a / 2)
    if s[3]:
        desenhar_segmento(x + t, y, l, t)
    if s[4]:
        desenhar_segmento(x, y + t, t, a / 2)
    if s[5]:
        desenhar_segmento(x, y + a / 2 + t, t, a / 2)
    if s[6]:
        desenhar_segmento(x + t, y + a / 2, l, t)


def desenhar_numero(valor, x, y, escala):
    texto = str(valor)
    for i in range(len(texto)):
        digito = int(texto[i])
        desenhar_digito(digito, x + i * 34 * escala, y, escala)


def desenhar_coracao(x, y, escala, brilho=1.0):
    cor = (0.92 * brilho, 0.15 * brilho, 0.22 * brilho)
    desenhar_circulo(x + 8 * escala, y + 14 * escala, 8 * escala, *cor, 1.0)
    desenhar_circulo(x + 20 * escala, y + 14 * escala, 8 * escala, *cor, 1.0)
    glDisable(GL_TEXTURE_2D)
    glColor4f(*cor, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(x + 1 * escala, y + 15 * escala)
    glVertex2f(x + 27 * escala, y + 15 * escala)
    glVertex2f(x + 14 * escala, y - 1 * escala)
    glEnd()


def desenhar_moeda(x, y, escala, brilho=1.0):
    desenhar_circulo(x + 12 * escala, y + 12 * escala, 11 * escala, 1.0, 0.84, 0.22, 0.95)
    desenhar_circulo(x + 12 * escala, y + 12 * escala, 7 * escala, 1.0, 0.96, 0.55, 1.0)
    desenhar_quad_rgba(x + 10 * escala, y + 4 * escala, 4 * escala, 16 * escala, 1.0, 0.75, 0.15, brilho)


def desenhar_estrela(x, y, escala, brilho=1.0):
    pontos = [
        (x + 12 * escala, y + 22 * escala),
        (x + 16 * escala, y + 16 * escala),
        (x + 22 * escala, y + 12 * escala),
        (x + 16 * escala, y + 8 * escala),
        (x + 12 * escala, y + 2 * escala),
        (x + 8 * escala, y + 8 * escala),
        (x + 2 * escala, y + 12 * escala),
        (x + 8 * escala, y + 16 * escala),
    ]
    glDisable(GL_TEXTURE_2D)
    glColor4f(1.0 * brilho, 0.88 * brilho, 0.32 * brilho, 1.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x + 12 * escala, y + 12 * escala)
    for px, py in pontos + [pontos[0]]:
        glVertex2f(px, py)
    glEnd()


def desenhar_hud(vidas, pontos, fase, camera_x, comprimento_fase, tempo):
    brilho = 0.5 + 0.5 * math.sin(tempo * 4.0)
    desenhar_quad_rgba(12, ALTURA - 78, LARGURA - 24, 64, 0.02, 0.04, 0.08, 0.70)
    desenhar_quad_rgba(16, ALTURA - 74, LARGURA - 32, 56, 0.08, 0.14, 0.22, 0.88)
    desenhar_quad_rgba(18, ALTURA - 72, LARGURA - 36, 2, 0.75, 0.88, 1.0, 0.12)

    desenhar_quad_rgba(26, ALTURA - 62, 170, 36, 0.11, 0.18, 0.28, 0.92)
    desenhar_quad_rgba(32, ALTURA - 56, 28, 28, 0.00, 0.00, 0.00, 0.12)
    desenhar_coracao(31, ALTURA - 56, 0.82, 0.95 + brilho * 0.05)
    desenhar_numero(vidas, 64, ALTURA - 56, 0.70)

    desenhar_quad_rgba(350, ALTURA - 62, 260, 36, 0.11, 0.18, 0.28, 0.92)
    desenhar_quad_rgba(356, ALTURA - 56, 28, 28, 0.00, 0.00, 0.00, 0.10)
    desenhar_moeda(353, ALTURA - 56, 0.75, 0.95)
    desenhar_numero(pontos, 394, ALTURA - 56, 0.70)

    desenhar_quad_rgba(720, ALTURA - 62, 212, 36, 0.11, 0.18, 0.28, 0.92)
    desenhar_estrela(728, ALTURA - 58, 0.78, 0.90 + brilho * 0.10)
    desenhar_numero(fase, 760, ALTURA - 56, 0.70)

    progresso = 0.0
    if comprimento_fase > LARGURA:
        progresso = camera_x / (comprimento_fase - LARGURA)
    if progresso < 0.0:
        progresso = 0.0
    if progresso > 1.0:
        progresso = 1.0

    barra_x = 104
    barra_y = 20
    barra_w = LARGURA - 208
    desenhar_quad_rgba(barra_x, barra_y, barra_w, 12, 0.03, 0.04, 0.06, 0.60)
    desenhar_quad_rgba(barra_x + 2, barra_y + 2, (barra_w - 4) * progresso, 8, 0.98, 0.76, 0.18, 0.95)
    desenhar_quad_rgba(barra_x + barra_w - 18, barra_y - 2, 18, 18, 0.72, 0.45, 0.10, 1.0)
    desenhar_quad_rgba(barra_x + barra_w - 16, barra_y, 14, 14, 0.96, 0.83, 0.37, 0.95)


def desenhar_tecla(x, y, largura, altura, r, g, b, a=1.0):
    desenhar_quad_rgba(x, y, largura, altura, r, g, b, a)
    desenhar_quad_rgba(x + 2, y + 2, largura - 4, altura - 4, 1.0, 1.0, 1.0, 0.06)


def desenhar_botao_play(x, y, tamanho):
    desenhar_circulo(x + tamanho / 2, y + tamanho / 2, tamanho / 2, 1.0, 0.89, 0.30, 1.0)
    desenhar_circulo(x + tamanho / 2, y + tamanho / 2, tamanho / 2 - 6, 0.18, 0.18, 0.24, 1.0)
    glDisable(GL_TEXTURE_2D)
    glColor4f(1.0, 0.92, 0.30, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(x + tamanho * 0.42, y + tamanho * 0.32)
    glVertex2f(x + tamanho * 0.42, y + tamanho * 0.68)
    glVertex2f(x + tamanho * 0.70, y + tamanho * 0.50)
    glEnd()


def desenhar_tela_inicio(tempo):
    brilho = 0.45 + 0.25 * math.sin(tempo * 3.0)
    desenhar_quad_rgba(0, 0, LARGURA, ALTURA, 0.0, 0.0, 0.0, 0.18)
    desenhar_quad_rgba(160, 108, 640, 314, 0.02, 0.03, 0.06, 0.95)
    desenhar_quad_rgba(174, 122, 612, 286, 0.12, 0.16, 0.24, 0.96)
    desenhar_quad_rgba(180, 128, 600, 6, 0.97, 0.83, 0.32, brilho)
    desenhar_quad_rgba(180, 404, 600, 6, 0.97, 0.83, 0.32, brilho)
    for i in range(4):
        desenhar_quad_rgba(194 + i * 146, 134, 6, 274, 0.97, 0.83, 0.32, 0.35)

    desenhar_circulo(276, 265, 74, 0.97, 0.84, 0.28, 0.18)
    desenhar_botao_play(228, 217, 96)
    desenhar_coracao(242, 305, 1.2, 1.0)
    desenhar_moeda(250, 160, 1.0, 1.0)
    desenhar_estrela(720, 164, 1.0, 0.9)
    desenhar_estrela(680, 302, 0.7, 0.75)

    desenhar_tecla(356, 330, 92, 42, 0.18, 0.24, 0.38, 1.0)
    desenhar_tecla(463, 330, 130, 42, 0.18, 0.24, 0.38, 1.0)
    desenhar_tecla(608, 330, 96, 42, 0.18, 0.24, 0.38, 1.0)
    desenhar_quad_rgba(377, 341, 48, 20, 0.96, 0.82, 0.28, 1.0)
    desenhar_quad_rgba(478, 344, 100, 14, 0.96, 0.82, 0.28, 1.0)
    desenhar_quad_rgba(639, 341, 20, 20, 0.96, 0.82, 0.28, 1.0)
    desenhar_quad_rgba(649, 335, 8, 32, 0.96, 0.82, 0.28, 1.0)

    desenhar_quad_rgba(230, 174, 500, 22, 0.98, 0.80, 0.20, 0.18)
    desenhar_quad_rgba(250, 184, 460, 16, 0.98, 0.80, 0.20, 0.10)


def desenhar_tela_game_over(tempo):
    brilho = 0.50 + 0.30 * math.sin(tempo * 4.0)
    desenhar_quad_rgba(0, 0, LARGURA, ALTURA, 0.0, 0.0, 0.0, 0.28)
    desenhar_quad_rgba(150, 102, 660, 326, 0.08, 0.02, 0.02, 0.95)
    desenhar_quad_rgba(164, 116, 632, 298, 0.28, 0.05, 0.04, 0.96)
    desenhar_quad_rgba(170, 122, 620, 6, 0.98, 0.68, 0.22, brilho)
    desenhar_quad_rgba(170, 406, 620, 6, 0.98, 0.68, 0.22, brilho)
    desenhar_quad_rgba(170, 122, 6, 290, 0.98, 0.68, 0.22, brilho)
    desenhar_quad_rgba(784, 122, 6, 290, 0.98, 0.68, 0.22, brilho)

    desenhar_circulo(315, 264, 70, 0.84, 0.10, 0.12, 0.18)
    desenhar_coracao(286, 220, 1.15, 0.8)
    desenhar_coracao(344, 220, 1.15, 0.8)
    glPushMatrix()
    glTranslatef(360, 264, 0)
    glRotatef(45, 0, 0, 1)
    desenhar_quad_rgba(-140, -10, 280, 20, 1.0, 0.86, 0.30, 1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(360, 264, 0)
    glRotatef(-45, 0, 0, 1)
    desenhar_quad_rgba(-140, -10, 280, 20, 1.0, 0.86, 0.30, 1.0)
    glPopMatrix()

    desenhar_quad_rgba(500, 170, 200, 120, 0.08, 0.02, 0.02, 0.78)
    desenhar_quad_rgba(516, 186, 168, 88, 0.14, 0.05, 0.04, 0.96)
    desenhar_estrela(575, 199, 1.2, 0.95)
    desenhar_estrela(540, 228, 0.65, 0.75)
    desenhar_circulo(575, 245, 15, 0.96, 0.80, 0.24, 1.0)

    for i in range(5):
        offset = math.sin(tempo * 2.5 + i) * 6
        desenhar_circulo(230 + i * 120, 154 + offset, 10 + i * 1.5, 0.98, 0.74, 0.20, 0.24)


def desenhar_tela_mensagem(estado, tempo):
    if estado == TELA_INICIO:
        desenhar_tela_inicio(tempo)
    if estado == GAME_OVER:
        desenhar_tela_game_over(tempo)
