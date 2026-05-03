import time

import glfw
import numpy as np

from collision import resolver_colisao_horizontal, resolver_colisao_vertical, retangulos_colidem
from level import reiniciar_jogo
from render import carregar_textura, configurar_opengl, desenhar_fundo, desenhar_hud, desenhar_jogador, desenhar_mapa, desenhar_tela_mensagem
from settings import (
    ACELERACAO_PLAYER,
    ALTURA,
    ATRITO_PLAYER,
    GAME_OVER,
    GRAVIDADE,
    JOGANDO,
    LARGURA,
    TEMPO_BUFFER_PULO,
    TEMPO_COYOTE,
    TELA_INICIO,
    TITULO,
    VELOCIDADE_PLAYER,
    VELOCIDADE_PULO,
    VIDAS_INICIAIS,
)


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

    velocidade_x = 0.0
    velocidade_y = 0.0
    camera_x = 0.0
    esta_no_chao = False
    tempo_coyote = 0.0
    tempo_buffer_pulo = 0.0
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
                velocidade_x = 0.0
                velocidade_y = 0.0
                esta_no_chao = False
                tempo_coyote = 0.0
                tempo_buffer_pulo = 0.0
                invencivel = False
                tempo_invencivel = 0.0
                espaco_antes = False
                jogador, blocos, inimigos, moedas, objetivo, comprimento_fase = reiniciar_jogo(fase)
        enter_antes = enter_agora

        if estado == JOGANDO:
            esquerda = glfw.get_key(janela, glfw.KEY_LEFT) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_A) == glfw.PRESS
            direita = glfw.get_key(janela, glfw.KEY_RIGHT) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_D) == glfw.PRESS
            direcao_x = 0
            if direita and not esquerda:
                direcao_x = 1
            elif esquerda and not direita:
                direcao_x = -1

            if direcao_x != 0:
                alvo_x = direcao_x * VELOCIDADE_PLAYER
                if velocidade_x < alvo_x:
                    velocidade_x = min(alvo_x, velocidade_x + ACELERACAO_PLAYER * delta_time)
                elif velocidade_x > alvo_x:
                    velocidade_x = max(alvo_x, velocidade_x - ACELERACAO_PLAYER * delta_time)
            else:
                if velocidade_x > 0:
                    velocidade_x = max(0.0, velocidade_x - ATRITO_PLAYER * delta_time)
                elif velocidade_x < 0:
                    velocidade_x = min(0.0, velocidade_x + ATRITO_PLAYER * delta_time)

            espaco_agora = glfw.get_key(janela, glfw.KEY_SPACE) == glfw.PRESS
            if espaco_agora and not espaco_antes:
                tempo_buffer_pulo = TEMPO_BUFFER_PULO
            espaco_antes = espaco_agora
            if tempo_buffer_pulo > 0:
                tempo_buffer_pulo -= delta_time
                if tempo_buffer_pulo < 0:
                    tempo_buffer_pulo = 0.0

            if esta_no_chao:
                tempo_coyote = TEMPO_COYOTE
            elif tempo_coyote > 0:
                tempo_coyote -= delta_time
                if tempo_coyote < 0:
                    tempo_coyote = 0.0

            if tempo_buffer_pulo > 0 and tempo_coyote > 0:
                velocidade_y = VELOCIDADE_PULO
                tempo_buffer_pulo = 0.0
                tempo_coyote = 0.0
                esta_no_chao = False

            deslocamento_x = velocidade_x * delta_time
            jogador[0] += deslocamento_x
            if resolver_colisao_horizontal(jogador, blocos, deslocamento_x):
                velocidade_x = 0.0

            velocidade_y += GRAVIDADE * delta_time
            jogador[1] += velocidade_y * delta_time
            velocidade_y, esta_no_chao = resolver_colisao_vertical(jogador, blocos, velocidade_y)
            if esta_no_chao:
                tempo_coyote = TEMPO_COYOTE

            if jogador[0] < 0:
                jogador[0] = 0
                velocidade_x = 0.0
            if jogador[0] > comprimento_fase - jogador[2]:
                jogador[0] = comprimento_fase - jogador[2]
                velocidade_x = 0.0

            jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]

            for inimigo in inimigos:
                velocidade_inimigo = 70 + fase * 12
                x_anterior = inimigo[0]
                y_anterior = inimigo[1]
                inimigo[0] += inimigo[4] * velocidade_inimigo * delta_time
                inimigo[5] += delta_time
                inimigo[1] += np.sin(inimigo[5] * 3.0) * 12.0 * delta_time
                inimigo_ret = [inimigo[0], inimigo[1], inimigo[2], inimigo[3]]
                bateu_em_bloco = False
                for bloco in blocos:
                    if retangulos_colidem(inimigo_ret, bloco):
                        bateu_em_bloco = True
                        break

                if bateu_em_bloco:
                    inimigo[0] = x_anterior
                    inimigo[1] = y_anterior
                    inimigo[4] *= -1
                else:
                    if inimigo[0] < 100:
                        inimigo[0] = 100
                        inimigo[4] = 1
                    if inimigo[0] > comprimento_fase - 200:
                        inimigo[0] = comprimento_fase - 200
                        inimigo[4] = -1

            for moeda in moedas[:]:
                if retangulos_colidem(jogador_ret, moeda):
                    pontos += 10
                    moedas.remove(moeda)

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
                        velocidade_x = 0.0
                        if vidas <= 0:
                            estado = GAME_OVER
                    break

            if jogador[1] < -120:
                vidas -= 1
                if vidas <= 0:
                    estado = GAME_OVER
                else:
                    jogador[0] = max(80, jogador[0] - 260)
                    jogador[1] = 240
                    velocidade_x = 0.0
                    velocidade_y = 0.0
                    esta_no_chao = False
                    tempo_coyote = 0.0
                    tempo_buffer_pulo = 0.0
                    invencivel = True
                    tempo_invencivel = 1.5

            if retangulos_colidem(jogador_ret, objetivo):
                fase += 1
                pontos += 100
                velocidade_x = 0.0
                velocidade_y = 0.0
                esta_no_chao = False
                tempo_coyote = 0.0
                tempo_buffer_pulo = 0.0
                jogador, blocos, inimigos, moedas, objetivo, comprimento_fase = reiniciar_jogo(fase)

            camera_x = jogador[0] - 280
            if camera_x < 0:
                camera_x = 0
            camera_maxima = comprimento_fase - LARGURA
            if camera_x > camera_maxima:
                camera_x = camera_maxima

        desenhar_fundo(texturas["sky"], camera_x, tempo_atual)
        desenhar_mapa(texturas, blocos, inimigos, moedas, objetivo, camera_x)
        desenhar_jogador(texturas, jogador, camera_x, invencivel, tempo_atual)
        desenhar_hud(vidas, pontos, fase, camera_x, comprimento_fase, tempo_atual)

        if estado == TELA_INICIO or estado == GAME_OVER:
            desenhar_tela_mensagem(estado, tempo_atual)

        glfw.swap_buffers(janela)

    glfw.destroy_window(janela)
    glfw.terminate()


if __name__ == "__main__":
    main()
