import pygame
import pygame_menu
import sys
from pygame.locals import *
import random, time

surface = pygame.display.set_mode((600,700))

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
        

class Menu:
    def __init__(self):
        self._size = (400,600)
        self._game = Game()
    def menuInit(self):
        menu = pygame_menu.Menu('Welcome', self._size[0], self._size[1], theme=pygame_menu.themes.THEME_BLUE)
        menu.add.button('Play', self._game.startGame)
        menu.add.button('Highscores', self._game.highscoreTable)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        return menu

class GameLoop:
    def __init__(self):
        self._list = ObjectsList()
        self._state = None
        self._bg = Background()
        self.FPS = 60
        surface.fill((255, 255, 255))
        pygame.display.set_caption("Game")
        self.FramePerSec = pygame.time.Clock()
        self.gameLoop()
    def gameLoop(self):
        player = PlayerShip((200,200),(30,30),'assets/P1.png')
        while True:
            for event in pygame.event.get():    
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self._bg.update()
            self._bg.render()
            surface.blit(player.getSprite(), player.getPos())
            player.movement()
            pygame.display.update()
            self.FramePerSec.tick(self.FPS)

class ScreenObject:
    def __init__(self, position, hitbox, spritePath):
        self._hitbox = pygame.Surface(hitbox)
        self._pos = self._hitbox.get_rect(center = position)
        self._state = None
        self._sprite = pygame.image.load(spritePath)
    def getPos(self):
        return self._pos
    def getSprite(self):
        return self._sprite

class Debris(ScreenObject):
    def __init__(self, position, hitbox, spritePath):
        super().__init__(position, hitbox, spritePath)
        self._speed = 5

class PlayerShip(ScreenObject):
    def __init__(self, position, hitbox, spritePath):
        super().__init__(position, hitbox, spritePath)
        self._health=10
    def movement(self):
        pressed_keys = pygame.key.get_pressed()
        if self._pos.left > 0:
            if pressed_keys[K_LEFT]:
                self._pos.move_ip(-5, 0)
        if self._pos.right < 600:        
            if pressed_keys[K_RIGHT]:
                self._pos.move_ip(5, 0)
        if pressed_keys[K_UP]:
            self._pos.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self._pos.move_ip(0,5)

class ObjectsList(metaclass = Singleton):
    def __init__(self):
        self._objectsList = []
    def addObject(self, object):
        self._objectsList.append(object)
        
    def removeObject(self, object):
        self._objectsList.remove(object)

class Background():
      def __init__(self):
            self.bgimage = pygame.image.load('assets/space.png')
            self.rectBGimg = self.bgimage.get_rect()
 
            self.bgY1 = self.rectBGimg.height
            self.bgX1 = 0
 
            self.bgY2 = 0
            self.bgX2 = 0
 
            self.moving_speed = 5
         
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

class main(metaclass = Singleton):
    game = Game()
    game.menuInit()

    