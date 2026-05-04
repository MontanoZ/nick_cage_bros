# Camada de renderização OpenGL: texturas, desenhos 2D, HUD e telas de interface.

import math
from collections import OrderedDict
from functools import lru_cache

import numpy as np
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont

from game.models import Block, Coin, Enemy, Goal, Player
from game.settings import ALTURA, GAME_OVER, LARGURA, TELA_INICIO

_CACHE_TEXTO_MAX_ITENS = 128
_cache_texturas_texto: "OrderedDict[tuple, tuple[int, int, int]]" = OrderedDict()


# Carrega imagem do disco e cria textura OpenGL 2D.
def carregar_textura(caminho):
    with Image.open(caminho) as imagem_original:
        if hasattr(Image, "Transpose"):
            imagem = imagem_original.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            imagem = imagem_original.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(imagem.convert("RGBA"), dtype=np.uint8)
        largura = imagem.width
        altura = imagem.height

    id_textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, id_textura)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        largura,
        altura,
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


@lru_cache(maxsize=16)

# Carrega e cacheia fontes para renderização de texto via PIL.
def _carregar_fonte(tamanho, negrito=False):
    candidatos = [
        "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf",
        "Arial Bold.ttf" if negrito else "Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if negrito
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]

    for caminho in candidatos:
        try:
            return ImageFont.truetype(caminho, tamanho)
        except OSError:
            continue

    return ImageFont.load_default()


# Converte imagem PIL em textura OpenGL para uso em texto.
def _uploadar_imagem_como_textura(imagem):
    if hasattr(Image, "Transpose"):
        imagem = imagem.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    else:
        imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)

    dados = np.array(imagem.convert("RGBA"), dtype=np.uint8)
    textura_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textura_id)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        imagem.width,
        imagem.height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        dados,
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return textura_id


# Converte canais de cor de 0..1 para 0..255 com clamp.
def _normalizar_cor_rgba(r, g, b, a):
    return (
        max(0, min(255, int(r * 255))),
        max(0, min(255, int(g * 255))),
        max(0, min(255, int(b * 255))),
        max(0, min(255, int(a * 255))),
    )


# Gera ou recupera textura cacheada para uma string de texto.
def _obter_textura_texto_cacheada(texto, tamanho, r, g, b, a, negrito):
    tamanho_fonte = max(8, int(tamanho))
    cor = _normalizar_cor_rgba(r, g, b, a)
    chave = (texto, tamanho_fonte, cor, negrito)
    entrada = _cache_texturas_texto.get(chave)
    if entrada is not None:
        _cache_texturas_texto.move_to_end(chave)
        return entrada

    fonte = _carregar_fonte(tamanho_fonte, negrito=negrito)
    imagem_base = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    desenho_base = ImageDraw.Draw(imagem_base)
    bbox = desenho_base.textbbox((0, 0), texto, font=fonte)
    largura = max(1, bbox[2] - bbox[0])
    altura = max(1, bbox[3] - bbox[1])
    padding_x = max(2, int(tamanho * 0.18))
    padding_y = max(2, int(tamanho * 0.14))

    imagem = Image.new(
        "RGBA",
        (largura + padding_x * 2, altura + padding_y * 2),
        (0, 0, 0, 0),
    )
    desenho = ImageDraw.Draw(imagem)
    desenho.text((padding_x - bbox[0], padding_y - bbox[1]), texto, font=fonte, fill=cor)
    textura_id = _uploadar_imagem_como_textura(imagem)
    entrada = (textura_id, imagem.width, imagem.height)
    _cache_texturas_texto[chave] = entrada

    if len(_cache_texturas_texto) > _CACHE_TEXTO_MAX_ITENS:
        _, (textura_antiga, _, _) = _cache_texturas_texto.popitem(last=False)
        glDeleteTextures([textura_antiga])

    return entrada


# Desenha texto na tela usando textura gerada por fonte.
def desenhar_texto_fonte(texto, x, y, tamanho, r, g, b, a=1.0, centralizado=False, negrito=False):
    if not texto:
        return

    textura, largura, altura = _obter_textura_texto_cacheada(
        texto, tamanho, r, g, b, a, negrito
    )
    quad_x = x - largura / 2 if centralizado else x
    quad_y = y - altura / 2 if centralizado else y
    desenhar_quad_textura(textura, quad_x, quad_y, largura, altura)


# Libera texturas OpenGL do jogo e limpa cache de texto.
def liberar_texturas(texturas):
    ids = [textura_id for textura_id in texturas.values() if textura_id]
    if ids:
        glDeleteTextures(ids)
    if _cache_texturas_texto:
        glDeleteTextures([entrada[0] for entrada in _cache_texturas_texto.values()])
        _cache_texturas_texto.clear()


# Viewport com barras (letterbox) para manter proporção LARGURA:ALTURA no framebuffer.
def _viewport_letterbox(largura_fb: int, altura_fb: int) -> None:
    largura_fb = max(1, largura_fb)
    altura_fb = max(1, altura_fb)
    escala = min(largura_fb / LARGURA, altura_fb / ALTURA)
    vw = max(1, int(LARGURA * escala))
    vh = max(1, int(ALTURA * escala))
    ox = (largura_fb - vw) // 2
    oy = (altura_fb - vh) // 2
    glViewport(ox, oy, vw, vh)


# Configura viewport, projeção ortográfica e blending.
def configurar_opengl(largura_framebuffer: int | None = None, altura_framebuffer: int | None = None):
    if largura_framebuffer is not None and altura_framebuffer is not None:
        _viewport_letterbox(largura_framebuffer, altura_framebuffer)
    else:
        glViewport(0, 0, LARGURA, ALTURA)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, LARGURA, 0, ALTURA, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


# Limpa o framebuffer inteiro e aplica escala que cabe na tela (barras pretas se preciso).
def preparar_frame_framebuffer(largura_fb: int, altura_fb: int) -> None:
    largura_fb = max(1, largura_fb)
    altura_fb = max(1, altura_fb)
    glViewport(0, 0, largura_fb, altura_fb)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    configurar_opengl(largura_fb, altura_fb)


# Desenha um retângulo texturizado nas coordenadas informadas.
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


# Desenha um retângulo sólido RGB sem textura.
def desenhar_quad_cor(x, y, largura, altura, r, g, b):
    glDisable(GL_TEXTURE_2D)
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura)
    glVertex2f(x, y + altura)
    glEnd()


# Desenha um retângulo sólido com canal alpha.
def desenhar_quad_rgba(x, y, largura, altura, r, g, b, a):
    glDisable(GL_TEXTURE_2D)
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura)
    glVertex2f(x, y + altura)
    glEnd()


# Desenha um círculo preenchido usando triângulos em leque.
def desenhar_circulo(x, y, raio, r, g, b, a=1.0, segmentos=24):
    glDisable(GL_TEXTURE_2D)
    glColor4f(r, g, b, a)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(segmentos + 1):
        angulo = (2.0 * math.pi * i) / segmentos
        glVertex2f(x + math.cos(angulo) * raio, y + math.sin(angulo) * raio)
    glEnd()


# Desenha uma nuvem estilizada combinando círculos e retângulo.
def desenhar_nuvem(x, y, escala, alpha=0.82):
    desenhar_circulo(x, y, 16 * escala, 1.0, 1.0, 1.0, alpha)
    desenhar_circulo(x + 18 * escala, y + 7 * escala, 22 * escala, 1.0, 1.0, 1.0, alpha)
    desenhar_circulo(x + 42 * escala, y, 18 * escala, 1.0, 1.0, 1.0, alpha)
    desenhar_quad_rgba(x - 4 * escala, y - 11 * escala, 56 * escala, 20 * escala, 1.0, 1.0, 1.0, alpha)


# Desenha uma montanha triangular para o cenário de fundo.
def desenhar_montanha(base_x, altura, largura, r, g, b):
    glDisable(GL_TEXTURE_2D)
    glColor3f(r, g, b)
    glBegin(GL_TRIANGLES)
    glVertex2f(base_x, 48)
    glVertex2f(base_x + largura / 2, altura)
    glVertex2f(base_x + largura, 48)
    glEnd()


# Renderiza céu, sol, nuvens, montanhas e vegetação com parallax.
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


# Desenha blocos, moedas, inimigos e objetivo da fase.
def desenhar_mapa(
    texturas,
    blocos: list[Block],
    inimigos: list[Enemy],
    moedas: list[Coin],
    objetivo: Goal,
    camera_x,
):
    for bloco in blocos:
        textura = texturas["ground"]
        if bloco.tipo == 1:
            textura = texturas["block"]
        desenhar_quad_textura(textura, bloco.x - camera_x, bloco.y, bloco.w, bloco.h)

    for moeda in moedas:
        desenhar_quad_textura(texturas["coin"], moeda.x - camera_x, moeda.y, moeda.w, moeda.h)

    for inimigo in inimigos:
        textura_inimigo = texturas["bee"] if inimigo.tipo == "abelha" else texturas["sahur"]
        desenhar_quad_textura(
            textura_inimigo,
            inimigo.x - camera_x,
            inimigo.y,
            inimigo.w,
            inimigo.h,
        )

    desenhar_quad_textura(
        texturas["chest"],
        objetivo.x - camera_x,
        objetivo.y,
        objetivo.w,
        objetivo.h,
    )


# Desenha jogador, sombra e efeito visual de invencibilidade.
def desenhar_jogador(texturas, jogador: Player, camera_x, invencivel, tempo):
    if invencivel and int(tempo * 12) % 2 == 0:
        return

    sombra_x = jogador.x - camera_x + jogador.w * 0.5
    sombra_y = jogador.y - 4
    desenhar_circulo(sombra_x, sombra_y, jogador.w * 0.48, 0.0, 0.0, 0.0, 0.18)
    if invencivel:
        desenhar_circulo(sombra_x, sombra_y + 18, jogador.w * 0.85, 1.0, 0.95, 0.40, 0.12)

    desenhar_quad_textura(
        texturas["player"],
        jogador.x - camera_x,
        jogador.y,
        jogador.w,
        jogador.h,
    )


# Renderiza número estilizado para HUD.
def desenhar_numero(valor, x, y, escala):
    desenhar_texto_fonte(str(valor), x, y, 24 * escala, 1.0, 0.92, 0.25, 1.0, negrito=True)


# Desenha ícone de coração para indicador de vidas.
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


# Desenha ícone de moeda para indicador de pontos.
def desenhar_moeda(x, y, escala, brilho=1.0):
    desenhar_circulo(x + 12 * escala, y + 12 * escala, 11 * escala, 1.0, 0.84, 0.22, 0.95)
    desenhar_circulo(x + 12 * escala, y + 12 * escala, 7 * escala, 1.0, 0.96, 0.55, 1.0)
    desenhar_quad_rgba(
        x + 10 * escala,
        y + 4 * escala,
        4 * escala,
        16 * escala,
        1.0,
        0.75,
        0.15,
        brilho,
    )


# Desenha HUD com vidas, pontos, fase e barra de progresso.
def desenhar_hud(vidas, pontos, fase, camera_x, comprimento_fase, tempo):
    brilho = 0.5 + 0.5 * math.sin(tempo * 4.0)
    desenhar_quad_rgba(12, ALTURA - 78, LARGURA - 24, 64, 0.02, 0.04, 0.08, 0.70)
    desenhar_quad_rgba(16, ALTURA - 74, LARGURA - 32, 56, 0.08, 0.14, 0.22, 0.88)
    desenhar_quad_rgba(18, ALTURA - 72, LARGURA - 36, 2, 0.75, 0.88, 1.0, 0.12)

    desenhar_quad_rgba(26, ALTURA - 62, 190, 36, 0.11, 0.18, 0.28, 0.92)
    desenhar_quad_rgba(32, ALTURA - 56, 28, 28, 0.00, 0.00, 0.00, 0.12)
    desenhar_coracao(31, ALTURA - 56, 0.82, 0.95 + brilho * 0.05)
    desenhar_texto_fonte("VIDAS", 72, ALTURA - 51, 18, 0.92, 0.96, 1.0, 0.82, negrito=True)
    desenhar_numero(vidas, 146, ALTURA - 56, 0.70)

    desenhar_quad_rgba(340, ALTURA - 62, 290, 36, 0.11, 0.18, 0.28, 0.92)
    desenhar_quad_rgba(356, ALTURA - 56, 28, 28, 0.00, 0.00, 0.00, 0.10)
    desenhar_moeda(353, ALTURA - 56, 0.75, 0.95)
    desenhar_texto_fonte("PONTOS", 390, ALTURA - 51, 18, 0.92, 0.96, 1.0, 0.82, negrito=True)
    desenhar_numero(pontos, 495, ALTURA - 56, 0.70)

    desenhar_quad_rgba(690, ALTURA - 62, 242, 36, 0.11, 0.18, 0.28, 0.92)
    desenhar_texto_fonte("FASE", 760, ALTURA - 51, 18, 0.92, 0.96, 1.0, 0.82, negrito=True)
    desenhar_numero(fase, 820, ALTURA - 56, 0.70)

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



# Desenha overlay da tela inicial com instruções de controle.
def desenhar_tela_inicio(tempo):
    box_w = 640
    box_h = 314
    box_x = (LARGURA - box_w) / 2
    box_y = (ALTURA - box_h) / 2 + 20

    inner_margin = 20
    inner_x = box_x + inner_margin
    inner_y = box_y + inner_margin
    inner_w = box_w - inner_margin * 2
    inner_h = box_h - inner_margin * 2

    desenhar_quad_rgba(0, 0, LARGURA, ALTURA, 0.0, 0.0, 0.0, 0.18)
    desenhar_quad_rgba(box_x, box_y, box_w, box_h, 0.02, 0.03, 0.06, 0.95)
    desenhar_quad_rgba(inner_x, inner_y, inner_w, inner_h, 0.12, 0.16, 0.24, 0.96)

    texto_x = LARGURA / 2
    titulo_y = box_y + box_h * 0.78
    controles_y = box_y + box_h * 0.62

    desenhar_texto_fonte("NICK CAGE BROS", texto_x, titulo_y, 34, 0.99, 0.92, 0.42, 1.0, centralizado=True, negrito=True)

    linhas_controle = [
        "A / < : ESQUERDA",
        "D / > : DIREITA",
        "ESPACO : PULAR",
        "ENTER : INICIAR",
        "ESC : SAIR",
    ]

    desenhar_texto_fonte("CONTROLES", texto_x, controles_y, 22, 0.98, 0.90, 0.36, 1.0, centralizado=True, negrito=True)

    espaco_linha = 20
    for i, linha in enumerate(linhas_controle):
        y_pos = controles_y - 30 - (i * espaco_linha)
        desenhar_texto_fonte(linha, texto_x, y_pos, 16, 0.90, 0.95, 1.0, 0.95, centralizado=True)

    brilho_cta = 0.60 + 0.35 * math.sin(tempo * 4.0)
    cta_y = box_y + box_h * 0.15
    desenhar_texto_fonte("PRESSIONE ENTER PARA INICIAR", texto_x, cta_y, 24, 0.98, 0.86, 0.34, 0.90 + brilho_cta * 0.10, centralizado=True, negrito=True)


# Desenha overlay de fim de jogo com opção de reinício.
def desenhar_tela_game_over(tempo):
    box_w = 340
    box_h = 214
    box_x = (LARGURA - box_w) / 2
    box_y = (ALTURA - box_h) / 2 + 20

    inner_margin = 20
    inner_x = box_x + inner_margin
    inner_y = box_y + inner_margin
    inner_w = box_w - inner_margin * 2
    inner_h = box_h - inner_margin * 2

    desenhar_quad_rgba(box_x, box_y, box_w, box_h, 0.02, 0.03, 0.06, 0.95)
    desenhar_quad_rgba(inner_x, inner_y, inner_w, inner_h, 0.12, 0.16, 0.24, 0.96)

    texto_x = LARGURA / 2
    texto_principal_y = box_y + box_h * 0.36
    texto_secundario_y = box_y + box_h * 0.64

    desenhar_texto_fonte("ENTER : REINICIAR", texto_x, texto_secundario_y, 20, 1.0, 0.92, 0.55, 1.0, centralizado=True, negrito=True)
    desenhar_texto_fonte("VOCE PERDEU", texto_x, texto_principal_y, 22, 0.98, 0.88, 0.60, 0.95, centralizado=True)

# Seleciona e desenha a tela de mensagem conforme estado atual.
def desenhar_tela_mensagem(estado, tempo):
    if estado == TELA_INICIO:
        desenhar_tela_inicio(tempo)
    if estado == GAME_OVER:
        desenhar_tela_game_over(tempo)
