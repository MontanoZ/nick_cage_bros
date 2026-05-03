# Nick Cage Bros - projeto OpenGL/Python

Jogo 2D inspirado em **Super Mario Bros.**, feito com Python, GLFW, OpenGL imediato, `PIL` e `numpy`.

## Como executar

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

Execute o comando dentro da pasta do projeto, porque o código carrega as imagens a partir de `assets/`.

## Controles

- `A` ou seta esquerda: mover para esquerda
- `D` ou seta direita: mover para direita
- `Espaço`: pular
- `Enter`: iniciar/reiniciar quando estiver em tela inicial ou game over
- `ESC`: sair

## Métodos implementados no jogo:

- Janela GLFW com double buffer.
- Renderização 2D usando primitivas `GL_QUADS`.
- Carregamento de texturas com `PIL` e `numpy`.
- Gravidade simples usando `delta_time`.
- Colisão AABB entre jogador, chão, plataformas, inimigos, itens e objetivo.
- Fases geradas de modo aleatório.
- Aumento de dificuldade a cada fase.

## Arquivos

- `main.py`: jogo principal.
- `settings.py`: constantes compartilhadas.
- `collision.py`: colisões e resolução de movimento.
- `level.py`: geração aleatória das fases.
- `render.py`: textura, HUD, cenário e telas.
- `assets/`: texturas PNG usadas no jogo.
- `gerar_assets.py`: script opcional para recriar as texturas placeholder.

