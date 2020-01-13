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
class_hero = 4
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
        rooms = [[False, (), 0, []] for x in range(kol)] + \
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
                rooms[nomer][1] = (
                    x + delta_x_y[rooms[i][-1][j]][0], y + delta_x_y[rooms[i][-1][j]][1])
                maket[y + delta_x_y[rooms[i][-1][j]][1]][x + delta_x_y[rooms[i][-1][j]][0]] = 1
                predki += [[i, nomer, rooms[i][-1][j]]]
            i += 1
        long = kol * 17 + (kol + 5) * 7
        self.karta = ["~" * long * 2 for i in range(long * 2)]
        x, y = long - 3, long - 3
        self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x + 7:]
        for i in range(1, 6):
            self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][x + 7:]
        self.karta[y + 6] = self.karta[y + 6][:x] + "#######" + self.karta[y + 6][x + 7:]
        self.karta[y + 3] = self.karta[y + 3][:x + 3] + "@" + self.karta[y + 3][x + 4:]
        self.make_map(rooms[0], 0, predki, rooms, x, y)
        i = 0
        while i < len(self.karta) - 11:
            if "." not in self.karta[i + 11] and "#" not in self.karta[i + 11] and "." not in \
                    self.karta[i] and "#" not in self.karta[i]:
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
                    if self.karta[y][x + 1] == "." and self.karta[y][x - 1] == "." or \
                            self.karta[y + 1][x] == "." and self.karta[y - 1][x] == ".":
                        self.karta[y] = self.karta[y][:x] + "^" + self.karta[y][x + 1:]
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
                        self.karta[y + i] = self.karta[y + i][:x] + "#...#" + self.karta[y + i][
                                                                              x + 5:]
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
                        self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][
                                                                                x + 7:]
                    self.karta[y + 4] = self.karta[y + 4][:x] + "#######" + self.karta[y + 4][
                                                                            x + 7:]
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
                        self.karta[y + i] = self.karta[y + i][:x] + "#...#" + self.karta[y + i][
                                                                              x + 5:]
                    self.karta[y + 6] = self.karta[y + 6][:x] + "#####" + self.karta[y + 6][x + 5:]
                else:
                    self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x + 7:]
                    for i in range(1, 4):
                        self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][
                                                                                x + 7:]
                    self.karta[y + 4] = self.karta[y + 4][:x] + "#######" + self.karta[y + 4][
                                                                            x + 7:]
                x += napravlenie2[room[-2]][0]
                y += napravlenie2[room[-2]][1]
            self.karta[y] = self.karta[y][:x] + "#################" + self.karta[y][x + 17:]
            for i in range(1, 16):
                self.karta[y + i] = self.karta[y + i][:x] + "#...............#" + self.karta[y + i][
                                                                                  x + 17:]
            self.karta[y + 16] = self.karta[y + 16][:x] + "#################" + self.karta[y + 16][
                                                                                x + 17:]
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
                    self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + self.karta[y + i][
                                                                            x + 7:]
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
    intro_text = ["ЗАСТАВКА",
                  "Правила игры",
                  "Есть в правилах несколько строк",
                  "Приходится выводить их построчно"]
    font = pygame.font.Font(None, 30)
    text_coord = 50
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("fon.jpg")
    image.image = pygame.transform.scale(image.image, (550, 550))
    image.rect = image.image.get_rect()
    sprite.add(image)
    sprite.draw(screen)
    for line in intro_text:
        string_render = font.render(line, 1, pygame.Color(0, 0, 0))
        intro_rect = string_render.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_render, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return
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
                if class_hero == 1:
                    new_player = KnightWithSpear(x, y)
                elif class_hero == 2:
                    new_player = Mage(x, y)
                elif class_hero == 3:
                    new_player = Dworf(x, y)
                elif class_hero == 4:
                    new_player = Rogue(x, y)
    return new_player, x, y


"""
class FirstOrk(pygame.sprite.Sprite):
    file_name = "images/characters/enemies/ORK1/"
    attack_right_images = [pygame.image.load(file_name + "_ATTACK_RIGHT/ATTACK_000.png"),
                           pygame.image.load(file_name + "_ATTACK_RIGHT/ATTACK_001.png"),
                           pygame.image.load(file_name + "_ATTACK_RIGHT/ATTACK_002.png"),
                           pygame.image.load(file_name + "_ATTACK_RIGHT/ATTACK_003.png"),
                           pygame.image.load(file_name + "_ATTACK_RIGHT/ATTACK_004.png"),
                           pygame.image.load(file_name + "_ATTACK_RIGHT/ATTACK_005.png"),
                           pygame.image.load(file_name + "_ATTACK_RIGHT/ATTACK_006.png")]
    attack_left_images = [pygame.image.load(file_name + "_ATTACK_LEFT/ATTACK_000.png"),
                          pygame.image.load(file_name + "_ATTACK_LEFT/ATTACK_001.png"),
                          pygame.image.load(file_name + "_ATTACK_LEFT/ATTACK_002.png"),
                          pygame.image.load(file_name + "_ATTACK_LEFT/ATTACK_003.png"),
                          pygame.image.load(file_name + "_ATTACK_LEFT/ATTACK_004.png"),
                          pygame.image.load(file_name + "_ATTACK_LEFT/ATTACK_005.png"),
                          pygame.image.load(file_name + "_ATTACK_LEFT/ATTACK_006.png")]
    die_images = [pygame.image.load(file_name + "_DIE/_DIE_000.png"),
                  pygame.image.load(file_name + "_DIE/_DIE_001.png"),
                  pygame.image.load(file_name + "_DIE/_DIE_002.png"),
                  pygame.image.load(file_name + "_DIE/_DIE_003.png"),
                  pygame.image.load(file_name + "_DIE/_DIE_004.png"),
                  pygame.image.load(file_name + "_DIE/_DIE_005.png"),
                  pygame.image.load(file_name + "_DIE/_DIE_006.png")]
    run_right_images = [pygame.image.load(file_name + "_RUN_RIGHT/_RUN_000.png"),
                        pygame.image.load(file_name + "_RUN_RIGHT/_RUN_001.png"),
                        pygame.image.load(file_name + "_RUN_RIGHT/_RUN_002.png"),
                        pygame.image.load(file_name + "_RUN_RIGHT/_RUN_003.png"),
                        pygame.image.load(file_name + "_RUN_RIGHT/_RUN_004.png"),
                        pygame.image.load(file_name + "_RUN_RIGHT/_RUN_005.png"),
                        pygame.image.load(file_name + "_RUN_RIGHT/_RUN_006.png")]
    run_left_images = [pygame.image.load(file_name + "_RUN_LEFT/_RUN_000.png"),
                       pygame.image.load(file_name + "_RUN_LEFT/_RUN_001.png"),
                       pygame.image.load(file_name + "_RUN_LEFT/_RUN_002.png"),
                       pygame.image.load(file_name + "_RUN_LEFT/_RUN_003.png"),
                       pygame.image.load(file_name + "_RUN_LEFT/_RUN_004.png"),
                       pygame.image.load(file_name + "_RUN_LEFT/_RUN_005.png"),
                       pygame.image.load(file_name + "_RUN_LEFT/_RUN_006.png")]

    def __init__(self, x, y):
        super().__init__()
        self.add(enemies)
        self.image = self.attack_right_images[0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(50 * x, 50 * y)
        self.hp = 100
        self.damage = 1
        self.armor = 100
        self.speed = 2
        self.alive = True
        self.left = False
        self.right = False
        self.pred_left = True
        self.pred_right = True
        self.figth = False
        self.stop = True
        self.idle_animation = 0
        self.run_animation = 0
        self.attack_animation = 0
        self.die_animation = 0
        self.pos_attack = self.rect
        self.width = len(level[0])
        self.height = len(level)

    def search_hero(self, x, y):
        # print(x, y, self.hero_x, self.hero_y)
        if self.color[x][y] == 0 and self.color[self.hero_x][self.hero_y] == 0:
            self.color[x][y] = 1
            # print(x, y)
            if y + 1 < self.width:
                if level[x][y + 1] != "#":
                    self.pred[x][y + 1] = (x, y)
                    self.search_hero(x, y + 1)
            if x + 1 < self.height:
                if level[x + 1][y] != "#":
                    self.pred[x + 1][y] = (x, y)
                    self.search_hero(x + 1, y)
            if y - 1 > -1:
                if level[x][y - 1] != "#":
                    self.pred[x][y - 1] = (x, y)
                    self.search_hero(x, y - 1)
            if x - 1 > -1:
                if level[x - 1][y] != "#":
                    self.pred[x - 1][y] = (x, y)
                    self.search_hero(x - 1, y)

    def update(self, hero_x, hero_y, *args):
        if self.hp <= 0 and self.die_animation <= 6:
            self.image = self.die_images[self.die_animation]
            self.die_animation += 1
        else:
            self.color = [[0 for i in range(self.width + 1)] for j in range(self.height + 1)]
            self.pred = [[(-1, -1) for i in range(self.width + 1)] for j in range(self.height + 1)]
            self.hero_x, self.hero_y = hero_x, hero_y
            print(self.rect)
            self.search_hero(self.rect[1] // 50, self.rect[0] // 50)
            if self.color[self.hero_x][self.hero_y] == 1:
                pass"""


class KnightWithSpear(pygame.sprite.Sprite):
    file_name = "images/characters/heroes/Knight_with_spear/"
    sl_images = {"attack_right": [], "attack_left": [], "idle_right": [], "idle_left": [],
                 "run_left": [], "run_right": [], "die": []}
    sl_seven_pict = {0: ["attack_right", "_ATTACK_RIGHT/ATTACK_00"],
                     1: ["attack_left", "_ATTACK_LEFT/ATTACK_00"]}
    sl_six_pict = {0: ["idle_right", "_IDLE_RIGHT/_IDLE_00"],
                   1: ["idle_left", "_IDLE_LEFT/_IDLE_00"],
                   2: ["run_right", "_RUN_RIGHT/_RUN_00"],
                   3: ["run_left", "_RUN_LEFT/_RUN_00"],
                   4: ["die", "_DIE/_DIE_00"]}
    for i in range(16):
        nom = sl_seven_pict[i // 8]
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 8) + ".png"))
    for i in range(35):
        nom = sl_six_pict[i // 7]
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 7) + ".png"))

    def __init__(self, x, y):
        super().__init__()
        self.add(player_group)
        self.image = self.sl_images["idle_right"][0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(50 * x, 50 * y)
        self.hp = 100
        self.damage = 25
        self.armor = 150
        self.speed = 3
        self.alive = True
        self.left = False
        self.right = False
        self.pred_left = True
        self.pred_right = True
        self.figth = False
        self.stop = True
        self.idle_animation = 0
        self.run_animation = 0
        self.attack_animation = 0
        self.die_animation = 0
        self.pos_attack = self.rect

    def update(self, x, y, *args):
        if self.hp <= 0:
            self.image = self.sl_images["die"][self.die_animation // 3]
            self.die_animation += 1
        else:
            if self.figth:
                self.stop = False
                self.run_animation = 0
                self.idle_animation = 0
                if self.pos_attack[0] < self.rect.x:
                    self.right = False
                    self.left = True
                    self.image = self.sl_images["attack_left"][self.attack_animation // 3]
                else:
                    self.right = True
                    self.left = False
                    self.image = self.sl_images["attack_right"][self.attack_animation // 3]
                self.attack_animation = self.attack_animation + 1
                if self.attack_animation == 24:
                    self.figth = False
                    self.attack_animation = 0
                    self.left = self.pred_left
                    self.right = self.pred_right
            else:
                self.rect = self.rect.move(x, 0)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(-x, 0)
                self.rect = self.rect.move(0, y)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(0, -y)
                if x != 0 or y != 0:
                    self.stop = False
                    self.pred_right = self.right
                    self.pred_left = self.left
                    self.idle_animation = 0
                    if self.left:
                        self.image = self.sl_images["run_left"][self.run_animation // 3]
                    else:
                        self.image = self.sl_images["run_right"][self.run_animation // 3]
                    self.run_animation = (self.run_animation + 1) % 21
                else:
                    self.stop = True
                if self.stop:
                    self.run_animation = 0
                    if self.pred_left:
                        self.image = self.sl_images["idle_left"][self.idle_animation // 3]
                    else:
                        self.image = self.sl_images["idle_right"][self.idle_animation // 3]
                    self.idle_animation = (self.idle_animation + 1) % 21
            for sprite in enemy_group:
                opa = pygame.sprite.Group()
                sprite.add(opa)
                if pygame.sprite.spritecollideany(self, opa):
                    if self.armor > 0:
                        self.armor -= sprite.damage
                    else:
                        self.hp -= sprite.damage + self.armor
                        self.armor = 0
                    if sprite.armor > 0:
                        sprite.armor -= sprite.damage
                    else:
                        sprite.hp -= sprite.damage + sprite.armor
                        sprite.armor = 0


class Mage(pygame.sprite.Sprite):
    file_name = "images/characters/heroes/Mage/"
    sl_images = {"attack_right": [], "attack_left": [], "idle_right": [], "idle_left": [],
                 "run_left": [], "run_right": [], "die": []}
    sl_six_pict = {0: ["idle_right", "_IDLE_RIGHT/_IDLE_00"],
                   1: ["idle_left", "_IDLE_LEFT/_IDLE_00"],
                   2: ["run_right", "_RUN_RIGHT/_RUN_00"],
                   3: ["run_left", "_RUN_LEFT/_RUN_00"],
                   4: ["die", "_DIE/_DIE_00"],
                   5: ["attack_right", "_ATTACK_RIGHT/ATTACK_00"],
                   6: ["attack_left", "_ATTACK_LEFT/ATTACK_00"]}
    for i in range(49):
        nom = sl_six_pict[i // 7]
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 7) + ".png"))

    def __init__(self, x, y):
        super().__init__()
        self.add(player_group)
        self.image = self.sl_images["idle_right"][0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(50 * x, 50 * y)
        self.hp = 100
        self.damage = 25
        self.armor = 150
        self.speed = 3
        self.alive = True
        self.left = False
        self.right = False
        self.pred_left = True
        self.pred_right = True
        self.figth = False
        self.stop = True
        self.idle_animation = 0
        self.run_animation = 0
        self.attack_animation = 0
        self.die_animation = 0
        self.pos_attack = self.rect

    def update(self, x, y, *args):
        if self.hp <= 0:
            self.image = self.sl_images["die"][self.die_animation // 4]
            self.die_animation += 1
        else:
            if self.figth:
                self.stop = False
                self.run_animation = 0
                self.idle_animation = 0
                if self.pos_attack[0] < self.rect.x:
                    self.right = False
                    self.left = True
                    self.image = self.sl_images["attack_left"][self.attack_animation // 4]
                else:
                    self.right = True
                    self.left = False
                    self.image = self.sl_images["attack_right"][self.attack_animation // 4]
                self.attack_animation = self.attack_animation + 1
                if self.attack_animation == 24:
                    self.figth = False
                    self.attack_animation = 0
                    self.left = self.pred_left
                    self.right = self.pred_right
            else:
                self.rect = self.rect.move(x, 0)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(-x, 0)
                self.rect = self.rect.move(0, y)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(0, -y)
                if x != 0 or y != 0:
                    self.stop = False
                    self.pred_right = self.right
                    self.pred_left = self.left
                    self.idle_animation = 0
                    if self.left:
                        self.image = self.sl_images["run_left"][self.run_animation // 4]
                    else:
                        self.image = self.sl_images["run_right"][self.run_animation // 4]
                    self.run_animation = (self.run_animation + 1) % 24
                else:
                    self.stop = True
                if self.stop:
                    self.run_animation = 0
                    if self.pred_left:
                        self.image = self.sl_images["idle_left"][self.idle_animation // 4]
                    else:
                        self.image = self.sl_images["idle_right"][self.idle_animation // 4]
                    self.idle_animation = (self.idle_animation + 1) % 24
            for sprite in enemy_group:
                opa = pygame.sprite.Group()
                sprite.add(opa)
                if pygame.sprite.spritecollideany(self, opa):
                    if self.armor > 0:
                        self.armor -= sprite.damage
                    else:
                        self.hp -= sprite.damage + self.armor
                        self.armor = 0
                    if sprite.armor > 0:
                        sprite.armor -= sprite.damage
                    else:
                        sprite.hp -= sprite.damage + sprite.armor
                        sprite.armor = 0


class Dworf(pygame.sprite.Sprite):
    file_name = "images/characters/heroes/Dworf/"
    sl_images = {"attack_right": [], "attack_left": [], "idle_right": [], "idle_left": [],
                 "run_left": [], "run_right": [], "die": []}
    sl_seven_pict = {0: ["attack_right", "_ATTACK_RIGHT/ATTACK_00"],
                     1: ["attack_left", "_ATTACK_LEFT/ATTACK_00"],
                     2: ["run_right", "_RUN_RIGHT/_RUN_00"],
                     3: ["run_left", "_RUN_LEFT/_RUN_00"]}
    for i in range(32):
        nom = sl_seven_pict[i // 8]
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 8) + ".png"))
    nom = ["die", "_DIE/_DIE_00"]
    for i in range(5):
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i) + ".png"))
    sl_seven_pict = {0: ["idle_right", "_IDLE_RIGHT/_IDLE_0"],
                     1: ["idle_left", "_IDLE_LEFT/_IDLE_0"]}
    for i in range(24):
        nom = sl_seven_pict[i // 12]
        st = str(i % 12).rjust(2, "0")
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + st + ".png"))

    def __init__(self, x, y):
        super().__init__()
        self.add(player_group)
        self.image = self.sl_images["idle_right"][0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(50 * x, 50 * y)
        self.hp = 100
        self.damage = 25
        self.armor = 150
        self.speed = 3
        self.alive = True
        self.left = False
        self.right = False
        self.pred_left = True
        self.pred_right = True
        self.figth = False
        self.stop = True
        self.idle_animation = 0
        self.run_animation = 0
        self.attack_animation = 0
        self.die_animation = 0
        self.pos_attack = self.rect

    def update(self, x, y, *args):
        if self.hp <= 0:
            self.image = self.sl_images["die"][self.die_animation // 3]
            self.die_animation += 1
        else:
            if self.figth:
                self.stop = False
                self.run_animation = 0
                self.idle_animation = 0
                if self.pos_attack[0] < self.rect.x:
                    self.right = False
                    self.left = True
                    self.image = self.sl_images["attack_left"][self.attack_animation // 3]
                else:
                    self.right = True
                    self.left = False
                    self.image = self.sl_images["attack_right"][self.attack_animation // 3]
                self.attack_animation = self.attack_animation + 1
                if self.attack_animation == 24:
                    self.figth = False
                    self.attack_animation = 0
                    self.left = self.pred_left
                    self.right = self.pred_right
            else:
                self.rect = self.rect.move(x, 0)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(-x, 0)
                self.rect = self.rect.move(0, y)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(0, -y)
                if x != 0 or y != 0:
                    self.stop = False
                    self.pred_right = self.right
                    self.pred_left = self.left
                    self.idle_animation = 0
                    if self.left:
                        self.image = self.sl_images["run_left"][self.run_animation // 3]
                    else:
                        self.image = self.sl_images["run_right"][self.run_animation // 3]
                    self.run_animation = (self.run_animation + 1) % 21
                else:
                    self.stop = True
                if self.stop:
                    self.run_animation = 0
                    if self.pred_left:
                        self.image = self.sl_images["idle_left"][self.idle_animation // 3]
                    else:
                        self.image = self.sl_images["idle_right"][self.idle_animation // 3]
                    self.idle_animation = (self.idle_animation + 1) % 21
            for sprite in enemy_group:
                opa = pygame.sprite.Group()
                sprite.add(opa)
                if pygame.sprite.spritecollideany(self, opa):
                    if self.armor > 0:
                        self.armor -= sprite.damage
                    else:
                        self.hp -= sprite.damage + self.armor
                        self.armor = 0
                    if sprite.armor > 0:
                        sprite.armor -= sprite.damage
                    else:
                        sprite.hp -= sprite.damage + sprite.armor
                        sprite.armor = 0


class Rogue(pygame.sprite.Sprite):
    file_name = "images/characters/heroes/Rogue/"
    sl_images = {"attack_right": [], "attack_left": [], "idle_right": [], "idle_left": [],
                 "run_left": [], "run_right": [], "die": []}
    sl_seven_pict = {0: ["run_right", "_RUN_RIGHT/_RUN_00"],
                     1: ["run_left", "_RUN_LEFT/_RUN_00"]}
    for i in range(16):
        nom = sl_seven_pict[i // 8]
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 8) + ".png"))
    sl_six_pict = {0: ["attack_right", "_ATTACK_RIGHT/ATTACK_00"],
                   1: ["attack_left", "_ATTACK_LEFT/ATTACK_00"]}
    for i in range(14):
        nom = sl_six_pict[i // 7]
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 7) + ".png"))
    nom = ["die", "_DIE/_DIE_00"]
    for i in range(5):
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i) + ".png"))
    sl_sixteen_pict = {0: ["idle_right", "_IDLE_RIGHT/_IDLE_0"],
                     1: ["idle_left", "_IDLE_LEFT/_IDLE_0"]}
    for i in range(34):
        nom = sl_sixteen_pict[i // 17]
        st = str(i % 17).rjust(2, "0")
        sl_images[nom[0]].append(pygame.image.load(file_name + nom[1] + st + ".png"))

    def __init__(self, x, y):
        super().__init__()
        self.add(player_group)
        self.image = self.sl_images["idle_right"][0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(50 * x, 50 * y)
        self.hp = 100
        self.damage = 25
        self.armor = 150
        self.speed = 10
        self.alive = True
        self.left = False
        self.right = False
        self.pred_left = True
        self.pred_right = True
        self.figth = False
        self.stop = True
        self.idle_animation = 0
        self.run_animation = 0
        self.attack_animation = 0
        self.die_animation = 0
        self.pos_attack = self.rect

    def update(self, x, y, *args):
        if self.hp <= 0:
            self.image = self.sl_images["die"][self.die_animation // 3]
            self.die_animation += 1
        else:
            if self.figth:
                self.stop = False
                self.run_animation = 0
                self.idle_animation = 0
                if self.pos_attack[0] < self.rect.x:
                    self.right = False
                    self.left = True
                    self.image = self.sl_images["attack_left"][self.attack_animation // 3]
                else:
                    self.right = True
                    self.left = False
                    self.image = self.sl_images["attack_right"][self.attack_animation // 3]
                self.attack_animation = self.attack_animation + 1
                if self.attack_animation == 21:
                    self.figth = False
                    self.attack_animation = 0
                    self.left = self.pred_left
                    self.right = self.pred_right
            else:
                self.rect = self.rect.move(x, 0)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(-x, 0)
                self.rect = self.rect.move(0, y)
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(0, -y)
                if x != 0 or y != 0:
                    self.stop = False
                    self.pred_right = self.right
                    self.pred_left = self.left
                    self.idle_animation = 0
                    if self.left:
                        self.image = self.sl_images["run_left"][self.run_animation // 3]
                    else:
                        self.image = self.sl_images["run_right"][self.run_animation // 3]
                    self.run_animation = (self.run_animation + 1) % 21
                else:
                    self.stop = True
                if self.stop:
                    self.run_animation = 0
                    if self.pred_left:
                        self.image = self.sl_images["idle_left"][self.idle_animation // 3]
                    else:
                        self.image = self.sl_images["idle_right"][self.idle_animation // 3]
                    self.idle_animation = (self.idle_animation + 1) % 21
            for sprite in enemy_group:
                opa = pygame.sprite.Group()
                sprite.add(opa)
                if pygame.sprite.spritecollideany(self, opa):
                    if self.armor > 0:
                        self.armor -= sprite.damage
                    else:
                        self.hp -= sprite.damage + self.armor
                        self.armor = 0
                    if sprite.armor > 0:
                        sprite.armor -= sprite.damage
                    else:
                        sprite.hp -= sprite.damage + sprite.armor
                        sprite.armor = 0


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
enemy_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
level = load_level("lobbi.txt")
player, level_x, level_y = generate_level(level)
camera = Camera()
del_x = 0
del_y = 0
player.stop = True
clock = pygame.time.Clock()
fps = 30
running = True
xod = {pygame.K_DOWN: (0, player.speed), pygame.K_UP: (0, -player.speed),
       pygame.K_LEFT: (-player.speed, 0), pygame.K_RIGHT: (player.speed, 0),
       pygame.K_s: (0, player.speed), pygame.K_w: (0, -player.speed),
       pygame.K_a: (-player.speed, 0), pygame.K_d: (player.speed, 0)}
camera.update(player)
for sprite in all_sprites:
    camera.apply(sprite)
camera.apply(player)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            key = event.key
            if key in xod.keys() and player.die_animation < 7:
                move = xod[event.key]
                del_x -= move[0]
                del_y -= move[1]
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key in xod.keys() and player.die_animation < 7:
                move = xod[event.key]
                del_x += move[0]
                del_y += move[1]
            elif key == pygame.K_f:
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
                    level = carta.make_room()
                    player, level_x, level_y = generate_level(level)
                    camera.update(player)
                    for sprite in all_sprites:
                        camera.apply(sprite)
                    camera.apply(player)
                elif pygame.sprite.spritecollideany(player, box_group):
                    pass
        if event.type == pygame.MOUSEBUTTONDOWN and player.die_animation < 7:
            if event.button == 1:
                player.left = False
                player.right = False
                player.figth = True
                player.pos_attack = event.pos
    if player.die_animation < 7:
        if del_y != 0:
            player.left = player.pred_left
            player.right = player.pred_right
        if del_x == player.speed:
            player.left = False
            player.right = True
        elif del_x == -player.speed:
            player.left = True
            player.right = False
        else:
            player.left = False
            player.right = False
        player_group.update(del_x, del_y)
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        camera.apply(player)
    screen.fill((255, 255, 255))
    all_sprites.draw(screen)
    player_group.draw(screen)
    enemy_group.draw(screen)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
