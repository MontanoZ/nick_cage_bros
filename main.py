# Arquivo principal do jogo: inicializa janela, loop principal, atualiza estado e renderiza cada frame.

import math
import time
from dataclasses import dataclass

import glfw

from collision import (
    resolver_colisao_horizontal,
    resolver_colisao_vertical,
    retangulos_colidem,
)
from level import reiniciar_jogo
from models import Block, Coin, Enemy, Goal, Player
from render import (
    carregar_textura,
    configurar_opengl,
    desenhar_fundo,
    desenhar_hud,
    desenhar_jogador,
    desenhar_mapa,
    desenhar_tela_mensagem,
    liberar_texturas,
)
from settings import (
    ACELERACAO_PLAYER,
    ATRITO_PLAYER,
    GAME_OVER,
    GRAVIDADE,
    JOGANDO,
    LARGURA,
    ALTURA,
    TELA_INICIO,
    TEMPO_BUFFER_PULO,
    TEMPO_COYOTE,
    TITULO,
    VELOCIDADE_PLAYER,
    VELOCIDADE_PULO,
    VIDAS_INICIAIS,
)

MARGEM_COLISAO_ABELHA = 10
MARGEM_COLISAO_SAHUR = 6


@dataclass

# Representa todo o estado mutável da partida em execução.
class EstadoJogo:
    estado: int
    fase: int
    vidas: int
    pontos: int
    jogador: Player
    blocos: list[Block]
    inimigos: list[Enemy]
    moedas: list[Coin]
    objetivo: Goal
    comprimento_fase: float
    velocidade_x: float = 0.0
    velocidade_y: float = 0.0
    camera_x: float = 0.0
    esta_no_chao: bool = False
    tempo_coyote: float = 0.0
    tempo_buffer_pulo: float = 0.0
    invencivel: bool = False
    tempo_invencivel: float = 0.0
    enter_antes: bool = False
    espaco_antes: bool = False


# Carrega todas as texturas do jogo e retorna um dicionário de IDs OpenGL.
def carregar_texturas_jogo():
    return {
        "player": carregar_textura("assets/nicolas_cage.png"),
        "bee": carregar_textura("assets/bee_enemy.png"),
        "sahur": carregar_textura("assets/tung_sahur_enemy.png"),
        "ground": carregar_textura("assets/ground.png"),
        "block": carregar_textura("assets/block.png"),
        "chest": carregar_textura("assets/chest_goal.png"),
        "coin": carregar_textura("assets/coin.png"),
        "sky": carregar_textura("assets/sky.png"),
    }


# Cria o estado inicial exibindo tela de início e fase 1 preparada.
def criar_estado_inicial():
    fase = 1
    jogador, blocos, inimigos, moedas, objetivo, comprimento_fase = reiniciar_jogo(fase)
    return EstadoJogo(
        estado=TELA_INICIO,
        fase=fase,
        vidas=VIDAS_INICIAIS,
        pontos=0,
        jogador=jogador,
        blocos=blocos,
        inimigos=inimigos,
        moedas=moedas,
        objetivo=objetivo,
        comprimento_fase=comprimento_fase,
    )


# Reseta velocidades, câmera e temporizadores ligados à movimentação do jogador.
def resetar_estado_movimento(jogo: EstadoJogo):
    jogo.velocidade_x = 0.0
    jogo.velocidade_y = 0.0
    jogo.camera_x = 0.0
    jogo.esta_no_chao = False
    jogo.tempo_coyote = 0.0
    jogo.tempo_buffer_pulo = 0.0
    jogo.invencivel = False
    jogo.tempo_invencivel = 0.0
    jogo.espaco_antes = False


# Inicia uma nova partida do zero, reiniciando fase, vidas e pontuação.
def iniciar_partida(jogo: EstadoJogo):
    jogo.estado = JOGANDO
    jogo.fase = 1
    jogo.vidas = VIDAS_INICIAIS
    jogo.pontos = 0
    resetar_estado_movimento(jogo)
    (
        jogo.jogador,
        jogo.blocos,
        jogo.inimigos,
        jogo.moedas,
        jogo.objetivo,
        jogo.comprimento_fase,
    ) = reiniciar_jogo(jogo.fase)


# Lê o teclado e converte entrada horizontal para -1, 0 ou 1.
def _entrada_horizontal(janela):
    esquerda = (
        glfw.get_key(janela, glfw.KEY_LEFT) == glfw.PRESS
        or glfw.get_key(janela, glfw.KEY_A) == glfw.PRESS
    )
    direita = (
        glfw.get_key(janela, glfw.KEY_RIGHT) == glfw.PRESS
        or glfw.get_key(janela, glfw.KEY_D) == glfw.PRESS
    )
    if direita and not esquerda:
        return 1
    if esquerda and not direita:
        return -1
    return 0


# Aplica aceleração e atrito para atualizar velocidade horizontal do jogador.
def atualizar_movimento_horizontal(janela, jogo: EstadoJogo, delta_time: float):
    direcao_x = _entrada_horizontal(janela)
    if direcao_x != 0:
        alvo_x = direcao_x * VELOCIDADE_PLAYER
        if jogo.velocidade_x < alvo_x:
            jogo.velocidade_x = min(alvo_x, jogo.velocidade_x + ACELERACAO_PLAYER * delta_time)
        elif jogo.velocidade_x > alvo_x:
            jogo.velocidade_x = max(alvo_x, jogo.velocidade_x - ACELERACAO_PLAYER * delta_time)
    else:
        if jogo.velocidade_x > 0:
            jogo.velocidade_x = max(0.0, jogo.velocidade_x - ATRITO_PLAYER * delta_time)
        elif jogo.velocidade_x < 0:
            jogo.velocidade_x = min(0.0, jogo.velocidade_x + ATRITO_PLAYER * delta_time)


# Gerencia buffer de pulo e tempo coyote para melhorar responsividade do salto.
def atualizar_buffer_pulo(janela, jogo: EstadoJogo, delta_time: float):
    espaco_agora = glfw.get_key(janela, glfw.KEY_SPACE) == glfw.PRESS
    if espaco_agora and not jogo.espaco_antes:
        jogo.tempo_buffer_pulo = TEMPO_BUFFER_PULO
    jogo.espaco_antes = espaco_agora

    if jogo.tempo_buffer_pulo > 0:
        jogo.tempo_buffer_pulo = max(0.0, jogo.tempo_buffer_pulo - delta_time)

    if jogo.esta_no_chao:
        jogo.tempo_coyote = TEMPO_COYOTE
    elif jogo.tempo_coyote > 0:
        jogo.tempo_coyote = max(0.0, jogo.tempo_coyote - delta_time)

    if jogo.tempo_buffer_pulo > 0 and jogo.tempo_coyote > 0:
        jogo.velocidade_y = VELOCIDADE_PULO
        jogo.tempo_buffer_pulo = 0.0
        jogo.tempo_coyote = 0.0
        jogo.esta_no_chao = False


# Atualiza física do jogador, resolve colisões e limita posição na fase.
def atualizar_fisica_jogador(jogo: EstadoJogo, delta_time: float):
    deslocamento_x = jogo.velocidade_x * delta_time
    jogo.jogador.x += deslocamento_x
    if resolver_colisao_horizontal(jogo.jogador, jogo.blocos, deslocamento_x):
        jogo.velocidade_x = 0.0

    jogo.velocidade_y += GRAVIDADE * delta_time
    jogo.jogador.y += jogo.velocidade_y * delta_time
    jogo.velocidade_y, jogo.esta_no_chao = resolver_colisao_vertical(
        jogo.jogador, jogo.blocos, jogo.velocidade_y
    )
    if jogo.esta_no_chao:
        jogo.tempo_coyote = TEMPO_COYOTE

    if jogo.jogador.x < 0:
        jogo.jogador.x = 0
        jogo.velocidade_x = 0.0
    if jogo.jogador.x > jogo.comprimento_fase - jogo.jogador.w:
        jogo.jogador.x = jogo.comprimento_fase - jogo.jogador.w
        jogo.velocidade_x = 0.0


# Verifica se uma entidade está colidindo com algum bloco do mapa.
def _colide_com_bloco(entidade, blocos: list[Block]):
    entidade_ret = entidade.retangulo()
    for bloco in blocos:
        if retangulos_colidem(entidade_ret, bloco.retangulo()):
            return True
    return False


# Atualiza movimento e direção dos inimigos conforme tipo e colisões.
def atualizar_inimigos(jogo: EstadoJogo, delta_time: float):
    velocidade_base = 70 + jogo.fase * 12
    for inimigo in jogo.inimigos:
        x_anterior = inimigo.x
        y_anterior = inimigo.y

        if inimigo.tipo == "abelha":
            inimigo.x += inimigo.direcao * velocidade_base * delta_time
            inimigo.tempo += delta_time
            inimigo.y = inimigo.base_y + math.sin(inimigo.tempo * 3.0) * 12.0
        else:
            velocidade_sahur = velocidade_base * 0.75
            inimigo.x += inimigo.direcao * velocidade_sahur * delta_time
            inimigo.y = inimigo.base_y

            if inimigo.x <= inimigo.limite_esquerda:
                inimigo.x = inimigo.limite_esquerda
                inimigo.direcao = 1
            if inimigo.x >= inimigo.limite_direita:
                inimigo.x = inimigo.limite_direita
                inimigo.direcao = -1

        if _colide_com_bloco(inimigo, jogo.blocos):
            inimigo.x = x_anterior
            inimigo.y = y_anterior
            inimigo.direcao *= -1
        elif inimigo.tipo == "abelha":
            if inimigo.x < 100:
                inimigo.x = 100
                inimigo.direcao = 1
            if inimigo.x > jogo.comprimento_fase - 200:
                inimigo.x = jogo.comprimento_fase - 200
                inimigo.direcao = -1


# Detecta coleta de moedas e soma pontos ao jogador.
def coletar_moedas(jogo: EstadoJogo):
    jogador_ret = jogo.jogador.retangulo()
    for moeda in jogo.moedas[:]:
        if retangulos_colidem(jogador_ret, moeda.retangulo()):
            jogo.pontos += 10
            jogo.moedas.remove(moeda)


# Atualiza o temporizador de invencibilidade após receber dano.
def atualizar_invencibilidade(jogo: EstadoJogo, delta_time: float):
    if jogo.tempo_invencivel > 0:
        jogo.tempo_invencivel -= delta_time
        if jogo.tempo_invencivel <= 0:
            jogo.invencivel = False


# Calcula hitbox de dano do inimigo com margem para colisão mais justa.
def _retangulo_dano_inimigo(inimigo: Enemy):
    margem = MARGEM_COLISAO_ABELHA if inimigo.tipo == "abelha" else MARGEM_COLISAO_SAHUR
    largura = max(8.0, inimigo.w - margem * 2)
    altura = max(8.0, inimigo.h - margem * 2)
    return [
        inimigo.x + margem,
        inimigo.y + margem,
        largura,
        altura,
    ]


# Aplica dano ao jogador ou elimina sahur ao pulo por cima.
def aplicar_dano_inimigos(jogo: EstadoJogo):
    if jogo.invencivel:
        return

    jogador_ret = jogo.jogador.retangulo()
    for inimigo in jogo.inimigos[:]:
        inimigo_ret = _retangulo_dano_inimigo(inimigo)
        if retangulos_colidem(jogador_ret, inimigo_ret):
            caiu_em_cima_do_sahur = (
                inimigo.tipo == "sahur"
                and jogo.velocidade_y < 0
                and jogo.jogador.y >= inimigo.y + inimigo.h - 12
            )
            if caiu_em_cima_do_sahur:
                jogo.inimigos.remove(inimigo)
                jogo.pontos += 20
                jogo.velocidade_y = VELOCIDADE_PULO * 0.65
                jogo.esta_no_chao = False
                break

            jogo.vidas -= 1
            jogo.invencivel = True
            jogo.tempo_invencivel = 1.5
            jogo.jogador.x -= 45
            jogo.velocidade_y = 360
            jogo.velocidade_x = 0.0
            if jogo.vidas <= 0:
                jogo.estado = GAME_OVER
            break


# Processa queda fora do mapa, consumindo vida e reposicionando o jogador.
def processar_queda(jogo: EstadoJogo):
    if jogo.jogador.y >= -120:
        return

    jogo.vidas -= 1
    if jogo.vidas <= 0:
        jogo.estado = GAME_OVER
        return

    jogo.jogador.x = max(80, jogo.jogador.x - 260)
    jogo.jogador.y = 240
    jogo.velocidade_x = 0.0
    jogo.velocidade_y = 0.0
    jogo.esta_no_chao = False
    jogo.tempo_coyote = 0.0
    jogo.tempo_buffer_pulo = 0.0
    jogo.invencivel = True
    jogo.tempo_invencivel = 1.5


# Avança para a próxima fase quando o jogador alcança o objetivo.
def avancar_fase(jogo: EstadoJogo):
    if not retangulos_colidem(jogo.jogador.retangulo(), jogo.objetivo.retangulo()):
        return

    jogo.fase += 1
    jogo.pontos += 100
    jogo.velocidade_x = 0.0
    jogo.velocidade_y = 0.0
    jogo.esta_no_chao = False
    jogo.tempo_coyote = 0.0
    jogo.tempo_buffer_pulo = 0.0
    (
        jogo.jogador,
        jogo.blocos,
        jogo.inimigos,
        jogo.moedas,
        jogo.objetivo,
        jogo.comprimento_fase,
    ) = reiniciar_jogo(jogo.fase)


# Centraliza a câmera no jogador respeitando limites da fase.
def atualizar_camera(jogo: EstadoJogo):
    jogo.camera_x = jogo.jogador.x - 280
    if jogo.camera_x < 0:
        jogo.camera_x = 0
    camera_maxima = jogo.comprimento_fase - LARGURA
    if jogo.camera_x > camera_maxima:
        jogo.camera_x = camera_maxima


# Executa o ciclo completo de atualização de gameplay no frame.
def atualizar_jogo(janela, jogo: EstadoJogo, delta_time: float):
    atualizar_movimento_horizontal(janela, jogo, delta_time)
    atualizar_buffer_pulo(janela, jogo, delta_time)
    atualizar_fisica_jogador(jogo, delta_time)
    atualizar_inimigos(jogo, delta_time)
    coletar_moedas(jogo)
    atualizar_invencibilidade(jogo, delta_time)
    aplicar_dano_inimigos(jogo)
    processar_queda(jogo)
    avancar_fase(jogo)
    atualizar_camera(jogo)


# Renderiza fundo, mapa, jogador, HUD e telas de mensagem.
def desenhar_frame(texturas, jogo: EstadoJogo, tempo_atual: float):
    desenhar_fundo(texturas["sky"], jogo.camera_x, tempo_atual)
    desenhar_mapa(
        texturas,
        jogo.blocos,
        jogo.inimigos,
        jogo.moedas,
        jogo.objetivo,
        jogo.camera_x,
    )
    desenhar_jogador(
        texturas,
        jogo.jogador,
        jogo.camera_x,
        jogo.invencivel,
        tempo_atual,
    )
    desenhar_hud(
        jogo.vidas,
        jogo.pontos,
        jogo.fase,
        jogo.camera_x,
        jogo.comprimento_fase,
        tempo_atual,
    )
    if jogo.estado in (TELA_INICIO, GAME_OVER):
        desenhar_tela_mensagem(jogo.estado, tempo_atual)


# Ponto de entrada: configura GLFW/OpenGL e executa o loop principal do jogo.
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

    texturas = carregar_texturas_jogo()
    jogo = criar_estado_inicial()
    tempo_anterior = time.time()

    while not glfw.window_should_close(janela):
        tempo_atual = time.time()
        delta_time = min(tempo_atual - tempo_anterior, 0.05)
        tempo_anterior = tempo_atual

        glfw.poll_events()

        if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(janela, True)

        enter_agora = glfw.get_key(janela, glfw.KEY_ENTER) == glfw.PRESS
        if enter_agora and not jogo.enter_antes and jogo.estado in (TELA_INICIO, GAME_OVER):
            iniciar_partida(jogo)
        jogo.enter_antes = enter_agora

        if jogo.estado == JOGANDO:
            atualizar_jogo(janela, jogo, delta_time)

        desenhar_frame(texturas, jogo, tempo_atual)
        glfw.swap_buffers(janela)

    liberar_texturas(texturas)
    glfw.destroy_window(janela)
    glfw.terminate()


if __name__ == "__main__":
    main()
