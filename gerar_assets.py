from PIL import Image, ImageDraw

TILE = 32


def salvar(nome, img):
    img.save('assets/' + nome)


def quad(draw, x, y, w, h, cor):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=cor)


def player():
    img = Image.new('RGBA', (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    quad(d, 10, 3, 12, 8, (70, 42, 20, 255))
    quad(d, 7, 8, 18, 16, (245, 196, 135, 255))
    quad(d, 7, 6, 5, 18, (80, 45, 20, 255))
    quad(d, 20, 6, 5, 18, (80, 45, 20, 255))
    quad(d, 11, 14, 3, 3, (30, 30, 30, 255))
    quad(d, 19, 14, 3, 3, (30, 30, 30, 255))
    quad(d, 15, 20, 5, 2, (120, 40, 30, 255))
    quad(d, 8, 25, 17, 14, (130, 30, 30, 255))
    quad(d, 5, 27, 6, 12, (245, 196, 135, 255))
    quad(d, 22, 27, 6, 12, (245, 196, 135, 255))
    quad(d, 10, 39, 5, 8, (25, 50, 120, 255))
    quad(d, 18, 39, 5, 8, (25, 50, 120, 255))
    quad(d, 6, 45, 9, 3, (40, 20, 10, 255))
    quad(d, 18, 45, 9, 3, (40, 20, 10, 255))
    salvar('nicolas_cage.png', img)


def bee():
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 9, 25, 24], fill=(235, 190, 30, 255), outline=(30, 20, 10, 255))
    quad(d, 11, 9, 3, 16, (30, 20, 10, 255))
    quad(d, 18, 9, 3, 16, (30, 20, 10, 255))
    d.ellipse([3, 3, 14, 13], fill=(190, 230, 255, 170), outline=(120, 170, 200, 180))
    d.ellipse([17, 3, 28, 13], fill=(190, 230, 255, 170), outline=(120, 170, 200, 180))
    quad(d, 23, 15, 4, 3, (30, 20, 10, 255))
    quad(d, 7, 13, 3, 3, (0, 0, 0, 255))
    salvar('bee_enemy.png', img)


def sahur():
    img = Image.new('RGBA', (44, 66), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Corpo de madeira clara
    d.rounded_rectangle([10, 10, 33, 47], radius=8, fill=(171, 109, 55, 255), outline=(92, 54, 28, 255))
    quad(d, 12, 12, 20, 4, (214, 167, 94, 255))
    quad(d, 16, 20, 3, 3, (255, 255, 255, 255))
    quad(d, 24, 20, 3, 3, (255, 255, 255, 255))
    quad(d, 17, 21, 2, 2, (20, 20, 20, 255))
    quad(d, 25, 21, 2, 2, (20, 20, 20, 255))
    quad(d, 20, 31, 4, 1, (100, 56, 38, 255))

    # Braços
    quad(d, 7, 27, 3, 14, (198, 132, 72, 255))
    quad(d, 34, 27, 3, 14, (198, 132, 72, 255))
    quad(d, 6, 40, 5, 3, (183, 116, 61, 255))
    quad(d, 33, 40, 5, 3, (183, 116, 61, 255))

    # Pernas e pés
    quad(d, 15, 47, 5, 15, (145, 84, 44, 255))
    quad(d, 24, 47, 5, 15, (145, 84, 44, 255))
    quad(d, 12, 61, 9, 4, (214, 167, 94, 255))
    quad(d, 23, 61, 9, 4, (214, 167, 94, 255))

    # Porrete em diagonal
    d.polygon([(4, 12), (8, 14), (19, 44), (15, 46)], fill=(196, 133, 67, 255), outline=(92, 54, 28, 255))
    d.ellipse([0, 8, 8, 16], fill=(178, 113, 56, 255), outline=(92, 54, 28, 255))

    salvar('tung_sahur_enemy.png', img)


def ground():
    img = Image.new('RGBA', (32, 32), (145, 86, 38, 255))
    d = ImageDraw.Draw(img)
    quad(d, 0, 0, 32, 8, (80, 170, 55, 255))
    for x in range(0, 32, 8):
        d.line([x, 8, x, 31], fill=(80, 45, 25, 255), width=2)
    for y in range(14, 32, 8):
        d.line([0, y, 31, y], fill=(100, 55, 25, 255), width=2)
    salvar('ground.png', img)


def block():
    img = Image.new('RGBA', (32, 32), (166, 88, 38, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 31], outline=(50, 25, 10, 255), width=2)
    d.line([0, 10, 31, 10], fill=(70, 35, 15, 255), width=2)
    d.line([0, 21, 31, 21], fill=(70, 35, 15, 255), width=2)
    d.line([10, 0, 10, 10], fill=(70, 35, 15, 255), width=2)
    d.line([22, 10, 22, 21], fill=(70, 35, 15, 255), width=2)
    d.line([10, 21, 10, 31], fill=(70, 35, 15, 255), width=2)
    salvar('block.png', img)


def chest():
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    quad(d, 5, 11, 22, 16, (150, 80, 25, 255))
    d.rectangle([5, 11, 26, 26], outline=(45, 25, 10, 255), width=2)
    quad(d, 5, 11, 22, 6, (200, 130, 40, 255))
    quad(d, 15, 15, 4, 6, (245, 220, 60, 255))
    salvar('chest_goal.png', img)


def coin():
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 2, 19, 21], fill=(245, 200, 35, 255), outline=(150, 100, 20, 255))
    quad(d, 10, 5, 3, 14, (255, 230, 80, 255))
    salvar('coin.png', img)


def sky():
    img = Image.new('RGBA', (64, 64), (104, 176, 245, 255))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 10, 29, 23], fill=(255, 255, 255, 220))
    d.ellipse([20, 8, 43, 23], fill=(255, 255, 255, 220))
    d.ellipse([34, 13, 56, 25], fill=(255, 255, 255, 220))
    salvar('sky.png', img)


def gerar_todos_assets():
    player()
    bee()
    sahur()
    ground()
    block()
    chest()
    coin()
    sky()


if __name__ == "__main__":
    gerar_todos_assets()
