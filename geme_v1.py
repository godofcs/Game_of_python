import pygame
import os
import sys
import random


pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
screen.fill((255, 255, 255))


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_images = {"wall": load_image("wall_2.png"), "empty": load_image("ground.png"),
               "door": load_image("door.png"), "box": load_image("box.png"),
               "fon": load_image("fon.png"), "gate": load_image("gate.png")}
player_image = pygame.transform.scale(load_image("goose_3.png", colorkey=-1), (50, 50))
#door_image = load_image("door.png")
tile_width = tile_height = 50


def load_level(filename):
    filename = "data/" + filename
    with open(filename, "r") as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, "."), level_map))


class Map():
    def __init__(self, flor):
        self.flor = flor
        self.kol_room = [2, 2, 2, 2, 3]
        if self.flor >= 2:
            self.kol_room[3] = 3
        if self.flor == 3:
            self.kol_room[2] = 4

    def make_room(self):
        number = random.randint(0, len(self.kol_room) - 1)
        kol = self.kol_room[number]
        self.kol_room = self.kol_room[:number] + self.kol_room[number + 1:]
        rooms = [[False, (), 0, []] for x in range(kol)] +\
                [[False, (), 0, 0], [False, (), 0, 0]]
        predki = []
        i = 0
        maket = [[0 for j in range((kol + 2) * 2 + 1)] for i in range((kol + 2) * 2 + 1)]
        x, y = kol + 2, kol + 2
        maket[y][x] = 1
        rooms[0][-2] = random.randint(1, 4)
        delta_x_y = {1: (0, -1), 2: (1, 0), 3: (0, 1), 4: (-1, 0)}
        x -= delta_x_y[rooms[0][-2]][0]
        y -= delta_x_y[rooms[0][-2]][1]
        maket[y][x] = 1
        rooms[0][1] = (x, y)
        while i < kol:
            x, y = rooms[i][1]
            if rooms[i][0] or i == kol - 1 and rooms[-1][0] and rooms[-2][0]:
                i += 1
                break
            quits = (2 if i == kol - 1 and not rooms[-1][0] and not rooms[-2][0]
                     else random.randint(1, min(kol - i - 1 + (1 if not rooms[-1][0] else 0) +
                                                (1 if not rooms[-2][0] else 0), 2)))
            rooms[i][0] = True
            vxod = rooms[i][-2]
            vyxody = set()
            while len(vyxody) < quits:
                vyxod = random.randint(1, 4)
                if maket[y + delta_x_y[vyxod][1]][x + delta_x_y[vyxod][0]] == 1:
                    continue
                vyxody.add(vyxod)
                vyxody -= {vxod}
            rooms[i][-1] = list(vyxody)
            quits = min(2, quits)
            for j in range(quits):
                ost_rooms = []
                for k in range(i + 1, kol + 1):
                    if rooms[k][-2] == 0:
                        ost_rooms += [rooms[k]]
                        break
                ost_rooms += [rooms[-2]] if not rooms[-2][0] else []
                ost_rooms += [rooms[-1]] if not rooms[-1][0] else []
                if rooms[i + 1][-2] == 0 and (quits == 1 or j == quits - 1):
                    ost_rooms = [ost_rooms[0]]
                sled_room = random.choice(ost_rooms)
                nomer = rooms.index(sled_room)
                if nomer == kol + 2 - 1 or nomer == kol + 2 - 2:
                    rooms[nomer][0] = True
                rooms[nomer][-2] = (rooms[i][-1][j] + 1) % 4 + 1
                rooms[nomer][1] = (x + delta_x_y[rooms[i][-1][j]][0], y + delta_x_y[rooms[i][-1][j]][1])
                maket[y + delta_x_y[rooms[i][-1][j]][1]][x + delta_x_y[rooms[i][-1][j]][0]] = 1
                predki += [[i, nomer, rooms[i][-1][j]]]
            i += 1
        long = kol * 17 + (kol + 5) * 7
        self.karta = ["~" * long * 2 for i in range(long * 2)]
        x, y = long - 3, long - 3
        self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x+7:]
        for i in range(1, 6):
            self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][x + 7:]
        self.karta[y + 6] = self.karta[y + 6][:x] + "#######" + self.karta[y + 6][x + 7:]
        self.karta[y + 3] = self.karta[y + 3][:x + 3] + "@" + self.karta[y + 3][x + 4:]
        self.make_map(rooms[0], 0, predki, rooms, x, y)
        i = 0
        while i < len(self.karta) - 11:
            if "." not in self.karta[i + 11] and "#" not in self.karta[i + 11] and "." not in self.karta[i] and "#" not in self.karta[i]:
                del self.karta[i]
                i -= 1
            i += 1
        i = 0
        while i < len(self.karta[0]) - 11:
            rows = ""
            rows2 = ""
            for row in self.karta:
                rows = rows + row[i]
                rows2 = rows2 + row[i + 11]
            if "." not in rows2 and "#" not in rows2 and "." not in rows and "#" not in rows:
                for j in range(len(self.karta)):
                    self.karta[j] = self.karta[j][:i] + self.karta[j][i + 1:]
                i -= 1
            i += 1
        for y in range(len(self.karta)):
            for x in range(len(self.karta[y])):
                if self.karta[y][x] == "#":
                    if self.karta[y][x + 1] == "." and self.karta[y][x - 1] == "." or self.karta[y + 1][x] == "." and self.karta[y - 1][x] == ".":
                        self.karta[y] = self.karta[y][:x] + "^" + self.karta[y][x + 1:]
        for i in self.karta:
            print(i)
        return self.karta

    def make_map(self, room, nomer, predki, rooms, x, y):
        napravlenie = {1: (6, 16), 2: (-6, 6), 3: (6, -6), 4: (16, 6)}
        napravlenie2 = {1: (-6, 6), 2: (-16, -6), 3: (-6, -16), 4: (6, -6)}
        if nomer != len(rooms) - 1 and nomer != len(rooms) - 2:
            if nomer == 0:
                if room[-2] == 1 or room[-2] == 3:
                    if room[-2] == 1:
                        x += 1
                        y += 6
                    else:
                        x += 1
                        y -= 6
                    self.karta[y] = self.karta[y][:x] + "#####" + self.karta[y][x + 5:]
                    for i in range(1, 6):
                        self.karta[y + i] = self.karta[y + i][:x] + "#...#" + self.karta[y + i][x + 5:]
                    self.karta[y + 6] = self.karta[y + 6][:x] + "#####" + self.karta[y + 6][x + 5:]
                    if room[-2] == 1:
                        x -= 6
                        y += 6
                    else:
                        x -= 6
                        y -= 16
                else:
                    if room[-2] == 2:
                        x -= 6
                        y += 1
                    else:
                        x += 6
                        y += 1
                    self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x + 7:]
                    for i in range(1, 4):
                        self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][x + 7:]
                    self.karta[y + 4] = self.karta[y + 4][:x] + "#######" + self.karta[y + 4][x + 7:]
                    if room[-2] == 2:
                        x -= 16
                        y -= 6
                    else:
                        x += 6
                        y -= 6
            else:
                x += napravlenie[room[-2]][0]
                y += napravlenie[room[-2]][1]
                if room[-2] == 1 or room[-2] == 3:
                    self.karta[y] = self.karta[y][:x] + "#####" + self.karta[y][x + 5:]
                    for i in range(1, 6):
                        self.karta[y + i] = self.karta[y + i][:x] + "#...#" + self.karta[y + i][x + 5:]
                    self.karta[y + 6] = self.karta[y + 6][:x] + "#####" + self.karta[y + 6][x + 5:]
                else:
                    self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x + 7:]
                    for i in range(1, 4):
                        self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][x + 7:]
                    self.karta[y + 4] = self.karta[y + 4][:x] + "#######" + self.karta[y + 4][x + 7:]
                x += napravlenie2[room[-2]][0]
                y += napravlenie2[room[-2]][1]
            self.karta[y] = self.karta[y][:x] + "#################" + self.karta[y][x + 17:]
            kol_enemies = random.randint(5, 8)
            for i in range(1, 16):
                self.karta[y + i] = self.karta[y + i][:x] + "#...............#" + self.karta[y + i][x + 17:]
                if kol_enemies:
                    enemie = random.choice([True, False])
                    if enemie:
                        enemies_pos = random.randint(2, 14)
                        self.karta[y + i] = self.karta[y + i][:x + enemies_pos] + "E" + self.karta[y + i][x + enemies_pos + 1:]
                        kol_enemies -= 1
            self.karta[y + 16] = self.karta[y + 16][:x] + "#################" + self.karta[y + 16][x + 17:]
            for i in range(len(room[-1])):
                for j in predki:
                    if nomer == j[0]:
                        for k in range(len(rooms)):
                            if k == j[1]:
                                self.make_map(rooms[k], k, predki, rooms, x, y)
                        del predki[predki.index(j)]
        else:
            x += napravlenie[room[-2]][0]
            y += napravlenie[room[-2]][1]
            if room[-2] == 1 or room[-2] == 3:
                self.karta[y] = self.karta[y][:x] + "#####" + self.karta[y][x + 5:]
                for i in range(1, 6):
                    self.karta[y + i] = self.karta[y + i][:x] + "#...#" + self.karta[y + i][x + 5:]
                self.karta[y + 6] = self.karta[y + 6][:x] + "#####" + self.karta[y + 6][x + 5:]
                if room[-2] == 1:
                    x -= 1
                    y += 6
                else:
                    x -= 1
                    y -= 6
            else:
                self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x + 7:]
                for i in range(1, 4):
                    self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][x + 7:]
                self.karta[y + 4] = self.karta[y + 4][:x] + "#######" + self.karta[y + 4][x + 7:]
                if room[-2] == 2:
                    x -= 6
                    y -= 1
                else:
                    x += 6
                    y -= 1
            self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x + 7:]
            for i in range(1, 6):
                self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][x + 7:]
            self.karta[y + 6] = self.karta[y + 6][:x] + "#######" + self.karta[y + 6][x + 7:]
            if nomer == len(rooms) - 1:
                self.karta[y + 3] = self.karta[y + 3][:x + 3] + "!" + self.karta[y + 3][x + 4:]
            else:
                self.karta[y + 3] = self.karta[y + 3][:x + 3] + "$" + self.karta[y + 3][x + 4:]


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = {"AUNTENTIFICATION": [(287, 78), (415, 40)], "LOGIN": [(266, 255), (462, 80)],
                  "PASSWORD": [(266, 459), (462, 80)], "LOG IN": [(412, 664), (165, 40)],
                  "REGISTRATE": [(346, 795), (300, 40)]}
    font = pygame.font.SysFont("SMW Text 2 NC", 40)
    text_coord = 0
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("authentication.png")
    image.image = pygame.transform.scale(image.image, (1000, 1000))
    image.rect = image.image.get_rect()
    sprite.add(image)
    sprite.draw(screen)
    for line in intro_text.keys():
        #text_rect_image = load_image("text_fon_4.png", -1)
        text_rect_image = pygame.transform.scale(load_image("text_fon_4.png", -1), (500, 82))
        pygame.draw.rect(text_rect_image, pygame.Color(255, 0, 0), (0, 0, intro_text[line][1][0], intro_text[line][1][1]), 2)
        text_fon = pygame.sprite.Sprite()
        text_fon.image = text_rect_image
        text_fon.rect = text_fon.image.get_rect()
        text_fon.rect.x = intro_text[line][0][0]
        text_fon.rect.y = intro_text[line][0][1]
        intro_text[line] += [text_fon]
    sprite.draw(screen)
    action_sprite = pygame.sprite.Group()
    enter_login = False
    login = ""
    enter_password = False
    password = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                flag = 0
                for value in intro_text.values():
                    if value[0][0] <= x <= value[0][0] + value[1][0] and value[0][1] <= y <= value[0][1] + value[1][1]:
                        flag = 1
                        action_sprite.add(value[2])
                        break
                if flag == 0:
                    action_sprite = pygame.sprite.Group()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return
        sprite.draw(screen)
        action_sprite.draw(screen)
        pygame.display.flip()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == "wall":
            super().__init__(tile_group, all_sprites)
        elif tile_type == "door":
            super().__init__(door_group, all_sprites)
        elif tile_type == "box":
            super().__init__(box_group, all_sprites)
        else:
            super().__init__(all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def go(self, vx, vy):
        self.rect.x = (self.rect.x + vx) % width
        self.rect.y = (self.rect.y + vy) % height


class Enemie(pygame.sprite.Sprite):
    pass


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == ".":
                Tile("empty", x, y)
            elif level[y][x] == "~":
                Tile("fon", x, y)
            elif level[y][x] == "^":
                Tile("gate", x, y)
            elif level[y][x] == "!":
                Tile("door", x, y)
            elif level[y][x] == "$":
                Tile("box", x, y)
            elif level[y][x] == "#":
                Tile("wall", x, y)
            elif level[y][x] == "@":
                Tile("empty", x, y)
                new_player = Player(x, y)
            elif level[y][x] == "E":
                Tile("empty", x, y)
                Enemie(x, y)
    return new_player, x, y


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = width // 2 - (target.rect.x + target.rect.w // 2)
        self.dy = height // 2 - (target.rect.y + target.rect.h // 2)


start_screen()
number_level = 0
number_room = 0
player = None
all_sprites = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player, level_x, level_y = generate_level(load_level("lobbi.txt"))
camera = Camera()
del_x = 0
del_y = 0
running = True
xod = {pygame.K_DOWN: (0, 1), pygame.K_UP: (0, -1), pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)}
camera.update(player)
for sprite in all_sprites:
    camera.apply(sprite)
camera.apply(player)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            f = event.key
            if f in xod.keys():
                k = xod[event.key]
                del_x -= k[0]
                del_y -= k[1]
        if event.type == pygame.KEYDOWN:
            f = event.key
            if f in xod.keys():
                k = xod[event.key]
                del_x += k[0]
                del_y += k[1]
            elif f == pygame.K_f:
                if pygame.sprite.spritecollideany(player, door_group):
                    all_sprites = pygame.sprite.Group()
                    tile_group = pygame.sprite.Group()
                    door_group = pygame.sprite.Group()
                    box_group = pygame.sprite.Group()
                    player_group = pygame.sprite.Group()
                    if number_room == 0:
                        number_level += 1
                        carta = Map(number_level)
                    number_roon = (number_room + 1) % 5
                    player, level_x, level_y = generate_level(carta.make_room())
                    camera.update(player)
                    for sprite in all_sprites:
                        camera.apply(sprite)
                    camera.apply(player)
                elif pygame.sprite.spritecollideany(player, box_group):
                    pass
    if del_x != 0 or del_y != 0:
        player.go(del_x, 0)
        if pygame.sprite.spritecollideany(player, tile_group):
            player.go(-del_x, 0)
        player.go(0, del_y)
        if pygame.sprite.spritecollideany(player, tile_group):
            player.go(0, -del_y)
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        camera.apply(player)
    screen.fill((255, 255, 255))
    all_sprites.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
pygame.quit()
#97 120 42; 275, ; 275, 390