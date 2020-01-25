import pygame
import os
import sys
import random
import sqlite3

pygame.init()
class_hero = ""
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
screen.fill((255, 255, 255))
con = sqlite3.connect("player.db")
cur = con.cursor()
con.commit()
con.close()

# создание уровня и случайная генерация поля
class Map():
    # создание объекта класса Map
    def __init__(self, flor):
        self.flor = flor
        self.kol_room = [2, 2, 2, 2, 3]
        if self.flor >= 2:
            self.kol_room[3] = 3
        if self.flor == 3:
            self.kol_room[2] = 4

    # случайная генерация комнаты
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
                st = delta_x_y[rooms[i][-1][j]][1]
                rooms[nomer][1] = (x + delta_x_y[rooms[i][-1][j]][0], y + st)
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
            if "." not in self.karta[i + 11] and "#" not in self.karta[i + 11] and \
                    "." not in self.karta[i] and "#" not in self.karta[i]:
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

    # отрисовка комнаты
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
                        st = self.karta[y + i][x + 5:]
                        self.karta[y + i] = self.karta[y + i][:x] + "#...#" + st
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
                        st = self.karta[y + i][x + 7:]
                        self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + st
                    st = self.karta[y + 4][x + 7:]
                    self.karta[y + 4] = self.karta[y + 4][:x] + "#######" + st
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
                        st = self.karta[y + i][x + 5:]
                        self.karta[y + i] = self.karta[y + i][:x] + "#...#" + st
                    self.karta[y + 6] = self.karta[y + 6][:x] + "#####" + self.karta[y + 6][x + 5:]
                else:
                    self.karta[y] = self.karta[y][:x] + "#######" + self.karta[y][x + 7:]
                    for i in range(1, 4):
                        st = self.karta[y + i][x + 7:]
                        self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + st
                    st = self.karta[y + 4][x + 7:]
                    self.karta[y + 4] = self.karta[y + 4][:x] + "#######" + st
                x += napravlenie2[room[-2]][0]
                y += napravlenie2[room[-2]][1]
            self.karta[y] = self.karta[y][:x] + "#################" + self.karta[y][x + 17:]
            List = []
            spisok = [(i, j) for j in range(3, 13) for i in range(3, 13)]
            while len(List) != 5:
                pos = random.choice(spisok)
                if pos not in List:
                    List.append(pos)
            for i in range(1, 16):
                st = self.karta[y + i][:x] + "#"
                for j in range(1, 16):
                    if (i, j) in List:
                        st += "O"
                    else:
                        st += "."
                self.karta[y + i] = st + "#" + self.karta[y + i][x + 17:]
            st = self.karta[y + 16][x + 17:]
            self.karta[y + 16] = self.karta[y + 16][:x] + "#################" + st
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
                    st = self.karta[y + i][x + 7:]
                    self.karta[y + i] = self.karta[y + i][:x] + "#.....#" + st
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

# создание врагов и моделирование их поведения
class Enemy(pygame.sprite.Sprite):
    file_1 = "Images/characters/enemies/ORK_1/"
    file_2 = "Images/characters/enemies/ORK_2/"
    file_3 = "Images/characters/enemies/ORK_3/"
    sl_images_first = {"attack_right": [], "attack_left": [], "run_left": [], "run_right": [],
                       "die": []}
    sl_images_second = {"attack_right": [], "attack_left": [], "run_left": [], "run_right": [],
                        "die": []}
    sl_images_third = {"attack_right": [], "attack_left": [], "run_left": [], "run_right": [],
                       "die": []}
    sl_six_pict = {0: ["attack_right", "_ATTACK_RIGHT/ATTACK_00"],
                   1: ["attack_left", "_ATTACK_LEFT/ATTACK_00"], 4: ["die", "_DIE/_DIE_00"],
                   2: ["run_right", "_RUN_RIGHT/_RUN_00"], 3: ["run_left", "_RUN_LEFT/_RUN_00"]}
    for i in range(35):
        nom = sl_six_pict[i // 7]
        sl_images_first[nom[0]].append(pygame.image.load(file_1 + nom[1] + str(i % 7) + ".png"))
        sl_images_second[nom[0]].append(pygame.image.load(file_2 + nom[1] + str(i % 7) + ".png"))
        sl_images_third[nom[0]].append(pygame.image.load(file_3 + nom[1] + str(i % 7) + ".png"))

    # создание объекта класса Enemy
    def __init__(self, x, y):
        nom = random.choice(range(1, 4))
        if nom == 1:
            self.sl_images = self.sl_images_first
        elif nom == 2:
            self.sl_images = self.sl_images_second
        else:
            self.sl_images = self.sl_images_third
        super().__init__(all_sprites)
        self.add(enemy_group)
        self.image = self.sl_images["attack_right"][0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(50 * y, 50 * x)
        self.hp = 60 + uroven * 10
        self.x = x * 50
        self.y = y * 50
        self.damage = 20 + uroven * 3
        self.armor = 50 + uroven * 5
        self.speed = 2
        self.pos_y = 0
        self.left = False
        self.right = False
        self.figth = False
        self.run_animation = 0
        self.attack_animation = 0
        self.die_animation = 0

    # поиск героя и моделирование дальнейших действий
    def search_hero(self, x, y):
        if self.color[x][y] == 0:
            self.color[x][y] = 1
            if y + 1 < self.width:
                if level[x][y + 1] != "#" and level[x][y + 1] != "^":
                    self.search_hero(x, y + 1)
            if x + 1 < self.height:
                if level[x + 1][y] != "#" and level[x + 1][y] != "^":
                    self.search_hero(x + 1, y)
            if y - 1 > -1:
                if level[x][y - 1] != "#" and level[x][y - 1] != "^":
                    self.search_hero(x, y - 1)
            if x - 1 > -1:
                if level[x - 1][y] != "#" and level[x - 1][y] != "^":
                    self.search_hero(x - 1, y)

    # обработка действий врага
    def update(self, *args):
        if self.hp <= 0:
            if self.die_animation < len(self.sl_images["die"]) * 4:
                self.image = self.sl_images["die"][self.die_animation // 4]
                self.die_animation += 1
        else:
            self.width = len(level[0])
            self.height = len(level)
            self.color = [[0 for i in range(self.width + 1)] for j in range(self.height + 1)]
            self.hero_x, self.hero_y = player.x // 50, player.y // 50
            self.search_hero(self.x // 50, self.y // 50)
            if self.color[self.hero_x][self.hero_y] == 1:
                del_x = 0
                del_y = 0
                if self.x < player.x:
                    del_x = self.speed
                elif self.x > player.x:
                    del_x = -self.speed
                if self.y < player.y:
                    del_y = self.speed
                elif self.y > player.y:
                    del_y = -self.speed
                if del_y + self.y > self.y:
                    self.right = True
                    self.left = False
                else:
                    self.left = True
                    self.right = False
                self.rect = self.rect.move(del_y, del_x)
                self.x += del_x
                self.y += del_y
                if pygame.sprite.spritecollideany(self, player_group):
                    self.figth = True
                    self.pos_y = player.y
                    self.run_animation = 0
                if self.figth:
                    if self.y < self.pos_y:
                        self.right = True
                        self.left = False
                        self.image = self.sl_images["attack_right"][self.attack_animation // 4]
                    else:
                        self.right = True
                        self.left = False
                        self.image = self.sl_images["attack_left"][self.attack_animation // 4]
                    self.attack_animation += 1
                    if self.attack_animation == len(self.sl_images["attack_left"]):
                        pygame.mixer.music.load(load_sound("tuch.mp3"))
                        pygame.mixer.music.play()
                    if self.attack_animation == len(self.sl_images["attack_left"]) * 4:
                        if pygame.sprite.spritecollideany(self, player_group):
                            if player.armor - self.damage >= 0:
                                player.armor -= self.damage
                            else:
                                player.hp -= self.damage + player.armor
                                player.armor = 0
                        self.attack_animation = 0
                        self.figth = False
                else:
                    if self.right:
                        self.image = self.sl_images["run_right"][self.run_animation // 5]
                    else:
                        self.image = self.sl_images["run_left"][self.run_animation // 5]
                    self.run_animation += 1
                    self.run_animation %= (len(self.sl_images["run_left"]) * 5)
            else:
                self.run_animation = 0
                self.attack_animation = 0
                self.image = self.sl_images["attack_right"][0]


# создание игрока
class Player(pygame.sprite.Sprite):
    file_name = "Images/characters/heroes/Knight_with_spear/"
    sl_images_khight = {"attack_right": [], "attack_left": [], "idle_right": [], "idle_left": [],
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
        sl_images_khight[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 8) + ".png"))
    for i in range(35):
        nom = sl_six_pict[i // 7]
        sl_images_khight[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 7) + ".png"))
    file_name = "Images/characters/heroes/Dworf/"
    sl_images_dworf = {"attack_right": [], "attack_left": [], "idle_right": [], "idle_left": [],
                       "run_left": [], "run_right": [], "die": []}
    sl_seven_pict = {0: ["attack_right", "_ATTACK_RIGHT/ATTACK_00"],
                     1: ["attack_left", "_ATTACK_LEFT/ATTACK_00"],
                     2: ["run_right", "_RUN_RIGHT/_RUN_00"],
                     3: ["run_left", "_RUN_LEFT/_RUN_00"]}
    for i in range(32):
        nom = sl_seven_pict[i // 8]
        sl_images_dworf[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 8) + ".png"))
    nom = ["die", "_DIE/_DIE_00"]
    for i in range(5):
        sl_images_dworf[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i) + ".png"))
    sl_seven_pict = {0: ["idle_right", "_IDLE_RIGHT/_IDLE_0"],
                     1: ["idle_left", "_IDLE_LEFT/_IDLE_0"]}
    for i in range(24):
        nom = sl_seven_pict[i // 12]
        st = str(i % 12).rjust(2, "0")
        sl_images_dworf[nom[0]].append(pygame.image.load(file_name + nom[1] + st + ".png"))
    file_name = "Images/characters/heroes/Rogue/"
    sl_images_rogue = {"attack_right": [], "attack_left": [], "idle_right": [], "idle_left": [],
                       "run_left": [], "run_right": [], "die": []}
    sl_seven_pict = {0: ["run_right", "_RUN_RIGHT/_RUN_00"],
                     1: ["run_left", "_RUN_LEFT/_RUN_00"]}
    for i in range(16):
        nom = sl_seven_pict[i // 8]
        sl_images_rogue[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 8) + ".png"))
    sl_six_pict = {0: ["attack_right", "_ATTACK_RIGHT/ATTACK_00"],
                   1: ["attack_left", "_ATTACK_LEFT/ATTACK_00"]}
    for i in range(14):
        nom = sl_six_pict[i // 7]
        sl_images_rogue[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i % 7) + ".png"))
    nom = ["die", "_DIE/_DIE_00"]
    for i in range(5):
        sl_images_rogue[nom[0]].append(pygame.image.load(file_name + nom[1] + str(i) + ".png"))
    sl_sixteen_pict = {0: ["idle_right", "_IDLE_RIGHT/_IDLE_0"],
                       1: ["idle_left", "_IDLE_LEFT/_IDLE_0"]}
    for i in range(34):
        nom = sl_sixteen_pict[i // 17]
        st = str(i % 17).rjust(2, "0")
        sl_images_rogue[nom[0]].append(pygame.image.load(file_name + nom[1] + st + ".png"))

    # создание объекта класса Player
    def __init__(self, type, x, y, hp=-1, damage=-1, armor=-1):
        super().__init__()
        self.add(player_group)
        if type == "knight":
            self.speed = 10
            self.sl_images = self.sl_images_khight
            self.attack_sound = "knight_attak.mp3"
            if hp != None and hp > -1:
                self.max_hp, self.hp = hp, hp
                self.max_damage, self.damage = damage, damage
                self.max_armor, self.armor = armor, armor
            else:
                self.max_hp, self.hp = 400, 400
                self.max_damage, self.damage = 20, 20
                self.max_armor, self.armor = 300, 300
        elif type == "rogue":
            self.sl_images = self.sl_images_rogue
            self.speed = 20
            self.attack_sound = "rogue_attak.mp3"
            if hp != None and hp > -1:
                self.max_hp, self.hp = hp, hp
                self.max_damage, self.damage = damage, damage
                self.max_armor, self.armor = armor, armor
            else:
                self.max_hp, self.hp = 150, 150
                self.max_damage, self.damage = 23, 23
                self.max_armor, self.armor = 150, 150
        elif type == "dworf":
            self.sl_images = self.sl_images_dworf
            self.attack_sound = "dworf_attak.mp3"
            self.speed = 15
            if hp != None and hp > -1:
                self.max_hp, self.hp = hp, hp
                self.max_damage, self.damage = damage, damage
                self.max_armor, self.armor = armor, armor
            else:
                self.max_hp, self.hp = 250, 250
                self.max_damage, self.damage = 23, 23
                self.max_armor, self.armor = 150, 150
        self.image = self.sl_images["idle_right"][0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(50 * y, 50 * x)
        self.x = x * 50
        self.y = y * 50
        self.alive = True
        self.left = False
        self.right = False
        self.pred_left = True
        self.pred_right = True
        self.figth = False
        self.stop = True
        self.bumb = 0
        self.idle_animation = 0
        self.run_animation = 0
        self.attack_animation = 0
        self.die_animation = 0
        self.pos_attack = self.rect

    # обратка действий игрока
    def update(self, x, y, *args):
        if self.hp <= 0:
            self.image = self.sl_images["die"][self.die_animation // 5]
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
                self.pred_right = self.right
                self.pred_left = self.left
                self.attack_animation = self.attack_animation + 1
                if self.attack_animation == len(self.sl_images["attack_left"]):
                    pygame.mixer.music.load(load_sound(self.attack_sound))
                    pygame.mixer.music.play()
                if self.attack_animation == len(self.sl_images["attack_left"]) * 4:
                    self.figth = False
                    self.attack_animation = 0
                    self.left = self.pred_left
                    self.right = self.pred_right
            else:
                self.rect = self.rect.move(x, 0)
                self.y += x
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(-x, 0)
                    self.y -= x
                self.rect = self.rect.move(0, y)
                self.x += y
                if pygame.sprite.spritecollideany(self, tile_group):
                    self.rect = self.rect.move(0, -y)
                    self.x -= y
                if x != 0 or y != 0:
                    self.stop = False
                    self.pred_right = self.right
                    self.pred_left = self.left
                    self.idle_animation = 0
                    if (self.run_animation + 1) % 3 == 0:
                        pygame.mixer.music.load(load_sound("step.mp3"))
                        pygame.mixer.music.play()
                    if self.left:
                        self.image = self.sl_images["run_left"][self.run_animation // 5]
                    else:
                        self.image = self.sl_images["run_right"][self.run_animation // 5]
                    self.run_animation += 1
                    self.run_animation %= (len(self.sl_images["run_left"]) * 5)
                else:
                    self.stop = True
                if self.stop:
                    self.run_animation = 0
                    if self.pred_left:
                        self.image = self.sl_images["idle_left"][self.idle_animation // 5]
                    else:
                        self.image = self.sl_images["idle_right"][self.idle_animation // 5]
                    self.idle_animation += 1
                    self.idle_animation %= (len(self.sl_images["idle_left"]) * 5)
            for sprite in enemy_group:
                group = pygame.sprite.Group()
                sprite.add(group)
                if pygame.sprite.spritecollideany(self, group) and sprite.hp > 0:
                    if self.attack_animation == len(self.sl_images["attack_left"]) - 1:
                        if sprite.armor - self.damage >= 0:
                            sprite.armor -= self.damage
                        else:
                            sprite.hp -= self.damage + sprite.armor
                            sprite.armor = 0
                        if sprite.hp <= 0:
                            self.hp = min(self.hp + 20, self.max_hp)
                            self.armor = min(self.armor + 10, self.max_armor)
                    else:
                        if self.figth == False:
                            if self.bumb == 500:
                                if self.armor - 2 >= 0:
                                    self.armor -= 2
                                else:
                                    self.hp -= 2 + sprite.armor
                                    self.armor = 0
                                self.bumb = 0
                            self.bumb += 1


# создание объектов окружения
class Tile(pygame.sprite.Sprite):
    # создание объекта класса Tile
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == "wall":
            super().__init__(tile_group, all_sprites)
        elif tile_type == "door":
            super().__init__(door_group, all_sprites)
        elif tile_type == "box":
            self.znach = -1
            super().__init__(box_group, all_sprites)
        elif tile_type == "gate":
            super().__init__(hall_group, all_sprites)
        elif tile_type == "hp" or tile_type == "armor":
            super().__init__(info_group)
        else:
            super().__init__(all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_y, tile_height * pos_x)


# создание камеры, следящей за героем
class Camera:
    # создание объекта класса Camera
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # задание велечины смещения камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # смещение объекта
    def update(self, target):
        self.dx = width // 2 - (target.rect.x + target.rect.w // 2)
        self.dy = height // 2 - (target.rect.y + target.rect.h // 2)


# загрузка изображений
def load_image(name, colorkey=None):
    fullname = os.path.join("Images\\", name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# загрузка звука
def load_sound(name):
    return os.path.join("Music", name)


# загрузка уровня
def load_level(filename):
    filename = "txt_files\\" + filename
    with open(filename, "r") as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, "."), level_map))


# завершение работы
def terminate():
    pygame.quit()
    sys.exit()


# обращение к базе данных для получения типа персонажа и номера уровня
def get_result(player_login, player_password, zapros=0):
    con = sqlite3.connect("player.db")
    cur = con.cursor()
    try:
        hero, level, hp, damage, armor = cur.execute("""SELECT hero, level, hp, damage, 
                                                        armor FROM info_player  
                                                        WHERE login == ? AND password == ?""",
                                                     (player_login, player_password)).fetchone()
        con.close()
        return hero, level, hp, damage, armor
    except:
        if zapros == 1:
            try:
                hero, level, hp, damage, armor = cur.execute("""SELECT hero, level, hp, damage, 
                                                                armor FROM info_player 
                                                                WHERE login == ?""",
                                                             (player_login,)).fetchone()
                con.close()
                return hero, level, hp, damage, armor
            except:
                con.close()
                return False, False, -1, -1, -1
        con.close()
        return False, False, -1, -1, -1


# отрисовка текста
def render_text(txt, x, y, razmer=40, color=(0, 0, 1)):
    font = pygame.font.SysFont("SMW Text 2 NC", razmer)
    text_image = load_image("background\\text_fon_1.png", -1)
    text = font.render(txt, 1, color)
    text_image.blit(text, (0, 0))
    txt_sprite = pygame.sprite.Sprite()
    txt_sprite.image = text_image
    txt_sprite.rect = txt_sprite.image.get_rect()
    txt_sprite.rect.x = x
    txt_sprite.rect.y = y
    return txt_sprite


# создание выделительных прямоугольников вокруг кнопок
def update_intro_text(intro_text):
    for line in intro_text.keys():
        text_rect_image = pygame.transform.scale(load_image("background\\text_fon_4.png", -1),
                                                 (500, 250))
        pygame.draw.rect(text_rect_image, pygame.Color(255, 0, 0),
                         (0, 0, intro_text[line][1][0], intro_text[line][1][1]), 2)
        text_fon = pygame.sprite.Sprite()
        text_fon.image = text_rect_image
        text_fon.rect = text_fon.image.get_rect()
        text_fon.rect.x = intro_text[line][0][0]
        text_fon.rect.y = intro_text[line][0][1]
        intro_text[line] += [text_fon]
    return intro_text


# работа с окном входа
def start_screen():
    global player_login
    intro_text = {"LOGIN": [(266, 255), (462, 80)], "PASSWORD": [(266, 459), (462, 80)],
                  "LOG IN": [(412, 664), (165, 40)], "REGISTRATE": [(346, 795), (300, 40)]}
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\authentication.png")
    image.image = pygame.transform.scale(image.image, (1000, 1000))
    image.rect = image.image.get_rect()
    sprite.add(image)
    intro_text = update_intro_text(intro_text)
    sprite.draw(screen)
    action_sprite = pygame.sprite.Group()
    enter_login = [False, False, False]
    login = ""
    enter_password = [False, False, False]
    password = ""
    normal_password = ""
    push_log_in = [False, False]
    push_registrate = [False, False]
    text_sprite = pygame.sprite.Group()
    muzik = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                flag = 0
                enter_login[0] = False
                enter_password[0] = False
                push_log_in = False
                push_registrate = False
                for value in intro_text.values():
                    if (value[0][0] <= x <= value[0][0] + value[1][0] and
                            value[0][1] <= y <= value[0][1] + value[1][1]):
                        flag = 1
                        if value[0] == intro_text["LOGIN"][0]:
                            enter_login[0] = True
                        elif value[0] == intro_text["PASSWORD"][0]:
                            enter_password[0] = True
                        elif value[0] == intro_text["LOG IN"][0]:
                            push_log_in = True
                        elif value[0] == intro_text["REGISTRATE"][0]:
                            push_registrate = True
                        if muzik == 0:
                            pygame.mixer.music.load(load_sound("click.mp3"))
                            pygame.mixer.music.play()
                            muzik = 1
                        action_sprite.add(value[2])
                        break
                if flag == 0:
                    muzik = 0
                    pygame.mixer.music.stop()
                    action_sprite = pygame.sprite.Group()
                if enter_login[1]:
                    action_sprite.add(intro_text["LOGIN"][2])
                if enter_password[1]:
                    action_sprite.add(intro_text["PASSWORD"][2])
            if event.type == pygame.MOUSEBUTTONDOWN:
                if push_registrate:
                    registrate_windows()
                if push_log_in:
                    hero, level, hp, damage, armor = get_result(login, normal_password)
                    if hero and level:
                        player_login = login
                        return hero, level, hp, damage, armor
                    else:
                        text_sprite.add(render_text("Неправильный логин или пароль",
                                                    intro_text["LOGIN"][0][0] + 10,
                                                    intro_text["LOGIN"][0][1] + 120,
                                                    razmer=20))
                if enter_login[1] and not enter_login[0]:
                    action_sprite.remove(intro_text["LOGIN"][2])
                    enter_login[1] = False
                elif enter_password[1] and not enter_password[0]:
                    action_sprite.remove(intro_text["PASSWORD"][2])
                    enter_password[1] = False
                if enter_login[0]:
                    enter_login[1] = not enter_login[1]
                    enter_password[1] = False
                elif enter_password[0]:
                    enter_password[1] = not enter_password[1]
                    enter_login[1] = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if enter_login[1]:
                        action_sprite.remove(intro_text["LOGIN"][2])
                        enter_login[1] = False
                    if enter_password[1]:
                        action_sprite.remove(intro_text["PASSWORD"][2])
                        enter_password[1] = False
                if enter_login[1]:
                    if event.key == pygame.K_BACKSPACE:
                        login = login[:-1]
                    elif event.unicode.isalnum() and len(login) < 11:
                        login += event.unicode
                elif enter_password[1]:
                    if event.key == pygame.K_BACKSPACE:
                        normal_password = normal_password[:-1]
                        password = password[:-1]
                    elif event.unicode.isalnum() and len(password) < 11:
                        normal_password += event.unicode
                        password += "*"
                text_sprite = pygame.sprite.Group()
                text_sprite.add(render_text(login, intro_text["LOGIN"][0][0] + 10,
                                            intro_text["LOGIN"][0][1] + 20))
                text_sprite.add(render_text(password, intro_text["PASSWORD"][0][0] + 10,
                                            intro_text["PASSWORD"][0][1] + 20))
        screen.fill((0, 0, 0))
        sprite.draw(screen)
        action_sprite.draw(screen)
        text_sprite.draw(screen)
        pygame.display.flip()


# работа с окном регистрации
def registrate_windows():
    intro_text = {"LOGIN": [(66, 294), (470, 88)], "PASSWORD": [(66, 514), (470, 88)],
                  "CONFIRM PASSWORD": [(66, 751), (470, 88)], "OK": [(449, 903), (100, 50)]}
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\registrate.png")
    image.rect = image.image.get_rect()
    sprite.add(image)
    intro_text = update_intro_text(intro_text)
    sprite.draw(screen)
    action_sprite = pygame.sprite.Group()
    enter_login = [False, False]
    login = ""
    enter_password = [False, False]
    password = ""
    normal_password = ""
    enter_password2 = [False, False]
    password2 = ""
    normal_password2 = ""
    push_ok = False
    muzik = 0
    text_sprite = pygame.sprite.Group()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                flag = 0
                enter_login[0] = False
                enter_password[0] = False
                enter_password2[0] = False
                push_ok = False
                for value in intro_text.values():
                    if (value[0][0] <= x <= value[0][0] + value[1][0] and
                            value[0][1] <= y <= value[0][1] + value[1][1]):
                        flag = 1
                        if value[0] == intro_text["LOGIN"][0]:
                            enter_login[0] = True
                        elif value[0] == intro_text["PASSWORD"][0]:
                            enter_password[0] = True
                        elif value[0] == intro_text["CONFIRM PASSWORD"][0]:
                            enter_password2[0] = True
                        elif value[0] == intro_text["OK"][0]:
                            push_ok = True
                        if muzik == 0:
                            pygame.mixer.music.load(load_sound("click.mp3"))
                            pygame.mixer.music.play()
                            muzik = 1
                        action_sprite.add(value[2])
                        break
                if flag == 0:
                    pygame.mixer.music.stop()
                    muzik = 0
                    action_sprite = pygame.sprite.Group()
                if enter_login[1]:
                    action_sprite.add(intro_text["LOGIN"][2])
                if enter_password[1]:
                    action_sprite.add(intro_text["PASSWORD"][2])
                if enter_password2[1]:
                    action_sprite.add(intro_text["CONFIRM PASSWORD"][2])
            if event.type == pygame.MOUSEBUTTONDOWN:
                if push_ok:
                    if normal_password2 != normal_password or len(normal_password) < 4:
                        text_sprite.add(render_text("Неправильный пароль",
                                                    intro_text["CONFIRM PASSWORD"][0][0] + 10,
                                                    intro_text["CONFIRM PASSWORD"][0][1] + 120,
                                                    razmer=20))
                        text_sprite.remove(render_text(password2,
                                                       intro_text["CONFIRM PASSWORD"][0][0] + 10,
                                                       intro_text["CONFIRM PASSWORD"][0][1] + 20))
                        enter_password2 = [False, False]
                        password2, normal_password2 = "", ""
                    else:
                        hero, level, hp, damage, armor = get_result(login, normal_password, 1)
                        if hero and level:
                            text_sprite = pygame.sprite.Group()
                            text_sprite.add(render_text("Такой логин уже есть",
                                                        intro_text["LOGIN"][0][0] + 500,
                                                        intro_text["LOGIN"][0][1] + 20,
                                                        razmer=20))
                            enter_login, enter_password, enter_password2 = [False, False], \
                                                                           [False, False], \
                                                                           [False, False]
                            login, password2, password, normal_password2, normal_password = "", \
                                                                                            "", \
                                                                                            "", \
                                                                                            "", ""
                        else:
                            con = sqlite3.connect("player.db")
                            cur = con.cursor()
                            cur.execute("""INSERT INTO info_player(login, password, hero, level, 
                                           hp, armor, damage) VALUES(?, ?, ?, ?, ?, ?, ?)""",
                                        (login, normal_password, "NO", -1, -1, -1, -1))
                            con.commit()
                            con.close()
                            return
                if enter_login[1] and not enter_login[0]:
                    action_sprite.remove(intro_text["LOGIN"][2])
                    enter_login[1] = False
                elif enter_password[1] and not enter_password[0]:
                    action_sprite.remove(intro_text["PASSWORD"][2])
                    enter_password[1] = False
                elif enter_password2[1] and not enter_password2[0]:
                    action_sprite.remove(intro_text["CONFIRM PASSWORD"][2])
                    enter_password2[1] = False
                if enter_login[0]:
                    enter_login[1] = not enter_login[1]
                    enter_password[1] = False
                    enter_password2[1] = False
                elif enter_password[0]:
                    enter_password[1] = not enter_password[1]
                    enter_login[1] = False
                    enter_password2[1] = False
                elif enter_password2[0]:
                    enter_password2[1] = not enter_password2[1]
                    enter_password[1] = False
                    enter_login[1] = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if enter_login[1]:
                        action_sprite.remove(intro_text["LOGIN"][2])
                        enter_login[1] = False
                    elif enter_password[1]:
                        action_sprite.remove(intro_text["PASSWORD"][2])
                        enter_password[1] = False
                    elif enter_password2[1]:
                        action_sprite.remove(intro_text["CONFIRM PASSWORD"][2])
                        enter_password2[1] = False
                if enter_login[1]:
                    if event.key == pygame.K_BACKSPACE:
                        login = login[:-1]
                    elif event.unicode.isalnum() and len(login) < 11:
                        login += event.unicode
                elif enter_password[1]:
                    if event.key == pygame.K_BACKSPACE:
                        normal_password = normal_password[:-1]
                        password = password[:-1]
                    elif event.unicode.isalnum() and len(password) < 11:
                        normal_password += event.unicode
                        password += "*"
                elif enter_password2[1]:
                    if event.key == pygame.K_BACKSPACE:
                        normal_password2 = normal_password2[:-1]
                        password2 = password2[:-1]
                    elif event.unicode.isalnum() and len(password2) < 11:
                        normal_password2 += event.unicode
                        password2 += "*"
                text_sprite = pygame.sprite.Group()
                text_sprite.add(render_text(login, intro_text["LOGIN"][0][0] + 10,
                                            intro_text["LOGIN"][0][1] + 20))
                text_sprite.add(render_text(password, intro_text["PASSWORD"][0][0] + 10,
                                            intro_text["PASSWORD"][0][1] + 20))
                text_sprite.add(render_text(password2,
                                            intro_text["CONFIRM PASSWORD"][0][0] + 10,
                                            intro_text["CONFIRM PASSWORD"][0][1] + 20))
        screen.fill((0, 0, 0))
        sprite.draw(screen)
        action_sprite.draw(screen)
        text_sprite.draw(screen)
        pygame.display.flip()


# работа с окном выбора персонажа
def choise():
    global class_hero
    pygame.mixer.music.stop()
    intro_text = {"KNIGHT": [(60, 555), (290, 240)], "DWORF": [(400, 337), (208, 200)],
                  "ROGUE": [(700, 497), (195, 200)]}
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\choise.png")
    image.rect = image.image.get_rect()
    sprite.add(image)
    intro_text = update_intro_text(intro_text)
    sprite.draw(screen)
    action_sprite = pygame.sprite.Group()
    push_ok = False
    muzik = 0
    text_sprite = pygame.sprite.Group()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                action_sprite = pygame.sprite.Group()
                f = 0
                push_ok = False
                for value in intro_text.values():
                    if (value[0][0] <= x <= value[0][0] + value[1][0] and
                            value[0][1] <= y <= value[0][1] + value[1][1]):
                        f = 1
                        if value[0] == intro_text["KNIGHT"][0]:
                            class_hero = "knight"
                            if muzik == 0:
                                pygame.mixer.music.load(load_sound("knight.mp3"))
                        elif value[0] == intro_text["DWORF"][0]:
                            class_hero = "dworf"
                            if muzik == 0:
                                pygame.mixer.music.load(load_sound("dworf.mp3"))
                        elif value[0] == intro_text["ROGUE"][0]:
                            class_hero = "rogue"
                            if muzik == 0:
                                pygame.mixer.music.load(load_sound("rogue.mp3"))
                        if muzik == 0:
                            muzik = 1
                            pygame.mixer.music.play()
                        push_ok = True
                        action_sprite.add(value[2])
                        break
                if f == 0:
                    muzik = 0
                    pygame.mixer.music.stop()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if push_ok:
                    pygame.mixer.music.stop()
                    return
        screen.fill((0, 0, 0))
        sprite.draw(screen)
        action_sprite.draw(screen)
        text_sprite.draw(screen)
        pygame.display.flip()


# работа с окном меню
def main():
    global all_sprites, tile_group, door_group, box_group, player_group, player_image
    global class_hero, hall_group, enemy_group, level, player, info_group
    hero, uroven, hp, damage, armor = get_result(player_login, 0, zapros=1)
    enemy_group = pygame.sprite.Group()
    hall_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    tile_group = pygame.sprite.Group()
    door_group = pygame.sprite.Group()
    box_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    info_group = pygame.sprite.Group()
    uroven = max(0, uroven)
    number_level = uroven // 5
    number_room = uroven % 5
    player = None
    if hero == "NO":
        choise()
        hero = class_hero
    else:
        class_hero = hero
    player = generate_level(load_level("lobbi.txt"), hp, damage, armor)
    camera = Camera()
    hp_sprite = render_text(str(max(0, player.hp)), 100, 50, color=(255, 0, 0))
    armor_sprite = render_text(str(player.armor), 100, 100, color=(128, 128, 128))
    level_sprite = render_text("0-0", 50, 150)
    Tile("hp", 1, 1)
    Tile("armor", 2, 1)
    info_group.add(hp_sprite, armor_sprite, level_sprite)
    del_x = 0
    del_y = 0
    player.stop = True
    clock = pygame.time.Clock()
    fps = 100
    running = True
    background = load_image("background\\fon.png")
    xod = {pygame.K_DOWN: (0, player.speed), pygame.K_UP: (0, -player.speed),
           pygame.K_LEFT: (-player.speed, 0), pygame.K_RIGHT: (player.speed, 0),
           pygame.K_s: (0, player.speed), pygame.K_w: (0, -player.speed),
           pygame.K_a: (-player.speed, 0), pygame.K_d: (player.speed, 0)}
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    camera.apply(player)
    if number_level != 0:
        carta = Map(number_level)
    number_room = max(-1, number_room - 1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                key = event.key
                if key in xod.keys() and player.die_animation < len(player.sl_images["die"]) * 5:
                    move = xod[event.key]
                    del_x -= move[0]
                    del_y -= move[1]
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key in xod.keys() and player.die_animation < len(player.sl_images["die"]) * 5:
                    move = xod[event.key]
                    del_x += move[0]
                    del_y += move[1]
                elif key == pygame.K_f:
                    if pygame.sprite.spritecollideany(player, door_group):
                        ans = True
                        for sprite in enemy_group:
                            if sprite.hp > 0:
                                ans = False
                                break
                        if ans:
                            all_sprites = pygame.sprite.Group()
                            enemy_group = pygame.sprite.Group()
                            tile_group = pygame.sprite.Group()
                            door_group = pygame.sprite.Group()
                            box_group = pygame.sprite.Group()
                            player_group = pygame.sprite.Group()
                            number_room = (number_room + 1) % 6
                            if number_room == 0:
                                number_level += 1
                                number_room += 1
                                if number_level == 4:
                                    win()
                                    return
                                carta = Map(number_level)
                            level = carta.make_room()
                            player = generate_level(level, player.max_hp, player.max_damage,
                                                    player.max_armor)
                            info_group.remove(level_sprite)
                            st = str(number_level) + "-" + str(number_room)
                            level_sprite = render_text(st, 50, 150)
                            info_group.add(level_sprite)
                            camera.update(player)
                            for sprite in all_sprites:
                                camera.apply(sprite)
                            camera.apply(player)
                    elif pygame.sprite.spritecollideany(player, box_group):
                        for sprite in box_group:
                            if sprite.znach == -1:
                                pygame.mixer.music.load(load_sound("chestopen.mp3"))
                                pygame.mixer.music.play()
                                nom = random.choice(range(0, 45))
                                st = "Images\\food\\"
                                sprite.image = pygame.image.load(st + food[nom] + ".png")
                                sprite.znach = nom
                            else:
                                pygame.mixer.music.load(load_sound("eating.mp3"))
                                pygame.mixer.music.play()
                                sprite.kill()
                                if sprite.znach == 1:
                                    pygame.mixer.music.load(load_sound("tuch.mp3"))
                                    pygame.mixer.music.play()
                                    player.hp -= 10
                                    player.max_hp -= 10
                                    player.damage -= 10
                                    player.max_damage -= 10
                                    player.armor -= 10
                                    player.max_armor -= 10
                                elif sprite.znach % 3 == 0:
                                    player.hp += 10
                                    player.max_hp += 10
                                elif sprite.znach % 3 == 1:
                                    player.damage += 10
                                    player.max_damage += 10
                                else:
                                    player.armor += 10
                                    player.max_armor += 10
                elif key == pygame.K_ESCAPE:
                    if not pause_screen(number_room, number_level, hero):
                        return
            if event.type == pygame.MOUSEBUTTONDOWN and \
                    player.die_animation < len(player.sl_images["die"]) * 5:
                if event.button == 1:
                    player.left = False
                    player.right = False
                    player.figth = True
                    player.pos_attack = event.pos
        if player.die_animation < len(player.sl_images["die"]) * 5:
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
            for sprite in enemy_group:
                sprite.update()
        elif player.die_animation == len(player.sl_images["die"]) * 5:
            game_over()
            return
        info_group.remove(hp_sprite, armor_sprite)
        hp_sprite = render_text(str(max(0, player.hp)), 100, 50, color=(255, 0, 0))
        armor_sprite = render_text(str(player.armor), 100, 100, color=(128, 128, 128))
        info_group.add(hp_sprite, armor_sprite)
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        camera.apply(player)
        screen.fill((255, 255, 255))
        screen.blit(background, background.get_rect())
        all_sprites.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)
        info_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    return


# работа с окном победы
def win():
    pygame.mixer.music.load(load_sound("win.mp3"))
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\win.png")
    image.rect = image.image.get_rect()
    sprite.add(image)
    sprite.draw(screen)
    sprite.draw(screen)
    con = sqlite3.connect("player.db")
    cur = con.cursor()
    cur.execute("""UPDATE info_player SET hero = ?, level = ? WHERE login = ?""",
                ("NO", -1, player_login))
    con.commit()
    con.close()
    pygame.mixer.music.play(loops=-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                pygame.mixer.music.stop()
                return
        pygame.display.flip()


# работа с окном паузы
def pause_screen(number_room, number_level, hero):
    intro_text = {"CONTINUE": [(255, 423), (477, 55)], "SAVE": [(298, 573), (393, 50)],
                  "EXIT": [(378, 702), (244, 59)]}
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\pause.png", colorkey=-1)
    image.rect = image.image.get_rect()
    sprite.add(image)
    intro_text = update_intro_text(intro_text)
    sprite.draw(screen)
    action_sprite = pygame.sprite.Group()
    push_continue = False
    push_save = False
    push_exit = False
    muzik = 0
    text_sprite = pygame.sprite.Group()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                flag = 0
                push_continue = False
                push_save = False
                push_exit = False
                for value in intro_text.values():
                    if (value[0][0] <= x <= value[0][0] + value[1][0] and
                            value[0][1] <= y <= value[0][1] + value[1][1]):
                        flag = 1
                        if value[0] == intro_text["CONTINUE"][0]:
                            push_continue = True
                        elif value[0] == intro_text["SAVE"][0]:
                            push_save = True
                        elif value[0] == intro_text["EXIT"][0]:
                            push_exit = True
                        action_sprite.add(value[2])
                        if muzik == 0:
                            pygame.mixer.music.load(load_sound("click.mp3"))
                            pygame.mixer.music.play()
                            muzik = 1
                        break
                if flag == 0:
                    pygame.mixer.music.stop()
                    muzik = 0
                    action_sprite = pygame.sprite.Group()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if push_continue:
                    return True
                elif push_save:
                    con = sqlite3.connect("player.db")
                    cur = con.cursor()
                    ch = number_level * 5 + number_room
                    cur.execute("""UPDATE info_player SET hero = ?, hp = ?, damage = ?, armor = ?,  
                                   level = ? WHERE login = ?""", (hero, player.max_hp,
                                                                  player.max_damage,
                                                                  player.max_armor,
                                                                  ch if ch != 0 else -1,
                                                                  player_login))
                    con.commit()
                    con.close()
                    return False
                elif push_exit:
                    con = sqlite3.connect("player.db")
                    cur = con.cursor()
                    cur.execute("""UPDATE info_player SET hero = ?, level = ?, hp = ?, damage = ?, 
                                   armor = ? WHERE login = ?""", ("NO", -1, -1, -1, -1,
                                                                  player_login))
                    con.commit()
                    con.close()
                    return False
        screen.fill((0, 0, 0))
        sprite.draw(screen)
        action_sprite.draw(screen)
        text_sprite.draw(screen)
        pygame.display.flip()


# работа с окном поражения
def game_over():
    MYEVENTTYPE = 10
    pygame.mixer.music.load(load_sound("game_over.mp3"))
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\game_over.png")
    image.rect = image.image.get_rect()
    sprite.add(image)
    sprite.draw(screen)
    sprite.draw(screen)
    pygame.time.set_timer(MYEVENTTYPE, 20)
    coord = [(95, 340), (906, 390)]
    con = sqlite3.connect("player.db")
    cur = con.cursor()
    cur.execute("""UPDATE info_player SET hero = ?, level = ?, hp = ?, damage = ?, armor = ?
                   WHERE login = ?""", ("NO", -1, -1, -1, -1, player_login))
    con.commit()
    con.close()
    pygame.mixer.music.play(loops=-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                pygame.mixer.music.stop()
                return
            if event.type == MYEVENTTYPE:
                pygame.draw.circle(screen, pygame.Color(255, 255, 255), coord[0], 10)
                pygame.draw.circle(screen, pygame.Color(255, 255, 255), coord[1], 10)
                if coord[0][1] != 950:
                    coord[0] = (coord[0][0], coord[0][1] + 1)
                    coord[1] = (coord[1][0], coord[1][1] + 1)
        pygame.display.flip()


# работа с окном правил
def rules():
    group = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\rules.jpg")
    image.rect = image.image.get_rect()
    group.add(image)
    screen.fill((0, 0, 0))
    group.draw(screen)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return


# работа с основным окном программы
def main_window(hero, level, hp, damage, armor):
    intro_text = {"START": [(266, 285), (462, 70)], "RULE": [(338, 398), (312, 60)],
                  "EXIT": [(368, 498), (255, 55)]}
    sprite = pygame.sprite.Group()
    image = pygame.sprite.Sprite()
    image.image = load_image("background\\main.png")
    image.rect = image.image.get_rect()
    sprite.add(image)
    intro_text = update_intro_text(intro_text)
    sprite.draw(screen)
    action_sprite = pygame.sprite.Group()
    push_start = False
    push_rule = False
    push_exit = False
    muzik = 0
    text_sprite = pygame.sprite.Group()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                flag = 0
                push_start = False
                push_rule = False
                push_exit = False
                for value in intro_text.values():
                    if (value[0][0] <= x <= value[0][0] + value[1][0] and
                            value[0][1] <= y <= value[0][1] + value[1][1]):
                        flag = 1
                        if value[0] == intro_text["START"][0]:
                            push_start = True
                        elif value[0] == intro_text["RULE"][0]:
                            push_rule = True
                        elif value[0] == intro_text["EXIT"][0]:
                            push_exit = True
                        action_sprite.add(value[2])
                        if muzik == 0:
                            pygame.mixer.music.load(load_sound("click.mp3"))
                            pygame.mixer.music.play()
                            muzik = 1
                        break
                if flag == 0:
                    pygame.mixer.music.stop()
                    muzik = 0
                    action_sprite = pygame.sprite.Group()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if push_start:
                    if hero == "NO" and level == 0:
                        pass
                    else:
                        main()
                elif push_rule:
                    rules()
                elif push_exit:
                    terminate()
        screen.fill((0, 0, 0))
        sprite.draw(screen)
        action_sprite.draw(screen)
        text_sprite.draw(screen)
        pygame.display.flip()


# отрисовка уровня
def generate_level(level, hp, damage, armor):
    new_player = None
    for x in range(len(level)):
        for y in range(len(level[0])):
            if level[x][y] == ".":
                Tile("empty", x, y)
            elif level[x][y] == "^":
                Tile("gate", x, y)
            elif level[x][y] == "!":
                Tile("door", x, y)
            elif level[x][y] == "$":
                Tile("empty", x, y)
                Tile("box", x, y)
            elif level[x][y] == "#":
                Tile("wall", x, y)
            elif level[x][y] == "O":
                Tile("empty", x, y)
                Enemy(x, y)
            elif level[x][y] == "@":
                Tile("empty", x, y)
                new_player = Player(class_hero, x, y, hp, damage, armor)
    return new_player


st = "blocks\\"
tile_images = {"wall": load_image(st + "wall_2.png"), "empty": load_image(st + "ground.png"),
               "door": load_image(st + "door.png"), "box": load_image(st + "box.png"),
               "gate": load_image(st + "gate.png"), "hp": load_image("menu\\hp.png", colorkey=-1),
               "armor": load_image("menu\\armor.png", colorkey=-1)}
food = ["Apple", "AppleWorm", "Avocado", "Bacon", "Beer", "Boar", "Bread", "Brownie", "Bug",
        "Cheese", "Cherry", "Chicken", "ChickenLeg", "Cookie", "DragonFruit", "Eggplant", "Eggs",
        "Fish", "FishFillet", "FishSteak", "Grub", "Grubs", "Honey", "Honeycomb", "Jam", "Jerky",
        "Lemon", "Marmalade", "MelonCantaloupe", "MelonHoneydew", "MelonWater", "Moonshine",
        "Olive", "Onion", "Peach", "PepperGreen", "Pepperoni", "PepperRed", "Pickle",
        "PickledEggs", "PieApple", "PieLemon", "PiePumpkin", "Pineapple", "Potato"]
tile_width = tile_height = 50
level = []
player = None
player_login = ""
info_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
hall_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
hero, uroven, hp, damage, armor = start_screen()
main_window(hero, uroven, hp, damage, armor)
con.close()
pygame.quit()
