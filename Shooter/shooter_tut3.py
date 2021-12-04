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

# 定义颜色
BG = (144, 201, 120)
RED = (255, 0, 0)
# 刷新背景函数
def draw_bg():
	screen.fill(BG)
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed):
		super().__init__()
		self.alive = True # 定义或者还是死亡变量
		self.char_type = char_type
		self.speed = speed
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
		animation_types = ["Idle", "Run", "Jump"]
		for animation in animation_types:
			# 重置临时列表
			temp_list = []
			# 统计每种动画帧数量
			num_of_frames = len(os.listdir(f"img/{char_type}/{animation}"))
			for i in range(num_of_frames):
				img = pygame.image.load(f"img/{char_type}/{animation}/{i}.png")
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

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
			self.frame_index = 0
	def update_action(self, new_action):
		 # 判断不同的行动播放不同的动画
		if new_action != self.action:
			self.action = new_action
			# 更新动画设置
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


player = Soldier("player", 200, 200, 3, 5)
enemy = Soldier("enemy", 400, 200, 3, 5)

run = True
while run:
	clock.tick(FPS)
	draw_bg()
	player.update_animation()
	player.draw()
	enemy.draw()
	# 更新玩家的动作
	if player.alive:
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


	pygame.display.update()