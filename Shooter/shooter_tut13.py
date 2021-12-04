import pygame
import sys
import os
import random
import math
import csv
import button
from pygame import mixer

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("射击游戏")

# 设置帧
clock = pygame.time.Clock()
FPS = 60

# 定义游戏变量
# 定义重力
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
# 变量
start_game = False
start_intro = False

# 定义玩家移动变量
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# 加载音乐和声音
pygame.mixer.music.load("audio/music2.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound("audio/jump.wav")
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound("audio/shot.wav")
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound("audio/grenade.wav")
grenade_fx.set_volume(0.7)

# 加载本精图片
pine1_img = pygame.image.load("img/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("img/background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("img/background/mountain.png").convert_alpha()
sky_img = pygame.image.load("img/background/sky_cloud.png").convert_alpha()
# 加载按钮图像
start_img = pygame.image.load("img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("img/exit_btn.png").convert_alpha()
restart_image = pygame.image.load("img/restart_btn.png").convert_alpha()
restart_img = pygame.transform.scale(restart_image, (int(restart_image.get_width() * 1.5), int(restart_image.get_height() * 1.5)))

# 加载图片a
# 加载21种瓷砖图像到列表中
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f"img/tile/{x}.png")
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

# 加载图片
# 子弹
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
# 加载物品
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()
item_boxes = {
	"Health": health_box_img,
	"Ammo": ammo_box_img,
	"Grenade": grenade_box_img
}
# 定义颜色
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# 定义字体
font = pygame.font.SysFont("华文行楷", 16)

# 定义一个显示文本函数
def draw_text(text, font, text_color, x, y):
	img = font.render(text, True, text_color)
	screen.blit(img, (x, y))

# 刷新背景函数
def draw_bg():
    screen.fill(BG)
    # pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))
    width = sky_img.get_width()
    for x in range(5):
	    screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
	    screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
	    screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
	    screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# 重置游戏
def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	# 创建空的瓷砖列表
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)
	return data

class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		super().__init__()
		self.alive = True # 定义或者还是死亡变量
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0 # 选择动作变量
		self.update_time = pygame.time.get_ticks()
		# 创建ai机器人特定边两个
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20) # 搜搜玩家在视线之内
		self.vision_grenade = pygame.Rect(0, 0, 6 * TILE_SIZE, 6 * TILE_SIZE)
		self.idling = False
		self.idling_counter = 0
		self.grenade_time = pygame.time.get_ticks()

		# 加载玩家是所有的图片类型
		animation_types = ["Idle", "Run", "Jump", "Death"]
		for animation in animation_types:
			# 重置临时列表
			temp_list = []
			# 统计每种动画帧数量
			num_of_frames = len(os.listdir(f"img/{char_type}/{animation}"))
			for i in range(num_of_frames):
				img = pygame.image.load(f"img/{char_type}/{animation}/{i}.png").convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.update_animation()
		self.check_alive()
		# 更新冷却时间
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1
	def move(self, moving_left, moving_right):
		# 重置移动变量
		screen_scroll = 0
		dx = 0
		dy = 0
		# 根据移动变量判断向左还是向右移动
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1
		# 跳跃
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True
		# 使用重力
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		# 检测与地面的碰撞
		for tile in world.objstacle_list:
			# 检测玩家与每个地面瓷砖x方向上的碰撞
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				# 检测机器人与墙壁碰撞就返回
				if self.char_type == "enemy":
					self.direction *= -1
					self.move_counter = 0
			# 检测玩家与瓷砖y方向上的碰撞
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				# 检测与地面底部的碰撞
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# 检测与地面顶部的碰撞
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		# 检测我方士兵与水面碰撞
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0
		# 检测从地图上坠落下来
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0
		# 检测与出口标志的碰撞
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True
		# 检测是否走到窗口边缘，如果走出了整个窗口边缘就停止
		if self.char_type == "player":
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0
		# if self.rect.bottom + dy > 300:
		# 	dy = 300 - self.rect.bottom
		# 	self.in_air = False
		# 更新矩形的位置
		self.rect.x += dx
		self.rect.y += dy
        # 在玩家相对地图的位置更新滚动地图
		if self.char_type == "player":
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < world.level_length * TILE_SIZE - SCREEN_WIDTH) \
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx
		return screen_scroll, level_complete

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
							self.direction)
			bullet_group.add(bullet)
			#减少弹药
			shot_fx.play()
			self.ammo -= 1
	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0) # 闲置状态
				self.idling = True
			# ai检测到我方士兵在附近
			if self.vision.colliderect(player.rect):
				# 停止巡逻并向地方开火
				self.update_action(0)
				# 开火
				self.shoot()
			else:
				now_time = pygame.time.get_ticks()
				self.vision_grenade.center = (self.rect.centerx + ((6 * TILE_SIZE) / 2) * self.direction, self.rect.centery)
				# pygame.draw.rect(screen, (0, 0, 255), self.vision_grenade)
				if self.vision_grenade.colliderect(player.rect):
					if self.grenades > 0:
						if now_time - self.grenade_time > random.randint(2000, 3000):
							# 敌方士兵停下扔手雷
							self.update_action(0)
							self.grenade_time = pygame.time.get_ticks()
							grenade = Grenade(self.rect.centerx, self.rect.centery, self.direction)
							grenade_group.add(grenade)
							self.grenades -= 1

				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
						self.idling_counter = 50
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1) # 选择动作
					self.move_counter += 1
					# 更新ai视觉范围移动
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
					# pygame.draw.rect(screen, RED, self.vision)
					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False
		# 敌人的滚动
		self.rect.x += screen_scroll

	def update_animation(self):
		# 更新动画
		ANIMATION_COOLDOWN= 100
		# 更新当前的帧
		self.image = self.animation_list[self.action][self.frame_index]
		# 检测现在的时间更新时间
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		# 检测如果列表索引超出了动画帧数
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0
	def update_action(self, new_action):
		 # 判断不同的行动播放不同的动画
		if new_action != self.action:
			self.action = new_action
			# 更新动画设置
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()
	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# 收集物品类
class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		super().__init__()
		self.item_type = item_type
		self.image = item_boxes.get(self.item_type)
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		# 滚动
		self.rect.x += screen_scroll
		# 检车士兵与物品的碰撞
		if pygame.sprite.collide_rect(self, player):
			# 检测获取箱子的种类
			if self.item_type == "Health":
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == "Ammo":
				player.ammo += 15
			elif self.item_type == "Grenade":
				player.grenades += 3
			# 删除物品
			self.kill()

# 创建血条类
class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health
	def draw(self, health):
		# 更新最新血条
		self.health = health
		# 计算血条的比率
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		super().__init__()
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		# 移动子弹
		self.rect.x += (self.direction * self.speed) + screen_scroll # 子弹加上滚动
		# 检测子弹如果已经超出了窗口
		# if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
		# 	self.kill()
		# 检测子弹与墙壁的碰撞
		for tile in world.objstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()
		# 检测子弹的碰撞
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

# 创建手雷
class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		super().__init__()
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction
		self.width = self.image.get_width()
		self.height = self.image.get_height()
	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y
		# 检测手雷与每个瓷砖地面的碰撞
		for tile in world.objstacle_list:
			# 检测手雷与x方向墙壁的碰撞
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			# 检测手雷与瓷砖y方向上的碰撞
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				# 检测与地面底部的碰撞
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# 检测与地面顶部的碰撞
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom

		# 检测手雷与地面的碰撞
		# if self.rect.bottom + dy > 300:
		# 	dy = 300 - self.rect.bottom
		# 	self.speed = 0
		# 检测手雷如果与墙碰撞
		# if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
		# 	self.direction *= -1
		# 更新受累的位置
		self.rect.x += dx + screen_scroll  # 手雷扔出去的时候滚动
		self.rect.y += dy

		# 手雷爆炸冷却时间
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.8)
			explosion_group.add(explosion)
			# 爆炸后对任何人在一定的范围内都有伤害
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				# if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE and \
				# 	abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE:
				# 	enemy.health -= 100
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50


# 创建地图的类
class World():
	def __init__(self):
		self.objstacle_list = [] # 障碍列表

	def process_data(self, data):
		self.level_length = len(data[0])
		# 迭代每个值更每个元素的值
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8: # 地面泥块
						self.objstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10: # 水
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14: # 装饰品
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15: # 创建我方士兵
						player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16: # 敌方士兵
						enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 5)
						enemy_group.add(enemy)
					elif tile == 17:
						# 收集子弹
						item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:
						# 收集手雷
						item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:
						# 收集医药
						item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar

	def draw(self):
		for tile in self.objstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])
# 装饰品类
class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		super().__init__()
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll

# 创建水
class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		super().__init__()
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll

# 出口类
class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		super().__init__()
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll

# 创建爆炸类
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		super().__init__()
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0

	def update(self):
		# 爆炸加滚动
		self.rect.x += screen_scroll
		EXPLOSION_SPEED = 4
		# 更新爆炸动画
		self.counter += 1
		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			# 检测爆炸完成后删除爆炸
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]
# 创建开幕闭幕
class ScreenFade():
	def __init__(self, direction, color, speed):
		self.direction = direction
		self.color = color
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:
			pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT)) # 向左拉开序幕
			pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT)) # 向右拉开序幕
			pygame.draw.rect(screen, self.color,
							 (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.color,
							 (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True
		if self.direction == 2:
			pygame.draw.rect(screen, self.color,
							 (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))

		return fade_complete
# 创建淡入淡出
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

# 创建开始、退出、重置菜单按钮
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 1)

#创建群组
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#  临时创建箱子
# item_box = ItemBox("Health", 100, 260)
# item_box_group.add(item_box)
# item_box = ItemBox("Ammo", 400, 260)
# item_box_group.add(item_box)
# item_box = ItemBox("Grenade", 500, 260)
# item_box_group.add(item_box)

# player = Soldier("player", 200, 300, 1.65, 5, 20, 5)
# health_bar = HealthBar(10, 10, player.health, player.health)
# enemy = Soldier("enemy", 500, 270, 1.65, 2, 20, 5)
# enemy2 = Soldier("enemy", 300, 270, 1.65, 2, 20, 5)
# enemy_group.add(enemy)
# enemy_group.add(enemy2)

# 创建空白瓷砖列表
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)

# 加载级别地图数据
with open(f"level{level}_data.csv", newline="") as csvfile:
	reader = csv.reader(csvfile, delimiter=",")
	for y, row in enumerate(reader):
		for x, tile in enumerate(row):
			world_data[y][x] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
	clock.tick(FPS)
	if start_game == False:
		# 显示菜单画面
		# 画菜单
		screen.fill(BG)
		# 增加按钮
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if exit_button.draw(screen):
			run = False
	else:
		draw_bg()
		# 显示地图
		world.draw()
		# 显示血条
		health_bar.draw(player.health)
		# 显示弹药量
		draw_text("子弹数量: ", font, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))
		# 显示手雷量
		draw_text("手雷数量: ", font, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img, (135 + (x * 15), 60))
		# 显示血条量
		# draw_text(f"AMMO: {player.ammo}", font, WHITE, 10, 35)

		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		# 更新和画组
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)
		# 显示淡入
		if start_intro:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0

		# 更新玩家的动作
		if player.alive:
			# 发射子弹
			if shoot:
				player.shoot()
			# 扔手雷
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
								  player.rect.top, player.direction)
				grenade_group.add(grenade)
				player.grenades -= 1
				grenade_thrown = True

			if player.in_air:
				player.update_action(2)
			elif moving_left or moving_right:
				player.update_action(1)
			else:
				player.update_action(0)

			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			# 检测玩家是否通过该级别
			if level_complete:
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVELS:
					# 加载下一关数据创建新地图
					with open(f"level{level}_data.csv", newline="") as csvfile:
						reader = csv.reader(csvfile, delimiter=",")
						for y, row in enumerate(reader):
							for x, tile in enumerate(row):
								world_data[y][x] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)
		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					# 重新加载地图数据
					with open(f"level{level}_data.csv", newline="") as csvfile:
						reader = csv.reader(csvfile, delimiter=",")
						for y, row in enumerate(reader):
							for x, tile in enumerate(row):
								world_data[y][x] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)


	for event in pygame.event.get():
		# 退出游戏
		if event.type == pygame.QUIT:
			run = False
			pygame.quit()
			sys.exit()
		# 键盘按键
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_w and player.alive:
			    player.jump = True
			    jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False
		# 按键释放
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False


	pygame.display.update()