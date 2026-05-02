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


def jogador_no_chao(jogador, blocos):
    area = [jogador[0] + 5, jogador[1] - 4, jogador[2] - 10, 6]
    for bloco in blocos:
        if retangulos_colidem(area, bloco):
            return True
    return False


def resolver_colisao_vertical(jogador, blocos, velocidade_y):
    esta_no_chao = False
    jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]
    for bloco in blocos:
        if retangulos_colidem(jogador_ret, bloco):
            if velocidade_y <= 0:
                jogador[1] = bloco[1] + bloco[3]
                velocidade_y = 0
                esta_no_chao = True
            else:
                jogador[1] = bloco[1] - jogador[3]
                velocidade_y = 0
            jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]
    return velocidade_y, esta_no_chao


def resolver_colisao_horizontal(jogador, blocos, deslocamento_x):
    colidiu = False
    jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]
    for bloco in blocos:
        if retangulos_colidem(jogador_ret, bloco):
            if deslocamento_x > 0:
                jogador[0] = bloco[0] - jogador[2]
            if deslocamento_x < 0:
                jogador[0] = bloco[0] + bloco[2]
            colidiu = True
            jogador_ret = [jogador[0], jogador[1], jogador[2], jogador[3]]
    return colidiu
