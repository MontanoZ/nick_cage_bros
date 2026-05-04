# Modelos de dados do jogo: entidades, jogador, blocos, moedas, objetivo e inimigos.

from dataclasses import dataclass
from typing import Literal

EnemyKind = Literal["abelha", "sahur"]


@dataclass

class Entidade:
    x: float
    y: float
    w: float
    h: float

    def retangulo(self) -> list[float]:
        return [self.x, self.y, self.w, self.h]


@dataclass

class Player(Entidade):
    pass


@dataclass

class Block(Entidade):
    tipo: int = 0


@dataclass

class Coin(Entidade):
    pass


@dataclass

class Goal(Entidade):
    pass


@dataclass

class Enemy(Entidade):
    tipo: EnemyKind
    direcao: int
    tempo: float = 0.0
    base_y: float = 0.0
    limite_esquerda: float = 0.0
    limite_direita: float = 0.0
