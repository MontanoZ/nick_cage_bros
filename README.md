# Nick Cage Bros - projeto OpenGL/Python

Jogo 2D inspirado em **Super Mario Bros.**, feito com Python, GLFW, OpenGL imediato, PIL e numpy.

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
- `models.py`: modelos de dados para jogador, inimigos, itens e fases.

## Imagens do jogo

### Menu Inicial

<img width="1582" height="1035" alt="Captura de Tela 2026-05-03 às 20 20 04" src="https://github.com/user-attachments/assets/7a21e677-5223-4fbd-b01e-a0464096c44f" />

### Tela de derrota

<img width="1582" height="1035" alt="Captura de Tela 2026-05-03 às 20 20 38" src="https://github.com/user-attachments/assets/a860c5a6-4f81-44ec-8f10-f081f65bf9c3" />

### Inicio do jogo

<img width="1582" height="1035" alt="Captura de Tela 2026-05-03 às 20 20 11" src="https://github.com/user-attachments/assets/fb59603a-e4ec-4567-9aec-0120fa0183f8" />

### Inimigos, plataformas e buracos

<img width="1582" height="1035" alt="Captura de Tela 2026-05-03 às 20 20 26" src="https://github.com/user-attachments/assets/4c2c3ea0-894a-4b56-8843-68efb159ed75" />
