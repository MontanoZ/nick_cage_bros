import random

from collision import retangulos_colidem
from models import Block, Coin, Enemy, Goal, Player
from settings import (
    ALTURA_PLAYER,
    ALTURAS_PLATAFORMA,
    LARGURA_MAX_PLATAFORMA,
    LARGURA_MIN_PLATAFORMA,
    LARGURA_PLAYER,
    MAX_FASE_DIFICULDADE,
    MAX_INIMIGOS,
    TAMANHO_TILE,
)

BURACO_MIN_TAMANHO = 1
BURACO_MAX_TAMANHO = 3
NIVEIS_PLATAFORMA = ALTURAS_PLATAFORMA
MARGEM_INICIO = 8 * TAMANHO_TILE
MARGEM_FIM = 8 * TAMANHO_TILE
SOLIDO_ENTRE_BURACOS_MINIMO = 2 * TAMANHO_TILE
SOLIDO_ENTRE_BURACOS_BASE = 4 * TAMANHO_TILE
MARGEM_PROTECAO_PLATAFORMA = {
    2: TAMANHO_TILE // 2,
    1: TAMANHO_TILE // 2,
    0: TAMANHO_TILE // 2,
}
NIVEIS_VOO_ABELHA = (TAMANHO_TILE, ALTURAS_PLATAFORMA[0])
TAMANHO_ABELHA = 40
TAMANHO_SAHUR = (44, 66)
TRECHO_CHAO_MIN_TILES = 5
TRECHO_CHAO_MAX_TILES = 10


def _intervalos_colidem(a_inicio, a_fim, b_inicio, b_fim):
    return a_inicio < b_fim and a_fim > b_inicio


def _adicionar_plataforma(plataformas, protecoes, x, nivel, largura_tiles):
    y = NIVEIS_PLATAFORMA[nivel]
    largura = largura_tiles * TAMANHO_TILE
    plataforma = Block(float(x), float(y), float(largura), float(TAMANHO_TILE), tipo=1)
    plataformas.append(plataforma)
    margem = MARGEM_PROTECAO_PLATAFORMA[nivel]
    if margem > 0:
        protecoes.append((x - margem, x + margem))
        protecoes.append((x + largura - margem, x + largura + margem))


def _intervalo_colide_com_protecao(inicio, fim, protecoes):
    for protecao_inicio, protecao_fim in protecoes:
        if _intervalos_colidem(inicio, fim, protecao_inicio, protecao_fim):
            return True
    return False


def _chance_buraco(dificuldade):
    return min(18 + dificuldade * 4, 58)


def _quantidade_minima_buracos(comprimento, dificuldade):
    tiles_uteis = max(1, (comprimento - MARGEM_INICIO - MARGEM_FIM) // TAMANHO_TILE)
    quantidade_por_dificuldade = 2 + dificuldade // 2
    quantidade_por_comprimento = tiles_uteis // max(14, 26 - dificuldade)
    return max(quantidade_por_dificuldade, quantidade_por_comprimento)


def _espaco_solido_entre_buracos(dificuldade):
    reducao = min(dificuldade // 3, 2) * TAMANHO_TILE
    return max(SOLIDO_ENTRE_BURACOS_MINIMO, SOLIDO_ENTRE_BURACOS_BASE - reducao)


def _tamanho_maximo_buraco(dificuldade):
    if dificuldade < 3:
        return 1
    if dificuldade < 8:
        return 2
    return BURACO_MAX_TAMANHO


def _pode_adicionar_buraco(inicio, fim, buracos, protecoes, espaco_solido):
    if _intervalo_colide_com_protecao(inicio, fim, protecoes):
        return False

    for buraco_inicio, buraco_fim in buracos:
        if inicio < buraco_fim + espaco_solido and fim > buraco_inicio - espaco_solido:
            return False

    return True


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


def _gerar_plataformas(comprimento, dificuldade):
    plataformas = []
    protecoes = []
    x = MARGEM_INICIO
    limite_util = comprimento - MARGEM_FIM
    nivel_atual = 0
    passou_por_trecho_chao = False
    while x < limite_util:
        if not passou_por_trecho_chao and x > comprimento * 0.45:
            tamanho_trecho_chao = random.randint(
                TRECHO_CHAO_MIN_TILES, TRECHO_CHAO_MAX_TILES
            )
            x += tamanho_trecho_chao * TAMANHO_TILE
            nivel_atual = 0
            passou_por_trecho_chao = True
            continue

        chance_trecho_chao = min(10 + dificuldade * 2, 32)
        if random.randint(0, 100) < chance_trecho_chao:
            tamanho_trecho_chao = random.randint(
                TRECHO_CHAO_MIN_TILES, TRECHO_CHAO_MAX_TILES
            )
            x += tamanho_trecho_chao * TAMANHO_TILE
            nivel_atual = 0
            continue

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
        if (
            indice_buraco < len(buracos)
            and buracos[indice_buraco][0] <= x < buracos[indice_buraco][1]
        ):
            x = buracos[indice_buraco][1]
            indice_buraco += 1
            continue
        blocos.append(Block(float(x), 0.0, float(TAMANHO_TILE), float(TAMANHO_TILE), tipo=0))
        x += TAMANHO_TILE
    return blocos


def _gerar_buracos(comprimento, dificuldade, protecoes):
    buracos = []
    x = 0
    espaco_solido = _espaco_solido_entre_buracos(dificuldade)
    ultimo_fim_buraco = -espaco_solido
    while x < comprimento:
        if x <= MARGEM_INICIO or x >= comprimento - MARGEM_FIM:
            x += TAMANHO_TILE
            continue

        pode_criar_buraco = x - ultimo_fim_buraco >= espaco_solido
        chance_buraco = _chance_buraco(dificuldade)
        if pode_criar_buraco and random.randint(0, 100) < chance_buraco:
            tamanho_buraco = random.randint(
                BURACO_MIN_TAMANHO, _tamanho_maximo_buraco(dificuldade)
            )
            inicio = x
            fim = x + tamanho_buraco * TAMANHO_TILE
            if _pode_adicionar_buraco(inicio, fim, buracos, protecoes, espaco_solido):
                buracos.append((inicio, fim))
                ultimo_fim_buraco = fim
                x = fim + espaco_solido
                continue
        x += TAMANHO_TILE

    quantidade_minima = _quantidade_minima_buracos(comprimento, dificuldade)
    tamanho_maximo = _tamanho_maximo_buraco(dificuldade)
    while len(buracos) < quantidade_minima:
        candidatos = []
        for tamanho_buraco in range(tamanho_maximo, BURACO_MIN_TAMANHO - 1, -1):
            tile_inicio = MARGEM_INICIO // TAMANHO_TILE + 1
            tile_fim = (comprimento - MARGEM_FIM) // TAMANHO_TILE - tamanho_buraco
            for tile_x in range(tile_inicio, tile_fim + 1):
                inicio = tile_x * TAMANHO_TILE
                fim = inicio + tamanho_buraco * TAMANHO_TILE
                if _pode_adicionar_buraco(inicio, fim, buracos, protecoes, espaco_solido):
                    candidatos.append((inicio, fim))

            if candidatos:
                break

        if not candidatos:
            break

        buracos.append(random.choice(candidatos))

    buracos.sort()
    return buracos


def _retangulo_colide_com_blocos(retangulo, blocos):
    for bloco in blocos:
        if retangulos_colidem(retangulo, bloco.retangulo()):
            return True
    return False


def _segmentos_de_suporte(blocos: list[Block]):
    blocos_ordenados = sorted(blocos, key=lambda bloco: (bloco.y, bloco.x))
    segmentos = []
    indice = 0
    while indice < len(blocos_ordenados):
        bloco = blocos_ordenados[indice]
        y = bloco.y
        inicio = bloco.x
        fim = bloco.x + bloco.w
        indice += 1

        while indice < len(blocos_ordenados):
            proximo = blocos_ordenados[indice]
            if proximo.y != y:
                break
            if proximo.x > fim + 0.5:
                break
            fim = max(fim, proximo.x + proximo.w)
            indice += 1

        segmentos.append((inicio, fim, y + bloco.h))

    return segmentos


def _gerar_abelha_sem_colisao(comprimento, blocos):
    for _ in range(80):
        ex = random.randint(8, int(comprimento / TAMANHO_TILE) - 4) * TAMANHO_TILE
        ey_base = random.choice(NIVEIS_VOO_ABELHA)
        abelha = Enemy(
            tipo="abelha",
            x=float(ex),
            y=float(ey_base),
            w=float(TAMANHO_ABELHA),
            h=float(TAMANHO_ABELHA),
            direcao=random.choice([-1, 1]),
            tempo=0.0,
            base_y=float(ey_base),
        )
        if not _retangulo_colide_com_blocos(abelha.retangulo(), blocos):
            return abelha
    return None


def _gerar_sahur_sem_colisao(blocos, inimigos):
    largura, altura = TAMANHO_SAHUR
    suportes = _segmentos_de_suporte(blocos)
    random.shuffle(suportes)

    for suporte_inicio, suporte_fim, suporte_topo in suportes[:220]:
        largura_suporte = suporte_fim - suporte_inicio
        if largura_suporte < largura + 8:
            continue

        min_x = int(suporte_inicio + 4)
        max_x = int(suporte_fim - largura - 4)
        if max_x <= min_x:
            continue

        sx = random.randint(min_x, max_x)
        sy = suporte_topo
        sahur_ret = [sx, sy, largura, altura]
        if _retangulo_colide_com_blocos(sahur_ret, blocos):
            continue

        colide_inimigo = False
        for inimigo in inimigos:
            if retangulos_colidem(sahur_ret, inimigo.retangulo()):
                colide_inimigo = True
                break
        if colide_inimigo:
            continue

        limite_esquerda = max(suporte_inicio + 2, sx - 3 * TAMANHO_TILE)
        limite_direita = min(suporte_fim - largura - 2, sx + 3 * TAMANHO_TILE)
        if limite_direita - limite_esquerda < TAMANHO_TILE:
            continue

        return Enemy(
            tipo="sahur",
            x=float(sx),
            y=float(sy),
            w=float(largura),
            h=float(altura),
            direcao=random.choice([-1, 1]),
            tempo=0.0,
            base_y=float(sy),
            limite_esquerda=float(limite_esquerda),
            limite_direita=float(limite_direita),
        )

    return None


def criar_fase(numero_fase):
    blocos: list[Block] = []
    inimigos: list[Enemy] = []
    moedas: list[Coin] = []

    dificuldade = min(max(1, numero_fase), MAX_FASE_DIFICULDADE)
    comprimento = 2300 + dificuldade * 450
    plataformas, protecoes = _gerar_plataformas(comprimento, dificuldade)
    buracos = _gerar_buracos(comprimento, dificuldade, protecoes)
    blocos.extend(_preencher_chao(comprimento, buracos))

    for plataforma in plataformas:
        tamanho = int(plataforma.w / TAMANHO_TILE)
        for j in range(tamanho):
            blocos.append(
                Block(
                    plataforma.x + j * TAMANHO_TILE,
                    plataforma.y,
                    float(TAMANHO_TILE),
                    float(TAMANHO_TILE),
                    tipo=1,
                )
            )
        moedas.append(Coin(plataforma.x + TAMANHO_TILE, plataforma.y + 60, 24.0, 24.0))

    quantidade_inimigos = min(4 + dificuldade * 2, MAX_INIMIGOS)
    quantidade_sahur = min(max(1, dificuldade // 2), max(2, MAX_INIMIGOS // 3))
    tentativas_sem_colisao = 0
    while (
        len(inimigos) < quantidade_inimigos
        and tentativas_sem_colisao < quantidade_inimigos * 4
    ):
        abelha = _gerar_abelha_sem_colisao(comprimento, blocos)
        if abelha is not None:
            inimigos.append(abelha)
        tentativas_sem_colisao += 1

    tentativas_sahur = 0
    while (
        len([i for i in inimigos if i.tipo == "sahur"]) < quantidade_sahur
        and tentativas_sahur < quantidade_sahur * 8
    ):
        sahur = _gerar_sahur_sem_colisao(blocos, inimigos)
        if sahur is not None:
            inimigos.append(sahur)
        tentativas_sahur += 1

    objetivo = Goal(float(comprimento - 160), float(TAMANHO_TILE), 64.0, 64.0)
    return blocos, inimigos, moedas, objetivo, float(comprimento)


def reiniciar_jogo(numero_fase):
    blocos, inimigos, moedas, objetivo, comprimento = criar_fase(numero_fase)
    jogador = Player(80.0, 170.0, float(LARGURA_PLAYER), float(ALTURA_PLAYER))
    return jogador, blocos, inimigos, moedas, objetivo, comprimento
