import random

from settings import (
    ALTURAS_PLATAFORMA,
    LARGURA_MAX_PLATAFORMA,
    LARGURA_MIN_PLATAFORMA,
    LARGURA_PLAYER,
    ALTURA_PLAYER,
    MAX_FASE_DIFICULDADE,
    MAX_INIMIGOS,
    TAMANHO_TILE,
)

BURACO_MIN_TAMANHO = 1
BURACO_MAX_TAMANHO = 2
NIVEIS_PLATAFORMA = ALTURAS_PLATAFORMA
MARGEM_INICIO = 8 * TAMANHO_TILE
MARGEM_FIM = 8 * TAMANHO_TILE
SOLIDO_ENTRE_BURACOS = 4 * TAMANHO_TILE
MARGEM_PROTECAO_PLATAFORMA = {
    2: 3 * TAMANHO_TILE,
    1: 2 * TAMANHO_TILE,
    0: 1 * TAMANHO_TILE,
}
PADROES_SEGMENTO = (
    (0,),
    (0, 1),
    (0, 1, 2),
)


def _intervalos_colidem(a_inicio, a_fim, b_inicio, b_fim):
    return a_inicio < b_fim and a_fim > b_inicio


def _adicionar_plataforma(plataformas, protecoes, x, nivel, largura_tiles):
    y = NIVEIS_PLATAFORMA[nivel]
    largura = largura_tiles * TAMANHO_TILE
    plataforma = [x, y, largura, TAMANHO_TILE, 1]
    plataformas.append(plataforma)
    margem = MARGEM_PROTECAO_PLATAFORMA[nivel]
    protecoes.append((x - margem, x + largura + margem))


def _intervalo_colide_com_protecao(inicio, fim, protecoes):
    for protecao_inicio, protecao_fim in protecoes:
        if _intervalos_colidem(inicio, fim, protecao_inicio, protecao_fim):
            return True
    return False


def _escolher_padrao_segmento(dificuldade):
    pesos = []
    for padrao in PADROES_SEGMENTO:
        if len(padrao) == 1:
            peso = 8 + dificuldade
        elif len(padrao) == 2:
            if padrao == (0, 1):
                peso = 28 + dificuldade
            else:
                peso = 22 + dificuldade
        else:
            peso = 18 + dificuldade
        pesos.append(peso)
    return random.choices(PADROES_SEGMENTO, weights=pesos, k=1)[0]


def _gerar_trecho_plataformas(plataformas, protecoes, x, nivel, limite_x, dificuldade):
    while x < limite_x:
        largura_maxima = min(LARGURA_MAX_PLATAFORMA, (limite_x - x) // TAMANHO_TILE)
        if largura_maxima < LARGURA_MIN_PLATAFORMA:
            break

        if dificuldade < 4:
            largura_minima = 2
            largura_maxima_efetiva = min(3, largura_maxima)
        else:
            largura_minima = LARGURA_MIN_PLATAFORMA
            largura_maxima_efetiva = min(4, largura_maxima)

        largura = random.randint(largura_minima, largura_maxima_efetiva)
        _adicionar_plataforma(plataformas, protecoes, x, nivel, largura)
        x += largura * TAMANHO_TILE

        if x >= limite_x:
            break

        x += random.randint(1, 2) * TAMANHO_TILE

    return x


def _escolher_nivel_proximo(nivel_atual, espaco_restante, dificuldade):
    if espaco_restante <= 10 * TAMANHO_TILE:
        return max(0, nivel_atual - 1)

    niveis = [nivel_atual]
    pesos = [8]

    if nivel_atual > 0:
        niveis.append(nivel_atual - 1)
        pesos.append(4 + dificuldade)

    if nivel_atual < len(NIVEIS_PLATAFORMA) - 1:
        niveis.append(nivel_atual + 1)
        pesos.append(3 + dificuldade)

    return random.choices(niveis, weights=pesos, k=1)[0]


def _espaco_entre_plataformas(nivel_atual, proximo_nivel, dificuldade):
    if proximo_nivel < nivel_atual:
        return random.randint(1, 2) * TAMANHO_TILE
    if proximo_nivel > nivel_atual:
        if dificuldade < 4:
            return random.randint(2, 3) * TAMANHO_TILE
        return random.randint(2, 4) * TAMANHO_TILE
    return random.randint(3, 5) * TAMANHO_TILE


def _gerar_segmento(plataformas, protecoes, x, limite_x, dificuldade):
    padrao = _escolher_padrao_segmento(dificuldade)
    niveis = list(padrao)
    if len(niveis) == 1:
        return _gerar_trecho_plataformas(plataformas, protecoes, x, niveis[0], limite_x, dificuldade)

    espaco_total = max(TAMANHO_TILE * 8, limite_x - x)
    if len(niveis) == 2:
        cortes = [random.uniform(0.42, 0.60)]
    else:
        cortes = sorted([random.uniform(0.28, 0.42), random.uniform(0.58, 0.78)])

    limites = [x]
    for corte in cortes:
        limites.append(int(x + espaco_total * corte))
    limites.append(limite_x)

    x_atual = x
    for indice, nivel in enumerate(niveis):
        x_atual = _gerar_trecho_plataformas(
            plataformas,
            protecoes,
            x_atual,
            nivel,
            limites[indice + 1],
            dificuldade,
        )
        if indice < len(niveis) - 1:
            x_atual += random.randint(1, 2) * TAMANHO_TILE
    return x_atual


def _gerar_plataformas(comprimento, dificuldade):
    plataformas = []
    protecoes = []
    x = MARGEM_INICIO
    limite_util = comprimento - MARGEM_FIM
    nivel_atual = 0
    while x < limite_util:
        espaco_restante = limite_util - x
        if espaco_restante < 6 * TAMANHO_TILE:
            nivel_atual = 0
        elif espaco_restante < 12 * TAMANHO_TILE:
            nivel_atual = max(0, nivel_atual - 1)

        largura_maxima = min(LARGURA_MAX_PLATAFORMA, (limite_util - x) // TAMANHO_TILE)
        if largura_maxima < LARGURA_MIN_PLATAFORMA:
            break

        if dificuldade < 4:
            largura_minima = 2
            largura_maxima_efetiva = min(3, largura_maxima)
        else:
            largura_minima = LARGURA_MIN_PLATAFORMA
            largura_maxima_efetiva = min(4, largura_maxima)

        largura = random.randint(largura_minima, largura_maxima_efetiva)
        _adicionar_plataforma(plataformas, protecoes, x, nivel_atual, largura)
        x += largura * TAMANHO_TILE

        if x >= limite_util:
            break

        proximo_nivel = _escolher_nivel_proximo(nivel_atual, limite_util - x, dificuldade)
        x += _espaco_entre_plataformas(nivel_atual, proximo_nivel, dificuldade)
        nivel_atual = proximo_nivel

    return plataformas, protecoes


def _preencher_chao(comprimento, buracos):
    blocos = []
    x = 0
    indice_buraco = 0
    while x < comprimento:
        if indice_buraco < len(buracos) and buracos[indice_buraco][0] <= x < buracos[indice_buraco][1]:
            x = buracos[indice_buraco][1]
            indice_buraco += 1
            continue
        blocos.append([x, 0, TAMANHO_TILE, TAMANHO_TILE, 0])
        x += TAMANHO_TILE
    return blocos


def _gerar_buracos(comprimento, dificuldade, protecoes):
    buracos = []
    x = 0
    ultimo_fim_buraco = -SOLIDO_ENTRE_BURACOS
    while x < comprimento:
        if x <= MARGEM_INICIO or x >= comprimento - MARGEM_FIM:
            x += TAMANHO_TILE
            continue

        pode_criar_buraco = x - ultimo_fim_buraco >= SOLIDO_ENTRE_BURACOS
        chance_buraco = min(10 + dificuldade * 2, 22)
        if pode_criar_buraco and random.randint(0, 100) < chance_buraco:
            tamanho_maximo_buraco = 1 if dificuldade < 6 else BURACO_MAX_TAMANHO
            tamanho_buraco = random.randint(BURACO_MIN_TAMANHO, tamanho_maximo_buraco)
            inicio = x
            fim = x + tamanho_buraco * TAMANHO_TILE
            if not _intervalo_colide_com_protecao(inicio, fim, protecoes):
                buracos.append((inicio, fim))
                ultimo_fim_buraco = fim
                x = fim + SOLIDO_ENTRE_BURACOS
                continue
        x += TAMANHO_TILE
    return buracos


def criar_fase(numero_fase):
    blocos = []
    inimigos = []
    moedas = []

    dificuldade = min(max(1, numero_fase), MAX_FASE_DIFICULDADE)
    comprimento = 2300 + dificuldade * 450
    plataformas, protecoes = _gerar_plataformas(comprimento, dificuldade)
    buracos = _gerar_buracos(comprimento, dificuldade, protecoes)
    blocos.extend(_preencher_chao(comprimento, buracos))

    for plataforma in plataformas:
        tamanho = int(plataforma[2] / TAMANHO_TILE)
        for j in range(tamanho):
            blocos.append([plataforma[0] + j * TAMANHO_TILE, plataforma[1], TAMANHO_TILE, TAMANHO_TILE, 1])
        moedas.append([plataforma[0] + TAMANHO_TILE, plataforma[1] + 60, 24, 24])

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
