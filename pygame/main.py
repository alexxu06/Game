import pygame

import random
import time
import sys
import math

if __name__ == "__main__":
    pygame.init()
    
class gameObj:
    def __init__(self,x, y, width, height, imgPath):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.image = pygame.image.load(imgPath)
        self.image = pygame.transform.scale(self.image, (width, height))
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
    
isRunning = True
isJumping = False
jumpSpeed = 0
playerSpeed = 10
gravity = 0.6
groundHeight = 700
bgColor = (97, 86, 180)

player = gameObj(400, 700, 100, 100, "pygame/guy.jpg")

platforms = []
platformX = []
platformY = []
numPlatforms = 5

Xmax = 400
Xmin = 100

for i in range(numPlatforms):
    platformX.append(random.randint(Xmin, Xmax))
    Xmax+=100
    Xmin+=100
    platformY.append(random.randint(100, 700))
    
    if i > 0:
        while abs(platformX[i] - platformX[i-1]) <= 100 or abs(platformY[i] - platformY[i-1]) <= 100:
            platformX[i] = random.randint(200, 750)
            platformY[i] = random.randint(100, 700)

for i in range(numPlatforms):
    plat = gameObj(platformX[i], platformY[i], 200, 50, "pygame/platform.png")
    platforms.append(plat)
    
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("jumping game")
clock = pygame.time.Clock()

def setPlayer(x, y):
    screen.blit(player,(x, y))

def setPlatforms(x, y, i):
    screen.blit(platforms[i], (x, y))
    
def endGame():
    global isRunning
    isRunning = False
    pygame.quit()
    sys.exit()
    
def hasCollided(player, platforms):
    standingOn = True
    for plat in platforms:
        if player.rect.bottom <= plat.rect.top + 10 and \
           player.rect.bottom >= plat.rect.top - 10 and \
           player.rect.right > plat.rect.left and player.rect.left < plat.rect.right:
               standingOn = plat
               player.rect.bottom = plat.rect.top
               break
    return standingOn
    
while isRunning:
    screen.fill(bgColor)
    player.draw(screen)
    
    for i in range(numPlatforms):
        platforms[i].draw(screen)
        #if hasCollided(player, platforms, jumpSpeed):
            #print("HIT")
        
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            endGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not isJumping:
                isJumping = True
                jumpSpeed = -20
    
    standingOn = hasCollided(player, platforms)
    
    if standingOn is None and player.rect.bottom < groundHeight:
        player.rect.y += jumpSpeed
        jumpSpeed+= gravity
        isJumping = True
    else:
        isJumping = False
        jumpSpeed = 0
        
    if player.rect.bottom >= groundHeight:
        player.rect.bottom = groundHeight
        isJumping = False
        jumpSpeed = 0
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if player.rect.x > 0:
            player.rect.x-=playerSpeed
    if keys[pygame.K_RIGHT]:
        if player.rect.x < 700:
            player.rect.x+=playerSpeed
    
    if isJumping:
        player.rect.y += jumpSpeed
        jumpSpeed += gravity
    
        
        if player.rect.y >= groundHeight:
            player.rect.y = groundHeight
            isJumping = False
    
  
            
    pygame.display.update()
    clock.tick(60)
    
endGame()