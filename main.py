import pygame
import pygame_menu
import sys
from pygame.locals import *
import random, time
from pygame import mixer
import pickle
from operator import itemgetter

surface = pygame.display.set_mode((600,800))

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Game(metaclass = Singleton):
    def __init__(self):     
        pygame.init()
        self._font = pygame.font.SysFont("Verdana", 30)
    def startGame(self):
        GameLoop()
    def highscoreTable(self):
        h = Highscores()
        h.highscoreInit()
    def menuInit(self):
        self._menu = Menu()
        menuData = self._menu.menuInit()
        menuData.mainloop(surface)     

class Menu():
    def __init__(self):
        self._size = (600,800)
        mixer.music.load("assets/music/bg/menu.ogg")
        mixer.music.set_volume(0.1)
        mixer.music.play(-1)
        self._game = Game()
    def menuInit(self):
        menu = pygame_menu.Menu('Space game', self._size[0], self._size[1], theme=pygame_menu.themes.THEME_BLUE)
        menu.add.button('Play', self._game.startGame)
        menu.add.button('Highscores', self._game.highscoreTable)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        return menu
        

class Highscores():
    def __init__(self): 
        self._size = (600,800)  
        self._font = pygame.font.SysFont("Verdana", 30)   
        self._game = Game()
        mixer.music.load('assets/music/bg/highscore.ogg')
        mixer.music.play(-1)
        with open('data/HighTable.pickle', 'rb') as f:
            self._dict = pickle.load(f)
        self._dict = sorted(self._dict, key=itemgetter(1), reverse=True)
        self._FPS = 60
        self._FramePerSec = pygame.time.Clock()
        self._bg = pygame.image.load('assets/graphics/other/space2.png')
        surface.blit(self._bg,(0,0))
    def highscoreInit(self):
        while True:
            for event in pygame.event.get():    
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 0 <= mouse[0] <= 80 and 770 <= mouse[1] <= 800:
                        self._game.menuInit()
            mouse = pygame.mouse.get_pos()
            if len(self._dict) < 6:
                num = 1
                for i in range(0,len(self._dict)):
                    text = str(self._dict[num-1])
                    text = text.replace("[","")
                    text = text.replace("]","")
                    text = text.replace(",","")
                    text = text.replace("\'","")
                    highscoreText = self._font.render(text, True, (255,255,255))
                    surface.blit(highscoreText, (10,num*100)) 
                    num += 1  
            elif len(self._dict) >= 6:
                num = 1
                for i in range(0,6):
                    text = str(self._dict[num-1])
                    text = text.replace("[","")
                    text = text.replace("]","")
                    text = text.replace(",","")
                    text = text.replace("\'","")
                    highscoreText = self._font.render(text, True, (255,255,255))
                    surface.blit(highscoreText, (10,num*100)) 
                    num += 1  

            back = self._font.render('BACK', True, (255,255,255))
            surface.blit(back, (0,765))
            pygame.display.update()
            self._FramePerSec.tick(self._FPS)
    def afterGame(self, highscore):
        input_box1 = InputBox(200,400,200,40)
        input_boxes = [input_box1]
        while True:
            for event in pygame.event.get():    
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                for box in input_boxes:
                    name = box.handle_event(event)
                    if isinstance(name, str):
                        self._dict.append([name,highscore])
                        with open('data/HighTable.pickle', 'wb') as f:
                            pickle.dump(self._dict, f)
                        h = Highscores()
                        h.highscoreInit()
            
            endText = self._font.render("Enter your name and press Enter: ", True, (255,255,255))
            surface.blit(endText, (40,300))

            for box in input_boxes:
                box.update()
            
            for box in input_boxes:
                box.draw(surface)

            pygame.display.update()
            self._FramePerSec.tick(self._FPS)

        
        
class GameLoop(metaclass = Singleton):
    def __init__(self):
        self._list = ObjectsList()
        self._state = LevelOne()
        self._state.context = self
        self._bg = Background(self._state.getData()[0])
        self._FPS = 60
        surface.fill((255, 255, 255))
        self._FramePerSec = pygame.time.Clock()
        self._font_small = pygame.font.SysFont("Verdana", 20)
        pygame.display.set_caption("Game")
        self._iCounter = 0
        self._dt = 10
        self._gameOverFlag = 0
        self._changeStateCounter = 240
        mixer.music.load(self._state.getData()[1])
        mixer.music.play(-1)
        self.gameLoop()
    def changeState(self, state):
        self._state = state
        self._state.context = self
        self._bg = Background(self._state.getData()[0])
        mixer.music.load(self._state.getData()[1])
        mixer.music.play(-1)
        self._iCounter = 0
    def gameLoop(self):
        self._iCounter = 0
        highscore = 0
        objectsList = ObjectsList()
        debrisList = ObjectsDebrisList()
        enemyList = ObjectsEnemyList()
        bulletsList = ObjectsBulletsList()
        enemyBulletsList = ObjectsEnemyBulletsList()
        destroyedEnemies = ObjectsDestroyedList()
        objectsList.clearList()
        debrisList.clearList()
        enemyList.clearList()
        bulletsList.clearList()
        enemyBulletsList.clearList()
        destroyedEnemies.clearList()
        player = PlayerShip((300,600),(16,16),'assets/graphics/player/P1.png')
        objectsList.addObject(player)
        for enem in objectsList:
            if isinstance(enem, Enemy):
                enemyList.addObject(enem)
        for enem in enemyList:
            enem.rotCenter(180)
        while True:
            destroyedEnemies.clearList()
            for event in pygame.event.get():    
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self._bg.update()
            self._bg.render()

            healthText = self._font_small.render("Health: ", True, (255,255,255))
            surface.blit(healthText, (10,10))

            health = self._font_small.render(str(player.getHealth()), True, (255,255,255))
            surface.blit(health, (90,10))

            highText = self._font_small.render("Score: ", True, (255,255,255))
            surface.blit(highText, (10,40))

            highscoreText = self._font_small.render(str(highscore), True, (255,255,255))
            surface.blit(highscoreText, (90,40))

            for object in objectsList:
                surface.blit(object.getSprite(), object.getPos())
                object.movement()
                if object.rect.centery > 815:
                    object.removeObject(self._iCounter)
                if object.rect.centery < -150:
                    object.removeObject(self._iCounter)
            
            if player in objectsList:
                player.fire()
            
            if player in objectsList:
                if pygame.sprite.spritecollideany(player, enemyList):
                    enemy1 = pygame.sprite.spritecollideany(player, enemyList)
                    if player.getIFrames() <= 0:
                        player.getHit()
                    elif player.getIFrames() > 0:
                        enemy1.removeObject(self._iCounter)
                    if player.getHealth() <= 0 and player.getAlive() == 1:
                        gameOver = GameEnd(self._iCounter, player, highscore)
                        self._gameOverFlag = 1
                elif pygame.sprite.spritecollideany(player, enemyBulletsList):
                    bullet1 = pygame.sprite.spritecollideany(player, enemyBulletsList)
                    if player.getIFrames() <= 0:
                        player.getHit()
                        bullet1.removeObject(self._iCounter)
                    elif player.getIFrames() > 0:
                        bullet1.removeObject(self._iCounter)
                    if player.getHealth() <= 0 and player.getAlive() == 1:
                        gameOver = GameEnd(self._iCounter, player, highscore)
                        self._gameOverFlag = 1
                      
            
            if self._gameOverFlag == 1:
                if player in objectsList:
                    objectsList.removeObject(player)
                gameOver.gameOver(self._iCounter) 
                          

            for object in bulletsList:
                if pygame.sprite.spritecollideany(object, enemyList):
                    e1 = pygame.sprite.spritecollideany(object, enemyList)
                    e1.getHit(object, self._iCounter)
                    object.removeObject(self._iCounter)

            if player.getIFrames() >= 0:
                player.decIFrames()
            

            if (self._iCounter % self._dt)==0:
                for object in debrisList:
                    object.update(self._iCounter)

            if self._iCounter < 3000:
                for object in enemyList:
                    object.fire()
                r = random.uniform(0,10)
                if r < 0.5:
                   self._state.spawner()

            if self._iCounter == 3000:
                self._state.bossSpawner()

            if self._iCounter > 3240:
                if (self._iCounter % self._dt)==0:
                    for object in enemyList:
                        object.fire()
                if enemyList.isEmpty():
                    self._changeStateCounter -= 1
                    if self._changeStateCounter <= 0 and isinstance(self._state, type(LevelOne())):
                        self._changeStateCounter = 240
                        self.changeState(LevelTwo())
                    elif self._changeStateCounter <= 0 and isinstance(self._state, type(LevelTwo())):
                        self._changeStateCounter = 240
                        self.changeState(LevelThree())
                    elif self._changeStateCounter <= 0 and isinstance(self._state, type(LevelThree())):
                        self._changeStateCounter = 240
                        self.changeState(LevelOne())

            for object in destroyedEnemies:
                highscore += object.getValue()
            
            self._iCounter += 1
            pygame.display.update()
            self._FramePerSec.tick(self._FPS)

class LevelState():
    def getData(self):
        pass

class LevelOne(LevelState):
    def __init__(self):
        self._bgPath = 'assets/graphics/other/space3.png'
        self._bgMusic = 'assets/music/bg/lvl1.ogg'
    def getData(self):
        return self._bgPath, self._bgMusic
    def spawner(self):
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        r = random.randint(0,10)
        if r <= 3:
            newEnem = Enemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E1.png',1,7,FlyStraight(),50)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
        elif r > 3 and r <= 6:
            newEnem = Enemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E2.png',2,3,FlyWavy(),70)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
        elif r > 6:
            newEnem = Enemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E3.png',1,5,FlyWavy(),80)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
    def bossSpawner(self):
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        boss = Boss((236,-127),(128,128),'assets/graphics/enemy/Boss1.png',25,5,FlySideways(),5000)
        boss.rotCenter(180)
        enemyList.addObject(boss)
        objectsList.addObject(boss)

class LevelTwo(LevelState):
    def __init__(self):
        self._bgPath = 'assets/graphics/other/space4.png'
        self._bgMusic = 'assets/music/bg/lvl2.ogg'
    def getData(self):
        return self._bgPath, self._bgMusic
    def spawner(self):
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        r = random.randint(0,10)
        if r <= 3:
            newEnem = BetterEnemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E4.png',2,8,FlyStraight(),80)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
        elif r > 3 and r <= 6:
            newEnem = Enemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E2.png',2,3,FlyWavy(),70)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
        elif r > 6:
            newEnem = Enemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E3.png',1,5,FlyWavy(),80)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
    def bossSpawner(self):
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        boss = Boss((236,-127),(128,128),'assets/graphics/enemy/Boss2.png',45,5,FlySideways(),10000)
        boss.rotCenter(180)
        enemyList.addObject(boss)
        objectsList.addObject(boss)

class LevelThree(LevelState):
    def __init__(self):
        self._bgPath = 'assets/graphics/other/space5.png'
        self._bgMusic = 'assets/music/bg/lvl3.ogg'
    def getData(self):
        return self._bgPath, self._bgMusic
    def spawner(self):
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        r = random.randint(0,10)
        if r <= 3:
            newEnem = BetterEnemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E4.png',2,8,FlyStraight(),80)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
        elif r > 3 and r <= 6:
            newEnem = BetterEnemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E5.png',4,3,FlyWavy(),90)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
        elif r > 6:
            newEnem = BetterEnemy((random.randint(16,584),0),(30,30),'assets/graphics/enemy/E6.png',2,5,FlyWavy(),100)
            newEnem.rotCenter(180)
            objectsList.addObject(newEnem)
            enemyList.addObject(newEnem)
    def bossSpawner(self):
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        boss = Boss((236,-127),(128,128),'assets/graphics/enemy/Boss3.png',55,5,FlySideways(),15000)
        enemyList.addObject(boss)
        objectsList.addObject(boss)

class GameEnd():
    def __init__(self, frame, player, highscore):
        player.removeObject(frame)
        self._gameEndTextFrame = frame + 120
        self._gameEndFrame = frame + 240
        self._font = pygame.font.SysFont("Verdana", 50)
        self._highscore = highscore
    def getGameEndFrame(self):
        return self._gameEndTextFrame, self._gameEndFrame
    def gameOver(self, frame):
        if self._gameEndTextFrame <= frame:
            gameOverText = self._font.render(str("Game Over"), True, (255,0,0))
            surface.blit(gameOverText, (170,300))
        if self._gameEndFrame <= frame:
            h = Highscores()
            h.afterGame(self._highscore)

class ScreenObject():
    def __init__(self, position, hitbox, spritePath):
        self._hitbox = pygame.Surface(hitbox)
        self._position = position
        self.rect = self._hitbox.get_rect(center = position)
        self._state = None
        self._sprite = pygame.transform.scale(pygame.image.load(spritePath), (32,32))
    def getPos(self):
        return self.rect
    def getSprite(self):
        return self._sprite
    def removeObject(self):
        objectsList = ObjectsList()
        objectsList.removeObject(self)
        

class PlayerShip(ScreenObject):
    def __init__(self, position, hitbox, spritePath):
        super().__init__(position, hitbox, spritePath)
        self._health = 3
        self._firestop = 0
        self._firecounter = 0
        self._iFrames = 0
        self._alive = 1
    def movement(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0:
            if pressed_keys[K_LEFT] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(-4, 0)
            elif pressed_keys[K_LEFT]:
                self.rect.move_ip(-8, 0)
        if self.rect.right < 584:  
            if pressed_keys[K_RIGHT] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(4, 0)      
            elif pressed_keys[K_RIGHT]:
                self.rect.move_ip(8, 0)
        if self.rect.top > 0: 
            if pressed_keys[K_UP] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(0, -4) 
            elif pressed_keys[K_UP]:
                self.rect.move_ip(0, -8)
        if self.rect.bottom < 800: 
            if pressed_keys[K_DOWN] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(0,4)
            elif pressed_keys[K_DOWN]:
                self.rect.move_ip(0,8)
    def fire(self):
        pressed_keys = pygame.key.get_pressed()
        if self._firestop == 0:
            if pressed_keys[K_z]:
                objectsList = ObjectsList()
                objectsBulletsList = ObjectsBulletsList()
                bullet = Bullet((self.rect.centerx+8,self.rect.centery),(8,8),"assets/graphics/other/bullet1.png",5,1)
                objectsList.addObject(bullet)
                objectsBulletsList.addObject(bullet)
                self._firestop = 1
                self._firecounter = 15
        elif self._firestop == 1:
            self._firecounter -= 1
            if self._firecounter == 0:
                self._firestop = 0
    def getFireStop(self):
        return self._firestop
    def removeObject(self, frame):
        self._alive = 0
        explosion = Debris((self.rect.centerx,self.rect.centery), (32,32), 'assets/graphics/animated/expl1.png', frame)
        debrisList = ObjectsDebrisList()
        objectsList = ObjectsList()
        debrisList.addObject(explosion)
        objectsList.addObject(explosion)
        objectsList.removeObject(self)
    def getIFrames(self):
        return self._iFrames
    def getHit(self):
        self._health -= 1
        self._iFrames = 180
        image = pygame.transform.scale(pygame.image.load("assets/graphics/other/invul.png"),(32,32))
        self._sprite.blit(image,(0,0))
    def getHealth(self):
        return self._health
    def decIFrames(self):
        self._iFrames -= 1
        if self._iFrames == 0:
            self._sprite = pygame.image.load('assets/graphics/player/P1.png')
    def getAlive(self):
        return self._alive
                

class Enemy(ScreenObject):
    def __init__(self, position, hitbox, spritePath, health, speed, state, value):
        super().__init__(position, hitbox, spritePath)
        self._health = health
        self._speed = speed
        self._state = state
        self._state.context = self
        self._offset = 5
        self._value = value
    def movement(self):
        self._state.movement()
    def rotCenter(self, angle):
        self._sprite = pygame.transform.rotate(self._sprite, angle)
        self.rect = self._sprite.get_rect(center=self.rect.center)
    def getHit(self, bullet, frame):
        self._health -= bullet.getDamage()
        if self._health <= 0:
            destroyed = ObjectsDestroyedList()
            destroyed.addObject(self)
            self.removeObject(frame)
    def removeObject(self, frame):
        explosion = Debris((self.rect.centerx,self.rect.centery), (32,32), 'assets/graphics/animated/expl1.png', frame)
        debrisList = ObjectsDebrisList()
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        debrisList.addObject(explosion)
        objectsList.addObject(explosion)
        enemyList.removeObject(self)
        objectsList.removeObject(self)
    def fire(self):
        pass
    def getValue(self):
        return self._value

class BetterEnemy(Enemy):
    def fire(self):
        r = random.uniform(0,10)
        if r < 0.1:
            objectsList = ObjectsList()
            enemyBulletsList = ObjectsEnemyBulletsList()
            bullet = EnemyBullet((self.rect.centerx+8,self.rect.centery),(8,8),"assets/graphics/other/bullet2.png",-5,1)
            objectsList.addObject(bullet)
            enemyBulletsList.addObject(bullet)

class EnemyState():
    def movement(self):
        pass

class FlyStraight(EnemyState):
    def movement(self):
        self.context.rect.move_ip(0,self.context._speed)  

class FlyWavy(EnemyState):
    def movement(self):
        initialPos = self.context._position[0]
        if (self.context.rect.centerx - initialPos) < -50: 
            self.context._offset = 5  
        elif (self.context.rect.centerx - initialPos) > 50:
            self.context._offset = -5
        self.context.rect.move_ip(self.context._offset,self.context._speed) 

class FlySideways(EnemyState):
    def movement(self):
        initialPos = self.context._position[0]
        if self.context.rect.centery < 200:
            self.context.rect.move_ip(0,self.context._speed) 
        else:
            if (self.context.rect.centerx - initialPos) < -200: 
                self.context._offset = 5  
            elif (self.context.rect.centerx - initialPos) > 200:
                self.context._offset = -5
            self.context.rect.move_ip(self.context._offset,0) 


class Boss(Enemy):
    def __init__(self, position, hitbox, spritePath, health, speed, state, value):
        self._hitbox = pygame.Surface(hitbox)
        self._position = position
        self.rect = self._hitbox.get_rect(center = position)
        self._sprite = pygame.transform.scale(pygame.image.load(spritePath), (128,128))
        self._health = health
        self._speed = speed
        self._state = state
        self._state.context = self
        self._offset = 5
        self._observer = None
        self._value = value
    def fire(self):
        objectsList = ObjectsList()
        enemyBulletsList = ObjectsEnemyBulletsList()
        bullet = EnemyBullet((self.rect.centerx+8,self.rect.centery),(8,8),"assets/graphics/other/bullet2.png",-5,1)
        bullet2 = DiagBulletLeft((self.rect.centerx+8,self.rect.centery),(8,8),"assets/graphics/other/bullet2.png",-5,1)
        bullet3 = DiagBulletRight((self.rect.centerx+8,self.rect.centery),(8,8),"assets/graphics/other/bullet2.png",-5,1)
        bullet2.rotCenter(-45)
        bullet3.rotCenter(45)
        objectsList.addObject(bullet)
        objectsList.addObject(bullet2)
        objectsList.addObject(bullet3)
        enemyBulletsList.addObject(bullet)
        enemyBulletsList.addObject(bullet2)
        enemyBulletsList.addObject(bullet3)
    def removeObject(self, frame):
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        enemyList.removeObject(self)
        objectsList.removeObject(self)
    
class Debris(ScreenObject):
    def __init__(self, position, hitbox, spritePath, frame):
        super().__init__(position, hitbox, spritePath)
        self._pathList = list(spritePath)
        self._frame = frame
        self._endFrame = frame + 80
        self._iCounter = 0
        a = animatedSprite()
        self._animated = a.animated(spritePath)
    def changeSprite(self, sprite):
        self._sprite = sprite
    def update(self, frame):
        if frame >= self._endFrame:
            self.removeObject(frame)
        else:
            self.changeSprite(pygame.transform.scale(self._animated[self._iCounter],(32,32)))
            self._iCounter += 1
    def movement(self):
        self.rect.move_ip(0,3)
    def removeObject(self, frame):
        objectsList = ObjectsList()
        debrisList = ObjectsDebrisList()
        debrisList.removeObject(self)
        objectsList.removeObject(self)
        
class Bullet(ScreenObject):
    def __init__(self, position, hitbox, spritePath, speed, damage):
        self._hitbox = pygame.Surface(hitbox)
        self._position = position
        self.rect = self._hitbox.get_rect(center = position)
        self._state = None
        self._sprite = pygame.transform.scale(pygame.image.load(spritePath), (8,8))
        self._speed = speed
        self._damage = damage
    def movement(self):
        #pass
        self.rect.move_ip(0,-self._speed)
    def removeObject(self, frame):
        objectsList = ObjectsList()
        bulletsList = ObjectsBulletsList()
        bulletsList.removeObject(self)
        objectsList.removeObject(self)
    def getDamage(self):
        return self._damage
    def rotCenter(self, angle):
        self._sprite = pygame.transform.rotate(self._sprite, angle)
        self.rect = self._sprite.get_rect(center=self.rect.center)

class EnemyBullet(Bullet):
    def removeObject(self, frame):
        objectsList = ObjectsList()
        enemyBulletsList = ObjectsEnemyBulletsList()
        enemyBulletsList.removeObject(self)
        objectsList.removeObject(self)

class DiagBulletLeft(EnemyBullet):
    def movement(self):
        self.rect.move_ip(-self._speed,-self._speed)

class DiagBulletRight(EnemyBullet):
    def movement(self):
        self.rect.move_ip(self._speed,-self._speed)


class ObjectsList(metaclass = Singleton):
    def __init__(self):
        self._objectsList = []
    def addObject(self, object):
        self._objectsList.append(object)
    def removeObject(self, object):
        self._objectsList.remove(object)
    def accessObject(self, index):
        return self._objectsList[index]
    def __iter__(self):
        return ObjectsListIterator(self)
    def size(self):
        return len(self._objectsList)
    def isEmpty(self):
        if len(self._objectsList) == 0:
            return True
        else:
            return False
    def clearList(self):
        self._objectsList = []

class ObjectsDebrisList(ObjectsList):
    pass

class ObjectsEnemyList(ObjectsList):
    pass

class ObjectsDestroyedList(ObjectsList):
    def clearList(self):
        self._objectsList = []

class ObjectsBulletsList(ObjectsList):
    pass

class ObjectsEnemyBulletsList(ObjectsList):
    pass

class ObjectsListIterator():
    def __init__(self, list):
        self._objectsList = list
        self._index = 0
    def __next__(self):
        if self._index < len(self._objectsList._objectsList):
            result =  self._objectsList._objectsList[self._index]
            self._index += 1
            return result
        raise StopIteration

class Background():
      def __init__(self, path):
            self.bgimage = pygame.image.load(path)
            self.rectBGimg = self.bgimage.get_rect()
 
            self.bgY1 = self.rectBGimg.height
            self.bgX1 = 0
 
            self.bgY2 = 0
            self.bgX2 = 0
 
            self.moving_speed = 3
         
      def update(self):
        self.bgY1 += self.moving_speed
        self.bgY2 += self.moving_speed
        if self.bgY1 >= self.rectBGimg.height:
            self.bgY1 = -self.rectBGimg.height
        if self.bgY2 >= self.rectBGimg.height:
            self.bgY2 = -self.rectBGimg.height
             
      def render(self):
         surface.blit(self.bgimage, (self.bgX1, self.bgY1))
         surface.blit(self.bgimage, (self.bgX2, self.bgY2))

class animatedSprite():
    def animated(self, path):
        self._pathList = list(path)
        self._list = []
        for i in range(0,8):
            self._pathList[29] = str(1+i)
            image = pygame.image.load("".join(self._pathList))
            self._list.append(image)
        return self._list

class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        font = pygame.font.SysFont("Verdana", 30)
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                font = pygame.font.SysFont("Verdana", 30)
                self.txt_surface = font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class main(metaclass = Singleton):
    game = Game()
    game.menuInit()

    