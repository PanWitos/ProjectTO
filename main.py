import pygame
import pygame_menu
import sys
from pygame.locals import *
import random, time

surface = pygame.display.set_mode((600,800))

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Game(metaclass = Singleton):
    def __init__(self):
        pygame.init()
        self._highscore = {}
    def startGame(self):
        GameLoop()
    def highscoreTable(self):
        print("siema eniu")
    def menuInit(self):
        self._menu = Menu()
        menuData = self._menu.menuInit()
        menuData.mainloop(surface)     

class Menu():
    def __init__(self):
        self._size = (400,600)
        self._game = Game()
    def menuInit(self):
        menu = pygame_menu.Menu('Welcome', self._size[0], self._size[1], theme=pygame_menu.themes.THEME_BLUE)
        menu.add.button('Play', self._game.startGame)
        menu.add.button('Highscores', self._game.highscoreTable)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        return menu

class GameLoop():
    def __init__(self):
        self._list = ObjectsList()
        self._state = None
        self._bg = Background('assets/graphics/other/space3.png')
        self._FPS = 60
        surface.fill((255, 255, 255))
        self._FramePerSec = pygame.time.Clock()
        self._font_small = pygame.font.SysFont("Verdana", 20)
        pygame.display.set_caption("Game")
        self._iCounter = 0
        self._dt = 10
        self.gameLoop()
    def gameLoop(self):
        objectsList = ObjectsList()
        debrisList = ObjectsDebrisList()
        player = PlayerShip((300,600),(15,15),'assets/graphics/player/P1.png')
        enemy = Enemy((300,200),(25,25),'assets/graphics/enemy/E1.png',1, 5)
        enemy2 = Enemy((200,200),(25,25),'assets/graphics/enemy/E1.png',2, 5)
        enemy3 = Enemy((400,200),(25,25),'assets/graphics/enemy/E1.png',3, 5)
        enemyList = ObjectsEnemyList()
        enemyList.addObject(enemy)
        enemyList.addObject(enemy2)
        enemyList.addObject(enemy3)
        objectsList.addObject(player)
        objectsList.addObject(enemy)
        objectsList.addObject(enemy2)
        objectsList.addObject(enemy3)
        for enem in enemyList:
            enem.rotCenter(180)
        while True:
            for event in pygame.event.get():    
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self._bg.update()
            self._bg.render()

            scores = self._font_small.render(str(self._iCounter), True, (255,255,255))
            surface.blit(scores, (10,10))

            for object in objectsList:
                surface.blit(object.getSprite(), object.getPos())
                object.movement()
            
            if pygame.sprite.spritecollideany(player, enemyList):
                e1 = pygame.sprite.spritecollideany(player, enemyList)
                e1.removeObject(self._iCounter)

            if (self._iCounter % self._dt)==0:
                for object in debrisList:
                    object.update(self._iCounter)

            self._iCounter += 1
            pygame.display.update()
            self._FramePerSec.tick(self._FPS)

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
    def removeObject(self, frame):
        objectsList = ObjectsList()
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
            print("exploded")
            self.removeObject(frame)
        else:
            self.changeSprite(pygame.transform.scale(self._animated[self._iCounter],(32,32)))
            self._iCounter += 1
    def movement(self):
        pass
    def removeObject(self, frame):
        objectsList = ObjectsList()
        debrisList = ObjectsDebrisList()
        debrisList.removeObject(self)
        objectsList.removeObject(self)


class PlayerShip(ScreenObject):
    def __init__(self, position, hitbox, spritePath):
        super().__init__(position, hitbox, spritePath)
        self._health = 10
    def movement(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0:
            if pressed_keys[K_LEFT] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(-4, 0)
            elif pressed_keys[K_LEFT]:
                self.rect.move_ip(-8, 0)
        if self.rect.right < 600:  
            if pressed_keys[K_RIGHT] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(4, 0)      
            elif pressed_keys[K_RIGHT]:
                self.rect.move_ip(8, 0)
        if self.rect.top > 0: 
            if pressed_keys[K_UP] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(0, -4) 
            elif pressed_keys[K_UP]:
                self.rect.move_ip(0, -8)
        if self.rect.bottom < 700: 
            if pressed_keys[K_DOWN] and pressed_keys[K_LSHIFT]:
                self.rect.move_ip(0,4)
            elif pressed_keys[K_DOWN]:
                self.rect.move_ip(0,8)

class Enemy(ScreenObject):
    def __init__(self, position, hitbox, spritePath, health, speed):
        super().__init__(position, hitbox, spritePath)
        self.health = health
        self._speed = speed
    def movement(self):
        pass
        #self.rect.move_ip(0,self._speed)
    def rotCenter(self, angle):
        self._sprite = pygame.transform.rotate(self._sprite, angle)
        self.rect = self._sprite.get_rect(center=self.rect.center)
    def removeObject(self, frame):
        explosion = Debris(self._position, (32,32), 'assets/graphics/animated/expl1.png', frame)
        debrisList = ObjectsDebrisList()
        objectsList = ObjectsList()
        enemyList = ObjectsEnemyList()
        debrisList.addObject(explosion)
        objectsList.addObject(explosion)
        enemyList.removeObject(self)
        objectsList.removeObject(self)

class Bullet(ScreenObject):
    def __init__(self, position, hitbox, spritePath):
        super().__init__(position, hitbox, spritePath)

class ObjectsList(metaclass = Singleton):
    def __init__(self):
        self._objectsList = []
    def addObject(self, object):
        self._objectsList.append(object)
    def removeObject(self, object):
        self._objectsList.remove(object)
    def __iter__(self):
        return ObjectsListIterator(self)

class ObjectsDebrisList(metaclass = Singleton):
    def __init__(self):
        self._objectsList = []
    def addObject(self, object):
        self._objectsList.append(object)
    def removeObject(self, object):
        self._objectsList.remove(object)
    def __iter__(self):
        return ObjectsListIterator(self)

class ObjectsEnemyList(metaclass = Singleton):
    def __init__(self):
        self._objectsList = []
    def addObject(self, object):
        self._objectsList.append(object)
    def removeObject(self, object):
        self._objectsList.remove(object)
    def __iter__(self):
        return ObjectsListIterator(self)

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


class main(metaclass = Singleton):
    game = Game()
    game.menuInit()

    