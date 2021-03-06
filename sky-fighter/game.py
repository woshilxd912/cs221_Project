from vars import *
from math import sqrt


def checkCollide(item1, item2):
    if item1.rect.x <= item2.rect.x:
        xCollide = item2.rect.x - item1.rect.x < item1.rect.width
    else:
        xCollide = item1.rect.x - item2.rect.x < item2.rect.width
    if item1.rect.y <= item2.rect.y:
        yCollide = item2.rect.y - item1.rect.y < item1.rect.height
    else:
        yCollide = item1.rect.y - item2.rect.y < item2.rect.height
    # print "item 1: %d, %d, %d, %d" % (item1.rect.x, item1.rect.y, item1.rect.width, item1.rect.height)
    # print "item 2: %d, %d, %d, %d" % (item2.rect.x, item2.rect.y, item2.rect.width, item2.rect.height)
    # print xCollide and yCollide
    return xCollide and yCollide


class Directions:
    UP = 'Up'
    DOWN = 'Down'
    STOP = 'Stop'
    LEFT = 'Left'
    RIGHT = 'Right'
    SHOOT = 'Shoot'


class Item(object):
    def __init__(self, rect, speed_x=0, speed_y=0, isPlayer=False):
        self.x = rect.x
        self.y = rect.y
        self.width = rect.width
        self.height = rect.height
        self.rect = rect
        self.isPlayer = isPlayer
        if self.isPlayer:
            self.speed_x = PLAYER_SPEED
            self.speed_y = PLAYER_SPEED
        else:
            self.speed_x = speed_x
            self.speed_y = speed_y

    def getDistance(self, item2):
        dis = sqrt((self.x - item2.x) ** 2 + (self.y - item2.y) ** 2)
        return dis

    def checkXCollide(self, item2):
        if self.x < item2.x:
            return item2.x - self.x < self.width
        else:
            return self.x - item2.x < item2.width

    def checkYCollide(self, item2):
        if self.y < item2.y:
            return item2.y - self.y < self.height
        else:
            return self.y - item2.y < item2.height

    def checkCollide(self, item2):
        return self.checkXCollide(item2) and self.checkYCollide(item2)

    def updateProjectilePosition(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def updateMissilePosition(self):
        self.updateProjectilePosition()

    def updateFlightPosition(self, action=None, playerX=None):
        if playerX is not None:
            if self.rect.x > playerX:
                self.speed_x = -abs(self.speed_x)
            else:
                self.speed_x = abs(self.speed_x)
        if action is None:
            self.x += self.speed_x
            self.y += self.speed_y
        else:
            if action == Directions.SHOOT:
                return
            elif action == Directions.UP:
                if self.y - self.speed_y <= 0:
                    self.y = 0
                else:
                    self.y -= self.speed_y
            elif action == Directions.DOWN:
                if self.y + self.speed_y + self.height >= SCREEN_HEIGHT:
                    self.y = SCREEN_HEIGHT - self.height
                else:
                    self.y += self.speed_y
            elif action == Directions.LEFT:
                if self.x - self.speed_x <= 0:
                    self.x = 0
                else:
                    self.x -= self.speed_x
            elif action == Directions.RIGHT:
                if self.x + self.speed_x + self.width >= SCREEN_WIDTH:
                    self.x = SCREEN_WIDTH - self.width
                else:
                    self.x += self.speed_x


class GameState(object):
    def __init__(self, game=None, previousState=None, currentAgent=0, enemyIsAgent=False):
        self.enemy_list = []
        self.missile_list = []
        self.projectile_list = []
        self.enemyIsAI = enemyIsAgent
        state = None
        if game is not None:
            state = game
        elif previousState is not None:
            state = previousState

        self.player = Item(state.player.rect, isPlayer=True)
        for enemy in state.enemy_list:
            self.enemy_list.append(Item(enemy.rect, speed_x=enemy.speed_x, speed_y=enemy.speed_y))
        for projectile in state.projectile_list:
            self.projectile_list.append(Item(projectile.rect, speed_x=projectile.speed_x, speed_y=projectile.speed_y))
        for missile in state.missile_list:
            self.missile_list.append(Item(missile.rect, speed_x=missile.speed_x, speed_y=missile.speed_y))
        self.score = state.score
        self.currentAgent = currentAgent

    def getProjPositions(self):
        res = []
        for projectile in self.projectile_list:
            res.append((projectile.x, projectile.y))
        return res

    def getPlayerPosition(self):
        return self.player.x, self.player.y

    def getEnemyPositions(self):
        res = []
        for enemy in self.enemy_list:
            res.append((enemy.x, enemy.y))
        return res

    def getFlight(self, agentIndex):
        if agentIndex == 0:
            return self.player
        return self.enemy_list[agentIndex - 1]

    def getLegalActions(self, agentIndex):
        legalActions = []
        flight = self.getFlight(agentIndex)
        # need to check agent's position to make sure it stays in the screen
        if agentIndex == 0:
            legalActions.append(Directions.STOP)
            legalActions.append(Directions.SHOOT)
            if flight.x > 0:
                legalActions.append(Directions.LEFT)
            if flight.x < SCREEN_WIDTH - flight.width:
                legalActions.append(Directions.RIGHT)
            if flight.y > 0:
                legalActions.append(Directions.UP)
            if flight.y < SCREEN_HEIGHT - flight.height:
                legalActions.append(Directions.DOWN)
        return legalActions

    def getScore(self):
        return self.score

    def getPlayer(self):
        return self.player

    def getEnemies(self):
        return self.enemy_list

    def getProjectiles(self):
        return self.projectile_list

    def isWin(self):
        return False

    def isLose(self):
        for enemy in self.enemy_list:
            if enemy.checkCollide(self.player):
                return True
        for projectile in self.projectile_list:
            if projectile.checkCollide(self.player):
                return True
        return False

    def getMissileHitList(self, agentIndex):
        enemy = self.getFlight(agentIndex)
        hitList = []
        for missile in self.missile_list:
            if enemy.checkCollide(missile):
                hitList.append(missile)
        return hitList

    def removeEnemy(self, agentIndex):
        self.enemy_list.pop(agentIndex - 1)

    def removeMissile(self, missileIndex):
        self.missile_list.pop(missileIndex)

    def getNextAgentIndex(self):
        return (self.currentAgent + 1) % self.getNumAgents()

    def getLevel(self):
        if self.getScore() >= SCORE_LEVEL_THREE:
            return 3
        elif self.getScore() >= SCORE_LEVEL_TWO:
            return 2
        else:
            return 1

    def getNumAgents(self):
        # if self.enemyIsAgent:
        #     return len(self.enemy_list) + 1
        # else:
        return 1

    def getNumMissile(self):
        return len(self.missile_list)

    def getNumProjectile(self):
        return len(self.projectile_list)

    def getMissilePositions(self):
        res = []
        for missile in self.missile_list:
            res.append((missile.x, missile.y))
        return res

    def getLastMissile(self):
        if len(self.missile_list) > 0:
            return self.missile_list[-1]
        else:
            return None

    def updateProjectilesPositions(self):
        for projectile in self.projectile_list:
            projectile.updateProjectilePosition()

    def updateMissilePositions(self):
        for missile in self.missile_list:
            missile.updateMissilePosition()

    def updateEnemyPositions(self):
        for enemy in self.enemy_list:
            if self.enemyIsAI:
                enemy.updateFlightPosition(playerX=self.getPlayer().x)
            else:
                enemy.updateFlightPosition()

    def updatePlayerPosition(self, action=None):
        self.getPlayer().updateFlightPosition(action=action)

    def generateSuccessor(self, agentIndex, action):
        nextAgentIndex = self.getNextAgentIndex()
        nextState = GameState(previousState=self, currentAgent=nextAgentIndex)
        if agentIndex == 0:
            # update each object's position
            nextState.updateProjectilesPositions()
            nextState.updateMissilePositions()
            nextState.updatePlayerPosition(action=action)
            nextState.updateEnemyPositions()
            if action == Directions.SHOOT:
                nextState.score += SCORE_FIRE_MISSILE
                missile = Item(self.player.rect, speed_y=-MISSILE_SPEED)
                missile.x = missile.x + self.player.rect.width / 2 - MISSILE_WIDTH / 2
                missile.y = missile.y + self.player.rect.height / 2 - MISSILE_HEIGHT / 2
                missile.width = MISSILE_WIDTH
                missile.height = MISSILE_HEIGHT
                nextState.missile_list.append(missile)
            for enemy in nextState.enemy_list:
                missileHitList = nextState.getMissileHitList(nextState.enemy_list.index(enemy))
                if len(missileHitList) > 0:
                    nextState.score += SCORE_HIT_ENEMY
                    nextState.enemy_list.remove(enemy)
                    for missile in missileHitList:
                        nextState.missile_list.remove(missile)
            if nextState.isLose():
                nextState.score = SCORE_LOSE
                # pass
            else:
                nextState.score += SCORE_STAY_ONE_FRAME
        else:
            enemy = nextState.getFlight(agentIndex)
            enemy.updateFlightPosition(action)
            hitList = nextState.getMissileHitList(agentIndex)
            if len(hitList) > 0:
                nextState.score += SCORE_HIT_ENEMY
            if enemy.checkCollide(nextState.player):
                nextState.score = SCORE_LOSE
        return nextState
