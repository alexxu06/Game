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

player = gameObj(400, 750, 100, 100, "pygame/idle.png")

platforms = []
platformX = []
platformY = []
numPlatforms = 4


for i in range(numPlatforms):
    platformX.append(random.randint(100, 400))
    platformY.append(random.randint(100, 700))
    
    if i > 0:
        while abs(platformX[i] - platformX[i-1]) <= 125 or abs(platformY[i] - platformY[i-1]) <= 125:
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
    
def hasCollided(player, platforms, jumpspeed):
    for plat in platforms:
        if player.rect.colliderect(plat.rect) and jumpspeed > 0:
            player.rect.bottom = plat.rect.top
            return True
    
    return False

threshold = 300
scrollSpeed = 10
while isRunning:
    screen.fill(bgColor)
    player.draw(screen)
    
    for i in range(numPlatforms):
        platforms[i].draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            endGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not isJumping:
                isJumping = True
                jumpSpeed = -20
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if player.rect.x > 0:
            player.rect.x-=playerSpeed
    if keys[pygame.K_RIGHT]:
        if player.rect.x < 700:
            player.rect.x+=playerSpeed
    
    player.rect.y += jumpSpeed
    jumpSpeed += gravity
    
    onPlat = False
    
    for plat in platforms:
        if jumpSpeed >= 0:
            if player.rect.bottom <= plat.rect.top + jumpSpeed and player.rect.colliderect(plat.rect):
                player.rect.bottom = plat.rect.top
                jumpSpeed = 0
                onPlat = True
                break
    if player.rect.y >= groundHeight:
        player.rect.y = groundHeight
        jumpSpeed = 0
        onPlat = True
    
    isJumping = not onPlat
    minSpacing = 100
    maxSpacing = 200
    if player.rect.y < threshold:
        scrollAmount =  threshold - player.rect.y
        player.rect.y = threshold
        for plat in platforms:
            plat.rect.y += scrollAmount
        highestY = min(p.rect.y for p in platforms)
        for plat in platforms:
            if plat.rect.y > 800:
                platformX.append(random.randint(100, 400))
                plat.rect.y = highestY -random.randint(minSpacing, maxSpacing)
                highestY = plat.rect.y
  
    pygame.display.update()
    clock.tick(60)
    
endGame()