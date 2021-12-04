import pygame
import sys
import os

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
# 定义玩家移动变量
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# 加载图片
# 子弹
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()

# 定义颜色
BG = (144, 201, 120)
RED = (255, 0, 0)
# 刷新背景函数
def draw_bg():
	screen.fill(BG)
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

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
	def update(self):
		self.update_animation()
		self.check_alive()
		# 更新冷却时间
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1
	def move(self, moving_left, moving_right):
		# 重置移动变量
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
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.in_air = False
		# 更新矩形的位置
		self.rect.x += dx
		self.rect.y += dy
	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery,
							self.direction)
			bullet_group.add(bullet)
			#减少弹药
			self.ammo -= 1
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
		self.rect.x += (self.direction * self.speed)
		# 检测子弹如果已经超出了窗口
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		# 检测子弹的碰撞
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
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
	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y
		# 检测手雷与地面的碰撞
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.speed = 0
		# 检测手雷如果与墙碰撞
		if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
			self.direction *= -1
		# 更新受累的位置
		self.rect.x += dx
		self.rect.y += dy


#创建子弹群组
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()

player = Soldier("player", 200, 200, 3, 5, 20, 5)
enemy = Soldier("enemy", 400, 200, 3, 5, 20, 0)

run = True
while run:
	clock.tick(FPS)
	draw_bg()
	player.update()
	player.draw()
	enemy.update()
	enemy.draw()

	# 更新和画组
	bullet_group.update()
	grenade_group.update()
	bullet_group.draw(screen)
	grenade_group.draw(screen)

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

		player.move(moving_left, moving_right)

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