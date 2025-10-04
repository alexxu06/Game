import pygame

import random
import time
import sys

if __name__ == "__main__":
    pygame.init()
    
isRunning = True
isJumping = False
jumpSpeed = 0
gravity = 0.6
groundHeight = 700
bgColor = (97, 86, 180)

playerImg = pygame.image.load("pygame\guy.jpg")
playerX = 400
playerY = groundHeight
player = pygame.transform.scale(playerImg, (100,100))

platformImg = pygame.image.load("pygame\platform.jpg")


screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("jumping game")
clock = pygame.time.Clock()

def setPlayer(x, y):
    screen.blit(player,(x, y))

def endGame():
    global isRunning
    isRunning = False
    sys.exit()
    pygame.quit
    
    
    


while isRunning:
    screen.fill(bgColor)
    setPlayer(playerX, playerY)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            endGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not isJumping:
                isJumping = True
                jumpSpeed = -20
                
    if isJumping:
        playerY += jumpSpeed
        jumpSpeed += gravity
        
        if playerY >= groundHeight:
            playerY = groundHeight
            isJumping = False
            
    pygame.display.update()
    clock.tick(60)
    
    
pygame.quit()
sys.quit()