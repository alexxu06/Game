import pygame

import random
import time
import sys
import math

from multiprocessing import Process
from camera_tracker import camera_process, game_process, delta_x, delta_y, jump_threshold

def run():
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
            
        def changeSprite(self, imgPath):
            self.image = pygame.image.load(imgPath)
            self.image = pygame.transform.scale(self.image,(self.width, self.height))
        
    isRunning = True
    isJumping = False
    jumpSpeed = 0
    playerSpeed = 10
    gravity = 0.6
    groundHeight = 700
    bgColor = (97, 86, 180)

    player = gameObj(400, 800, 100, 100, "pygame/idle.png")

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
        
    def endGame():
        global isRunning
        isRunning = False
        pygame.quit()
        sys.exit()
        

    thresholdUp = 300
    thresholdDown = 500
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


        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     if player.rect.x > 0:
        #         player.rect.x-=playerSpeed
        # if keys[pygame.K_RIGHT]:
        #     if player.rect.x < 700:
        #         player.rect.x+=playerSpeed
    # Camera-based left/right
        # Camera-based jump
        player.changeSprite("pygame/idle.png")
        if delta_y.value > jump_threshold and not isJumping:
            isJumping = True
            jumpSpeed = -20
            player.changeSprite("pygame/jump.png")

        # Camera-based left/right
        if delta_x.value > 8:
            if player.rect.x < 700:
                player.rect.x += playerSpeed
                player.changeSprite("pygame/right.png")
        elif delta_x.value < -8:
            if player.rect.x > 0:
                player.rect.x -= playerSpeed
                player.changeSprite("pygame/left.png")
        
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
        scrollAmount = 0
        
        if not onPlat:
            if player.rect.y < thresholdUp:
                scrollAmount =  thresholdUp - player.rect.y
                player.rect.y = thresholdUp
            elif player.rect.y > thresholdDown:
                scrollAmount = thresholdDown - player.rect.y
                player.rect.y = thresholdDown
            
        
        for plat in platforms:
            plat.rect.y += scrollAmount
            
        highestY = min(p.rect.y for p in platforms)
        lowestY = max(p.rect.y for p in platforms)
        for plat in platforms:
            if plat.rect.y > 800:
                plat.rect.x = random.randint(100, 400)
                plat.rect.y = highestY -random.randint(minSpacing, maxSpacing)
                highestY = plat.rect.y
            elif plat.rect.y < -100:
                plat.rect.x = random.randint(100, 400)
                plat.rect.y = lowestY + random.randint(minSpacing, maxSpacing)
                lowestY = plat.rect.y


        pygame.display.update()
        clock.tick(60)
        if onPlat:
            player.changeSprite("pygame/idle.png")
        else:
              player.changeSprite("pygame/jump.png")
        
    endGame()

if __name__ == "__main__":
    p1 = Process(target=camera_process, args=(delta_y, delta_y))
    p2 = Process(target=game_process, args=(delta_x, delta_y))
    p1.start()
    p2.start()
    pygame.init()
    run() 
    p1.join()
    p2.join()