import pygame
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("射击游戏")

# 设置帧
clock = pygame.time.Clock()
FPS = 60

# 定义玩家移动变量
moving_left = False
moving_right = False

# 定义颜色
BG = (144, 201, 120)
# 刷新背景函数
def draw_bg():
	screen.fill(BG)

class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed):
		super().__init__()
		self.char_type = char_type
		self.speed = speed
		self.direction = 1
		self.flip = False
		img = pygame.image.load(f"img/{char_type}/Idle/0.png")
		self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
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
		# 更新矩形的位置
		self.rect.x += dx
		self.rect.y += dy
	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


player = Soldier("player", 200, 200, 3, 5)
enemy = Soldier("enemy", 400, 200, 3, 5)

run = True
while run:
	clock.tick(FPS)
	draw_bg()
	player.move(moving_left, moving_right)
	player.draw()
	enemy.draw()

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
			if event.key == pygame.K_ESCAPE:
				run = False
		# 按键释放
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False


	pygame.display.update()