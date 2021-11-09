import pygame
from pygame import mixer
from pygame.locals import *
import sys
import random

# 定义帧
clock = pygame.time.Clock()
fps = 60

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
screen_width = 400
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("太空侵略者")

# 定义字体
font30 = pygame.font.SysFont("Constantia", 30)
font40 = pygame.font.SysFont("Constantia", 40)

# 加载音效
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

explosion_fx_ship = pygame.mixer.Sound("img/explosion.wav")
explosion_fx_ship.set_volume(1)
# 定义游戏变量
rows = 5
cols = 5
alien_cooldown = 1000
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0 # 0游戏没有结束 1是玩赢了 -1 是输了

# 定义健康条颜色
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# 加载图片
bg = pygame.image.load("img/bg.png")

def draw_bg():
    screen.blit(bg, (0, 0))

# 定义一个文字提示的函数
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# 创建太空飞船的类
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # 设置移动速度
        speed = 8

        # 设置一个冷却时间变量
        cooldown = 500 # 毫秒
        game_over = 0
        # 按键
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        # 记录当前时间
        time_now = pygame.time.get_ticks()

        # 发射子弹
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        # 创建蒙版
        self.mask = pygame.mask.from_surface(self.image)

        # 画健康条
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            explosion_fx_ship.play()
            self.kill()
            game_over = -1
        return game_over



# 创建子弹
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()

        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


# 创建外星人
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

# 外星人子弹
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()

        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # 减少健康条
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

# 创建爆炸类
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            # 根据尺寸缩放
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            # 将图像加到列表中
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # 更新爆炸动画
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        # 如果动画完成，删除爆炸
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

# create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# 创建飞船
spaceship = Spaceship(screen_width // 2, screen_height - 80, 3)
spaceship_group.add(spaceship)

def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(item * 70 + 50, row * 60 + 50)
            alien_group.add(alien)

create_aliens()
run = True
while run:
    clock.tick(fps)
    # 画背景色
    draw_bg()
    if countdown == 0:
        # 创建随机的外星人子弹
        # 记录当前时间
        time_now = pygame.time.get_ticks()
        # 发射子弹
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now

        # 检查所有的敌人是否被消灭
        if len(alien_group) == 0:
            game_over = 1
        if game_over == 0:
            # 更新飞船
            game_over = spaceship.update()

            # 更新子弹
            bullet_group.update()

            # 更新外星人
            alien_group.update()

            # 更新外星人子弹
            alien_bullet_group.update()
        else:
            if game_over == -1:
                draw_text("GET OVER!", font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text("YOU WIN!", font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))

    if countdown > 0:
        draw_text("GET READY!", font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer

    # 更新爆炸
    explosion_group.update()

    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
    pygame.display.update()