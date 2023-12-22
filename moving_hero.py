import os
import sys
import pygame

pygame.init()
pygame.key.set_repeat(200, 70)
FPS = 50
WIDTH = 500
HEIGHT = 500
STEP = 10
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Перемещение героя')
clock = pygame.time.Clock()
player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = [
        'Перемещение героя',
        "",
        "",
        "",
        "",
    ]
    background = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 60
    for line in intro_text:
        string_rendered = font.render(line, True, 'black')
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        screen.blit(string_rendered, intro_rect)
        text_coord += intro_rect.height + 10

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                string_rendered = font.render('Введите имя файла уровня в терминале', True, 'black')
                intro_rect = string_rendered.get_rect()
                intro_rect.top = text_coord
                intro_rect.x = 10
                screen.blit(string_rendered, intro_rect)
                pygame.display.flip()
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()


def load_level(filename):
    filename = os.path.join('data', filename)
    with open(filename, 'r') as fd:
        level_map = [line.strip() for line in fd]
    max_width = max(map(len, level_map))
    level_map = [i.ljust(max_width, '.') for i in level_map]
    return level_map


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')
tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x - 15, tile_height * pos_y - 5)

        def update(self, *args, **kwargs) -> None:
            pass


class Player(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        for i in pygame.sprite.spritecollide(self, tiles_group, False):
            tile_type = getattr(i, 'tile_type', None)
            if tile_type == 'wall':
                self.rect.x -= dx
                self.rect.y -= dy
                return


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            if level[y][x] == '#':
                Tile('wall', x, y)
            if level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def get_level_from_user():
    filepath = f"data/{input('Введите имя файла уровня: ')}"
    if not os.path.exists(filepath):
        print(f'Файл "{filepath}" не существует')
        sys.exit(1)
    filepath = os.path.join('..', filepath)
    level = load_level(filepath)
    return level


player, level_x, level_y = generate_level(get_level_from_user())


class Camera:

    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, sprite: pygame.sprite.Sprite):
        sprite.rect.x += self.dx
        sprite.rect.y += self.dy

    def update(self, target: pygame.sprite.Sprite):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def flip_tiles(dx, dy):
    if abs(dx) != tile_width and abs(dy) != tile_height:
        return
    top_right_rect = max((i for i in tiles_group if isinstance(i, Tile)),
                         key=lambda t: (t.rect.x, -t.rect.y)).rect.copy()
    bottom_left_rect = min((i for i in tiles_group if isinstance(i, Tile)),
                           key=lambda t: (t.rect.x, -t.rect.y)).rect.copy()
    for tile in tiles_group:
        if dx > 0:
            if tile.rect.right != top_right_rect.right:
                continue
            tile.rect.x = bottom_left_rect.x - top_right_rect.width
        elif dx < 0:
            if tile.rect.left != bottom_left_rect.left:
                continue
            tile.rect.x = top_right_rect.x + bottom_left_rect.width
    for tile in tiles_group:
        if dy > 0:
            if tile.rect.bottom != bottom_left_rect.bottom:
                continue
            tile.rect.y = top_right_rect.y - tile.rect.w
        elif dy < 0:
            if tile.rect.top != top_right_rect.top:
                continue
            tile.rect.y = bottom_left_rect.y + tile.rect.width


camera = Camera()

running = True
while running:
    WIDTH, HEIGHT = pygame.display.get_window_size()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.move(-tile_width, 0)
            if event.key == pygame.K_RIGHT:
                player.move(tile_width, 0)
            if event.key == pygame.K_UP:
                player.move(0, -tile_height)
            if event.key == pygame.K_DOWN:
                player.move(0, tile_height)
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    flip_tiles(camera.dx, camera.dy)
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
