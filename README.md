# Nick Cage Bros - projeto OpenGL/Python

Jogo 2D inspirado em **Super Mario Bros.** com tema do Nicolas Cage, feito com Python, GLFW, OpenGL imediato, `PIL` e `numpy`.

## Como executar

```bash
python -m pip install -r requirements.txt
python main.py
```

Execute o comando dentro da pasta do projeto, porque o código carrega as imagens a partir de `assets/`.

## Controles

- `A` ou seta esquerda: mover para esquerda
- `D` ou seta direita: mover para direita
- `Espaço`: pular
- `Enter`: iniciar/reiniciar quando estiver em tela inicial ou game over
- `ESC`: sair

## O que já foi implementado

- Janela GLFW com double buffer.
- Renderização 2D usando primitivas `GL_QUADS`.
- Carregamento de texturas com `PIL` e `numpy`.
- Personagem principal com movimento lateral e pulo.
- Gravidade simples usando `delta_time`.
- Colisão AABB entre jogador, chão, plataformas, inimigos, itens e objetivo.
- Contador de vidas e pontuação desenhados com primitivas geométricas.
- Fases geradas de modo aleatório.
- Aumento de dificuldade a cada fase.
- O jogo só termina quando as vidas chegam a zero.

## Requisitos do enunciado

- Bibliotecas usadas: `PyOpenGL_accelerate`, `glfw`, `Pillow (PIL)`, `time`, `numpy`, `random`.
- Personagem se movimenta com teclado.
- Tratamento de colisão entre jogador, cenário, inimigos, moedas e objetivo.
- Contador de vidas visível na HUD.
- Fim de jogo apenas quando as vidas acabam.
- Fases aleatórias com dificuldade crescente.
- Uso de comandos de OpenGL imediato vistos em aula.

## Ideia do tema

O protagonista é um personagem de pixel art inspirado em Nicolas Cage. Os inimigos e objetos seguem temas associados de forma paródica: abelhas, tesouros, pergaminhos e blocos de filme. As imagens são placeholders originais em pixel art para facilitar a substituição depois.

## Arquivos

- `main.py`: jogo principal.
- `settings.py`: constantes compartilhadas.
- `collision.py`: colisões e resolução de movimento.
- `level.py`: geração aleatória das fases.
- `render.py`: textura, HUD, cenário e telas.
- `assets/`: texturas PNG usadas no jogo.
- `gerar_assets.py`: script opcional para recriar as texturas placeholder.

## Próximos passos sugeridos no Codex

1. Melhorar as texturas e animações do protagonista.
2. Adicionar tela de vitória final ou ranking.
3. Adicionar sons apenas se o professor permitir novas bibliotecas.
4. Ajustar dificuldade, número de vidas e quantidade de inimigos conforme o tempo de apresentação.
