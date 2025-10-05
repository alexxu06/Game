import pygame
import random
import sys
from multiprocessing import Process
from camera_tracker import camera_process, game_process, delta_x, delta_y, jump_threshold

def run():
    # Constants
    PLAYER_WIDTH = 100
    PLAYER_HEIGHT = 100
    PLATFORM_WIDTH = 200
    PLATFORM_HEIGHT = 50
    GROUND_HEIGHT = 700
    PLAYER_SPEED = 10
    GRAVITY = 0.6
    THRESHOLD_UP = 300
    THRESHOLD_DOWN = 500

    class gameObj:
        def __init__(self, x, y, width, height, imgPath, yOffset=0):
            self.width = width
            self.height = height
            self.image = pygame.image.load(imgPath)
            self.image = pygame.transform.scale(self.image, (width, height))
            self.rect = pygame.Rect(x, y - yOffset, width, height)
            self.yOffset = yOffset

        def draw(self, surface):
            surface.blit(self.image, (self.rect.x, self.rect.y))

        def changeSprite(self, imgPath, yOffset=None):
            self.image = pygame.image.load(imgPath)
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            if yOffset is not None:
                self.rect.y -= (yOffset - self.yOffset)
                self.yOffset = yOffset

    # Initialize player
    player = gameObj(400, 800, PLAYER_WIDTH, PLAYER_HEIGHT, "pygame/idle.png", yOffset=0)

    # Initialize platforms
    numPlatforms = 4
    platforms = []
    platformX = []
    platformY = []

    bgImgs = [
        pygame.transform.scale((pygame.image.load("pygame/bg1.png")), (800, 800)),
        pygame.transform.scale((pygame.image.load("pygame/bg2.png")), (800, 800)),
        pygame.transform.scale((pygame.image.load("pygame/bg3.png")), (800, 800)),
        pygame.transform.scale((pygame.image.load("pygame/bg4.png")), (800, 800))   
    ]
    for i in range(numPlatforms):
        platformX.append(random.randint(100, 400))
        platformY.append(random.randint(100, 700))
        if i > 0:
            while abs(platformX[i] - platformX[i - 1]) <= 125 or abs(platformY[i] - platformY[i - 1]) <= 125:
                platformX[i] = random.randint(200, 750)
                platformY[i] = random.randint(100, 700)

    for i in range(numPlatforms):
        plat = gameObj(platformX[i], platformY[i], PLATFORM_WIDTH, PLATFORM_HEIGHT, "pygame/platform.png")
        platforms.append(plat)

    # Pygame setup
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Raccoon Jumper")
    clock = pygame.time.Clock()
    bgColor = (97, 86, 180)

    isRunning = True
    isJumping = False
    currBg = bgImgs[0]
    jumpSpeed = 0
    totalScroll = 0

    def endGame():
        nonlocal isRunning
        isRunning = False
        pygame.quit()
        sys.exit()

    while isRunning:
        screen.blit(currBg, (0, 0))
        player.draw(screen)
        for plat in platforms:
            plat.draw(screen)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                endGame()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not isJumping:
                    jumpSpeed = -20
                    isJumping = True
                    player.changeSprite("pygame/jump.png", yOffset=0)

        # Camera-based jump
        if delta_y.value > jump_threshold and not isJumping:
            jumpSpeed = -20
            isJumping = True
            player.changeSprite("pygame/jump.png", yOffset=0)

        # Camera-based left/right movement
        if delta_x.value > 8:
            if player.rect.x < 700:
                player.rect.x += PLAYER_SPEED
                if not isJumping:
                    player.changeSprite("pygame/right.png", yOffset=0)
        elif delta_x.value < -8:
            if player.rect.x > 0:
                player.rect.x -= PLAYER_SPEED
                if not isJumping:
                    player.changeSprite("pygame/left.png", yOffset=0)
        elif not isJumping:
            player.changeSprite("pygame/idle.png", yOffset=0)

        # Apply gravity
        player.rect.y += jumpSpeed
        jumpSpeed += GRAVITY

        # Check collision with platforms
        onPlat = False
        for plat in platforms:
            if jumpSpeed >= 0 and player.rect.colliderect(plat.rect):
                if player.rect.bottom <= plat.rect.top + jumpSpeed:
                    player.rect.bottom = plat.rect.top
                    jumpSpeed = 0
                    onPlat = True
                    player.changeSprite("pygame/idle.png", yOffset=0)
                    break

        # Check ground
        if player.rect.y >= GROUND_HEIGHT:
            player.rect.y = GROUND_HEIGHT
            jumpSpeed = 0
            onPlat = True
            player.changeSprite("pygame/idle.png", yOffset=0)

        isJumping = not onPlat

        # Screen scrolling
        scrollAmount = 0
        if not onPlat:
            if player.rect.y < THRESHOLD_UP:
                scrollAmount = THRESHOLD_UP - player.rect.y
                player.rect.y = THRESHOLD_UP
            elif player.rect.y > THRESHOLD_DOWN:
                scrollAmount = THRESHOLD_DOWN - player.rect.y
                player.rect.y = THRESHOLD_DOWN

        totalScroll += scrollAmount
        if totalScroll >= 300 and totalScroll < 600:
            currBg = bgImgs[1]
        if totalScroll >=600 and totalScroll < 900:
            currBg = bgImgs[2]
        if totalScroll >=900:
            currBg = bgImgs[3]
            
        screen.blit(currBg, (0, 0))
        
        for plat in platforms:
            plat.rect.y += scrollAmount

        # Recycle platforms
        minSpacing, maxSpacing = 100, 200
        highestY = min(p.rect.y for p in platforms)
        lowestY = max(p.rect.y for p in platforms)

        for plat in platforms:
            if plat.rect.y > 800:
                plat.rect.x = random.randint(100, 400)
                plat.rect.y = highestY - random.randint(minSpacing, maxSpacing)
                highestY = plat.rect.y
            elif plat.rect.y < -100:
                plat.rect.x = random.randint(100, 400)
                plat.rect.y = lowestY + random.randint(minSpacing, maxSpacing)
                lowestY = plat.rect.y

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    # Start camera processes AFTER initializidng pygame
    p1 = Process(target=camera_process, args=(delta_x, delta_y), daemon=True)
    p2 = Process(target=game_process, args=(delta_x, delta_y), daemon=True)
    p1.start()
    p2.start()
    run()
    # Processes will terminate automatically with daemon=True