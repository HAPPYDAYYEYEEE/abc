import pygame
import sys
import os
import pickle
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("平台游戏")

# 定义字体
font_score = pygame.font.SysFont("Bauhaus 93", 30)

# 定义游戏变量
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 8
score = 0

# 定义文字颜色
white = (255, 255, 255)


# 加载图片
sun_img = pygame.image.load("img/sun.png")
bg_img = pygame.image.load("img/sky.png")
restart_img = pygame.image.load("img/restart_btn.png")
start_img = pygame.image.load("img/start_btn.png")
exit_img = pygame.image.load("img/exit_btn.png")

# 显示文本信息
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def reset_level(level):
    player.__init__(100, screen_height - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    # 加载并且创建地图
    if os.path.exists(f"./level{level}_data"):
        pickle_in = open(f"level{level}_data", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

# 创建按钮
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # 得到鼠标的位置
        pos = pygame.mouse.get_pos()
        # 检测鼠标是否经过按钮位置和是否已点击
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # 将按钮画到屏幕上
        screen.blit(self.image, self.rect)

        return action


# 创建玩家
class Player():
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f"img/guy{num}.png")
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("img/ghost.png")
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # 获取按键事件
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1

            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            # 播放动画
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # 检测玩家与每个泥块与草地的碰撞
            self.in_air = True
            for tile in world.tile_list:
                #判断玩家在x方向上的碰撞
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # 检测玩家在y方向的碰撞
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #检测玩家顶部与泥块底部碰撞
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #检测玩家底部与泥块顶部的碰撞
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # 玩家与敌人的碰撞
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1

            # 玩家与熔岩的碰撞
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            # 玩家与出口的碰撞
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # 更新玩家的位置
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # 把玩家画到屏幕上
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over


# def draw_grid():
#     for line in range(0, 20):
#         pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))



# 创建地图类
class World(object):
    def __init__(self, data):
        self.tile_list = []

        #加载图片
        dirt_img = pygame.image.load("img/dirt.png")
        grass_img = pygame.image.load("img/grass.png")
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# 创建敌人
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

# 创建熔岩
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 创建硬币
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load("img/coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# 创建出口
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# 定义地图列表
# world_data = [
# [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
# [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
# [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
# [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
# [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
# [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
# [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
# [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# ]

player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# 显示虚拟硬币
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# 加载地图数据
if os.path.exists(f"./level{level}_data"):
    pickle_in = open(f"level{level}_data", "rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)
# 实例化按钮
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True
while run:

    clock.tick(fps)

    # 加载窗口背景
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        # 画地图
        world.draw()

        # 显示敌人
        if game_over == 0:
            blob_group.update()
            # 检测玩家与硬币的碰撞
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            draw_text("X" + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        # 显示玩家
        game_over = player.update(game_over)

        # 判断玩家是否死掉
        if game_over == -1:
            if restart_button.draw():
                player.__init__(100, screen_height - 130)
                game_over = 0
                score = 0
        # 判断游戏是否通关
        if game_over == 1:
            level += 1
            if level <= max_levels:
               world_data = []
               world = reset_level(level)
               game_over = 0

            else:
                if restart_button.draw():
                    level = 0
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0


    # 画格子
    # draw_grid()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
    pygame.display.update()