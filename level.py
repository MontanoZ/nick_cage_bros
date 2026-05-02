import random

from settings import (
    LARGURA_PLAYER,
    ALTURA_PLAYER,
    MAX_FASE_DIFICULDADE,
    MAX_INIMIGOS,
    MAX_PLATAFORMAS,
    TAMANHO_TILE,
)


def criar_fase(numero_fase):
    blocos = []
    inimigos = []
    moedas = []

    dificuldade = min(max(1, numero_fase), MAX_FASE_DIFICULDADE)
    comprimento = 2300 + dificuldade * 450

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

    quantidade_plataformas = min(5 + dificuldade, MAX_PLATAFORMAS)
    for i in range(quantidade_plataformas):
        px = random.randint(5, int(comprimento / TAMANHO_TILE) - 7) * TAMANHO_TILE
        py = random.choice([160, 215, 270])
        tamanho = random.randint(2, 5)
        for j in range(tamanho):
            blocos.append([px + j * TAMANHO_TILE, py, TAMANHO_TILE, TAMANHO_TILE, 1])
        moedas.append([px + TAMANHO_TILE, py + 60, 24, 24])

    quantidade_inimigos = min(4 + dificuldade * 2, MAX_INIMIGOS)
    for i in range(quantidade_inimigos):
        ex = random.randint(8, int(comprimento / TAMANHO_TILE) - 4) * TAMANHO_TILE
        ey = random.choice([TAMANHO_TILE, 112, 170])
        inimigos.append([ex, ey, 40, 40, random.choice([-1, 1]), 0])

    objetivo = [comprimento - 160, TAMANHO_TILE, 64, 64]
    return blocos, inimigos, moedas, objetivo, comprimento


def reiniciar_jogo(numero_fase):
    blocos, inimigos, moedas, objetivo, comprimento = criar_fase(numero_fase)
    jogador = [80, 170, LARGURA_PLAYER, ALTURA_PLAYER]
    return jogador, blocos, inimigos, moedas, objetivo, comprimento
