import glfw
from OpenGL.GL import *
from PIL import Image
import numpy as np
import time
import random

# =============================================================
# NICK CAGE BROS - projeto inicial
# Bibliotecas usadas no jogo: glfw, OpenGL, PIL, numpy, time, random
# Estrutura simples para ficar próxima dos exercícios de aula.
# =============================================================

LARGURA = 960
ALTURA = 540
TITULO = "Nick Cage Bros - OpenGL"

TAMANHO_TILE = 48
LARGURA_PLAYER = 36
ALTURA_PLAYER = 54

GRAVIDADE = -1600.0
VELOCIDADE_PULO = 640.0
VELOCIDADE_PLAYER = 260.0

VIDAS_INICIAIS = 3
MAX_FASE_DIFICULDADE = 12
MAX_PLATAFORMAS = 14
MAX_INIMIGOS = 22

# Estados do jogo
TELA_INICIO = 0
JOGANDO = 1
GAME_OVER = 2


def carregar_textura(caminho):
    imagem = Image.open(caminho)
    imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(imagem.convert("RGBA"), dtype=np.uint8)

    id_textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, id_textura)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, imagem.width, imagem.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
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


def desenhar_fundo(textura_sky, camera_x):
    glClearColor(0.40, 0.68, 0.95, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Nuvens repetidas com textura simples, usando a câmera para dar parallax.
    inicio = int(camera_x * 0.25) % 256
    for i in range(-1, 6):
        x = i * 256 - inicio
        desenhar_quad_textura(textura_sky, x, 355, 192, 112)

    # Montanhas geométricas no fundo.
    glDisable(GL_TEXTURE_2D)
    glColor3f(0.25, 0.62, 0.28)
    glBegin(GL_TRIANGLES)
    for i in range(-1, 8):
        base_x = i * 220 - (camera_x * 0.12 % 220)
        glVertex2f(base_x, 96)
        glVertex2f(base_x + 130, 285)
        glVertex2f(base_x + 260, 96)
    glEnd()


def retangulos_colidem(a, b):
    if a[0] + a[2] < b[0]:
        return False
    if a[0] > b[0] + b[2]:
        return False
    if a[1] + a[3] < b[1]:
        return False
    if a[1] > b[1] + b[3]:
        return False
    return True


def criar_fase(numero_fase):
    blocos = []
    inimigos = []
    moedas = []

    dificuldade = min(max(1, numero_fase), MAX_FASE_DIFICULDADE)
    comprimento = 2300 + dificuldade * 450

    # Chão principal com buracos aleatórios.
    x = 0
    while x < comprimento:
        cria_buraco = False
        if x > 450 and x < comprimento - 500:
            chance_buraco = min(10 + dificuldade * 3, 35)
            if random.randint(0, 100) < chance_buraco:
                cria_buraco = True
        if cria_buraco:
            x += TAMANHO_TILE * random.randint(1, 2)
        else:
            blocos.append([x, 0, TAMANHO_TILE, TAMANHO_TILE, 0])
            x += TAMANHO_TILE

    # Plataformas suspensas.
    quantidade_plataformas = min(5 + dificuldade, MAX_PLATAFORMAS)
    for i in range(quantidade_plataformas):
        px = random.randint(5, int(comprimento / TAMANHO_TILE) - 7) * TAMANHO_TILE
        py = random.choice([160, 215, 270])
        tamanho = random.randint(2, 5)
        for j in range(tamanho):
            blocos.append([px + j * TAMANHO_TILE, py, TAMANHO_TILE, TAMANHO_TILE, 1])
        moedas.append([px + TAMANHO_TILE, py + 60, 24, 24])

    # Inimigos: abelhas cinematográficas.
    quantidade_inimigos = min(4 + dificuldade * 2, MAX_INIMIGOS)
    for i in range(quantidade_inimigos):
        ex = random.randint(8, int(comprimento / TAMANHO_TILE) - 4) * TAMANHO_TILE
        ey = random.choice([TAMANHO_TILE, 112, 170])
        inimigos.append([ex, ey, 40, 40, random.choice([-1, 1]), 0])

    objetivo = [comprimento - 160, TAMANHO_TILE, 64, 64]
    return blocos, inimigos, moedas, objetivo, comprimento


def jogador_no_chao(jogador, blocos):
    area = [jogador[0] + 5, jogador[1] - 2, jogador[2] - 10, 4]
    for bloco in blocos:
        if retangulos_colidem(area, bloco):
            return True
    return False


def resolver_colisao_vertical(jogador, blocos, velocidade_y):
    jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]
    for bloco in blocos:
        if retangulos_colidem(jogador_ret, bloco):
            if velocidade_y <= 0:
                jogador[1] = bloco[1] + bloco[3]
                velocidade_y = 0
            else:
                jogador[1] = bloco[1] - jogador[3]
                velocidade_y = -80
            jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]
    return velocidade_y


def resolver_colisao_horizontal(jogador, blocos, deslocamento_x):
    jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]
    for bloco in blocos:
        if retangulos_colidem(jogador_ret, bloco):
            if deslocamento_x > 0:
                jogador[0] = bloco[0] - jogador[2]
            if deslocamento_x < 0:
                jogador[0] = bloco[0] + bloco[2]
            jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]


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
    # Pisca depois de dano para indicar invencibilidade.
    if invencivel:
        if int(tempo * 12) % 2 == 0:
            return
    desenhar_quad_textura(texturas["player"], jogador[0] - camera_x, jogador[1], jogador[2], jogador[3])


def desenhar_segmento(x, y, w, h):
    desenhar_quad_cor(x, y, w, h, 1.0, 0.92, 0.25)


def desenhar_digito(numero, x, y, escala):
    # Segmentos: topo, sup_dir, inf_dir, baixo, inf_esq, sup_esq, meio
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
    if s[0]: desenhar_segmento(x + t, y + a, l, t)
    if s[1]: desenhar_segmento(x + l + t, y + a / 2 + t, t, a / 2)
    if s[2]: desenhar_segmento(x + l + t, y + t, t, a / 2)
    if s[3]: desenhar_segmento(x + t, y, l, t)
    if s[4]: desenhar_segmento(x, y + t, t, a / 2)
    if s[5]: desenhar_segmento(x, y + a / 2 + t, t, a / 2)
    if s[6]: desenhar_segmento(x + t, y + a / 2, l, t)


def desenhar_numero(valor, x, y, escala):
    texto = str(valor)
    for i in range(len(texto)):
        digito = int(texto[i])
        desenhar_digito(digito, x + i * 34 * escala, y, escala)


def desenhar_hud(vidas, pontos, fase):
    # Coração/vidas no canto superior esquerdo.
    desenhar_quad_cor(16, ALTURA - 38, 18, 18, 0.9, 0.05, 0.08)
    desenhar_quad_cor(22, ALTURA - 44, 18, 18, 0.9, 0.05, 0.08)
    desenhar_numero(vidas, 52, ALTURA - 55, 0.75)

    # Pontuação no centro e fase à direita.
    desenhar_numero(pontos, 410, ALTURA - 55, 0.75)
    desenhar_numero(fase, 850, ALTURA - 55, 0.75)


def desenhar_tela_mensagem(estado):
    if estado == TELA_INICIO:
        desenhar_quad_cor(260, 210, 440, 120, 0.05, 0.05, 0.08)
        desenhar_quad_cor(275, 225, 410, 90, 0.17, 0.17, 0.22)
        # Desenho simples de um play/entrada.
        glColor3f(1.0, 0.92, 0.25)
        glBegin(GL_TRIANGLES)
        glVertex2f(430, 245)
        glVertex2f(430, 300)
        glVertex2f(490, 272)
        glEnd()
    if estado == GAME_OVER:
        desenhar_quad_cor(250, 200, 460, 140, 0.06, 0.02, 0.02)
        desenhar_quad_cor(270, 220, 420, 100, 0.35, 0.05, 0.04)
        # X grande de game over.
        desenhar_quad_cor(380, 245, 200, 18, 1.0, 0.85, 0.25)
        glLoadIdentity()
        glTranslatef(480, 270, 0)
        glRotatef(45, 0, 0, 1)
        desenhar_quad_cor(-110, -9, 220, 18, 1.0, 0.85, 0.25)
        glLoadIdentity()
        glTranslatef(480, 270, 0)
        glRotatef(-45, 0, 0, 1)
        desenhar_quad_cor(-110, -9, 220, 18, 1.0, 0.85, 0.25)
        glLoadIdentity()


def reiniciar_jogo(numero_fase):
    blocos, inimigos, moedas, objetivo, comprimento = criar_fase(numero_fase)
    jogador = [80, 170, LARGURA_PLAYER, ALTURA_PLAYER]
    return jogador, blocos, inimigos, moedas, objetivo, comprimento


def main():
    if not glfw.init():
        return

    janela = glfw.create_window(LARGURA, ALTURA, TITULO, None, None)
    if not janela:
        glfw.terminate()
        return

    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    configurar_opengl()

    texturas = {
        "player": carregar_textura("assets/nicolas_cage.png"),
        "bee": carregar_textura("assets/bee_enemy.png"),
        "ground": carregar_textura("assets/ground.png"),
        "block": carregar_textura("assets/block.png"),
        "chest": carregar_textura("assets/chest_goal.png"),
        "coin": carregar_textura("assets/coin.png"),
        "sky": carregar_textura("assets/sky.png"),
    }

    estado = TELA_INICIO
    fase = 1
    vidas = VIDAS_INICIAIS
    pontos = 0
    jogador, blocos, inimigos, moedas, objetivo, comprimento_fase = reiniciar_jogo(fase)

    velocidade_y = 0.0
    camera_x = 0.0
    invencivel = False
    tempo_invencivel = 0.0
    enter_antes = False
    espaco_antes = False
    tempo_anterior = time.time()

    while not glfw.window_should_close(janela):
        tempo_atual = time.time()
        delta_time = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual
        if delta_time > 0.05:
            delta_time = 0.05

        glfw.poll_events()

        if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(janela, True)

        enter_agora = glfw.get_key(janela, glfw.KEY_ENTER) == glfw.PRESS
        if enter_agora and not enter_antes:
            if estado == TELA_INICIO or estado == GAME_OVER:
                estado = JOGANDO
                fase = 1
                vidas = VIDAS_INICIAIS
                pontos = 0
                velocidade_y = 0
                invencivel = False
                tempo_invencivel = 0
                jogador, blocos, inimigos, moedas, objetivo, comprimento_fase = reiniciar_jogo(fase)
        enter_antes = enter_agora

        if estado == JOGANDO:
            deslocamento_x = 0.0
            if glfw.get_key(janela, glfw.KEY_RIGHT) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_D) == glfw.PRESS:
                deslocamento_x += VELOCIDADE_PLAYER * delta_time
            if glfw.get_key(janela, glfw.KEY_LEFT) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_A) == glfw.PRESS:
                deslocamento_x -= VELOCIDADE_PLAYER * delta_time

            espaco_agora = glfw.get_key(janela, glfw.KEY_SPACE) == glfw.PRESS
            if espaco_agora and not espaco_antes:
                if jogador_no_chao(jogador, blocos):
                    velocidade_y = VELOCIDADE_PULO
            espaco_antes = espaco_agora

            jogador[0] += deslocamento_x
            resolver_colisao_horizontal(jogador, blocos, deslocamento_x)

            velocidade_y += GRAVIDADE * delta_time
            jogador[1] += velocidade_y * delta_time
            velocidade_y = resolver_colisao_vertical(jogador, blocos, velocidade_y)

            if jogador[0] < 0:
                jogador[0] = 0
            if jogador[0] > comprimento_fase - jogador[2]:
                jogador[0] = comprimento_fase - jogador[2]

            # Atualiza inimigos com movimento simples de patrulha.
            for inimigo in inimigos:
                velocidade_inimigo = 70 + fase * 12
                inimigo[0] += inimigo[4] * velocidade_inimigo * delta_time
                inimigo[5] += delta_time
                inimigo[1] += np.sin(inimigo[5] * 3.0) * 12.0 * delta_time
                if inimigo[0] < 100:
                    inimigo[4] = 1
                if inimigo[0] > comprimento_fase - 200:
                    inimigo[4] = -1

            jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]

            # Coleta moedas/pergaminhos.
            for moeda in moedas[:]:
                if retangulos_colidem(jogador_ret, moeda):
                    pontos += 10
                    moedas.remove(moeda)

            # Colisão com inimigos.
            if tempo_invencivel > 0:
                tempo_invencivel -= delta_time
                if tempo_invencivel <= 0:
                    invencivel = False

            for inimigo in inimigos:
                if retangulos_colidem(jogador_ret, inimigo):
                    if not invencivel:
                        vidas -= 1
                        invencivel = True
                        tempo_invencivel = 1.5
                        jogador[0] -= 45
                        velocidade_y = 360
                        if vidas <= 0:
                            estado = GAME_OVER
                    break

            # Queda em buraco também tira vida.
            if jogador[1] < -120:
                vidas -= 1
                if vidas <= 0:
                    estado = GAME_OVER
                else:
                    jogador[0] = max(80, jogador[0] - 260)
                    jogador[1] = 240
                    velocidade_y = 0
                    invencivel = True
                    tempo_invencivel = 1.5

            # Passou de fase ao tocar no baú.
            if retangulos_colidem(jogador_ret, objetivo):
                fase += 1
                pontos += 100
                velocidade_y = 0
                jogador, blocos, inimigos, moedas, objetivo, comprimento_fase = reiniciar_jogo(fase)

            camera_x = jogador[0] - 280
            if camera_x < 0:
                camera_x = 0
            camera_maxima = comprimento_fase - LARGURA
            if camera_x > camera_maxima:
                camera_x = camera_maxima

        desenhar_fundo(texturas["sky"], camera_x)
        desenhar_mapa(texturas, blocos, inimigos, moedas, objetivo, camera_x)
        desenhar_jogador(texturas, jogador, camera_x, invencivel, tempo_atual)
        desenhar_hud(vidas, pontos, fase)

        if estado == TELA_INICIO or estado == GAME_OVER:
            desenhar_tela_mensagem(estado)

        glfw.swap_buffers(janela)

    glfw.destroy_window(janela)
    glfw.terminate()


if __name__ == "__main__":
    main()
