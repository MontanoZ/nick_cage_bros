from models import Block, Player


def retangulos_colidem(a, b):
    if a[0] + a[2] <= b[0]:
        return False
    if a[0] >= b[0] + b[2]:
        return False
    if a[1] + a[3] <= b[1]:
        return False
    if a[1] >= b[1] + b[3]:
        return False
    return True


def resolver_colisao_vertical(jogador: Player, blocos: list[Block], velocidade_y: float):
    esta_no_chao = False
    jogador_ret = jogador.retangulo()
    for bloco in blocos:
        if retangulos_colidem(jogador_ret, bloco.retangulo()):
            if velocidade_y <= 0:
                jogador.y = bloco.y + bloco.h
                velocidade_y = 0.0
                esta_no_chao = True
            else:
                jogador.y = bloco.y - jogador.h
                velocidade_y = 0.0
            jogador_ret = jogador.retangulo()
    return velocidade_y, esta_no_chao


def resolver_colisao_horizontal(
    jogador: Player, blocos: list[Block], deslocamento_x: float
):
    colidiu = False
    jogador_ret = jogador.retangulo()
    for bloco in blocos:
        if retangulos_colidem(jogador_ret, bloco.retangulo()):
            if deslocamento_x > 0:
                jogador.x = bloco.x - jogador.w
            if deslocamento_x < 0:
                jogador.x = bloco.x + bloco.w
            colidiu = True
            jogador_ret = jogador.retangulo()
    return colidiu
