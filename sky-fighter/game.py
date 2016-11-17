import pygame
import copy

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
ENEMY_SIZE = 80


class Directions:
	UP = 'Up'
	DOWN = 'Down'
	LEFT = 'Left'
	RIGHT = 'Right'
	STOP = 'Stop'


class GameState(object):
	def __init__(self, game):
		self.data = game
		self.getPositions()

	def getPositions(self):
		i = 1
		res = {}
		res[0] = (self.data.player.rect.x, self.data.player.rect.y)
		for enemy in self.data.enemy_list:
			pos = (enemy.rect.x, enemy.rect.y)
			res[i] = pos
			i += 1
		for projectile in self.data.projectile_list:
			pos = (projectile.rect.x, projectile.rect.y)
			res[i] = pos
			i += 1
		self.positions = res
		return res

	def getLegalActions(self, index):
		res = []
		player = self.data.player
		curPos = (player.rect.top, player.rect.left)
		playerHeight = player.rect.height
		playerWidth = player.rect.width
		if curPos[0] > 0:
			res.append(Directions.UP)
		if curPos[0] < SCREEN_HEIGHT - playerHeight:
			res.append(Directions.DOWN)
		if curPos[1] > 0:
			res.append(Directions.LEFT)
		if curPos[1] < SCREEN_WIDTH - playerWidth:
			res.append(Directions.RIGHT)
		return res

	def getScore(self):
		return self.data.score

	def getPlayerPosition(self):
		return self.player.rect.x, self.player.rect.y

	def getPlayer(self):
		return self.data.player

	def getLethal(self):
		return self.data.enemy_list, self.data.projectile_list

	def getEnemyPositions(self):
		res = []
		for enemy in self.data.enemy_list:
			res.append((enemy.rect.x, enemy.rect.y))
		return res

	def getProjPositions(self):
		res = []
		for projectile in self.data.projectile_list:
			res.append((projectile.rect.x, projectile.rect.y))
		return res

	def getMisslPositions(self):
		res = []
		for missile in self.data.missile_list:
			res.append((missile.rect.x, missile.rect.y))
		return res

	def isWin(self):
		return False

	def isLose(self):
		hitList = pygame.sprite.spritecollide(self.getPlayer(), self.getLethal()[0], \
			False, pygame.sprite.collide_mask)
		if len(hitList) > 0:
			return True
		hitList = pygame.sprite.spritecollide(self.getPlayer(), self.getLethal()[1], \
			False, pygame.sprite.collide_mask)
		if len(hitList) > 0:
			return True
		return False

	def getEnemyImgSize(self):
		return ENEMY_SIZE, ENEMY_SIZE

	def isEnd(self):
		return self.terminate

	def getLevel(self):
		if self.getScore() >= 100:
			return 3
		elif self.getScore() >= 50:
			return 2
		else:
			return 1

	def getEnemyNum(self):
		return len(self.data.enemy_list)

	def getNumAgents(self):
		return len(self.data.enemy_list) + 1

	def generateSuccessor(self, index, action):
		nextState = GameState(self.data)
		game = nextState.data

		if index == 0:
			# for projectile in game.projectile_list:
			# 	projectile.update()

			game.player.update(action)
		else:
			print index
			for enemy in game.enemy_list:
				index -= 1
				if index == 0:
					enemy.updateWithAction(action)
					break

		return GameState(game)
