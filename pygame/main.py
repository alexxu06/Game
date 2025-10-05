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
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    PLAYER_SPEED = 10
    GRAVITY = 0.6

    class gameObj:
        def __init__(self, x, y, width, height, imgPath, yOffset=0):
            self.width = width
            self.height = height
            self.image = pygame.image.load(imgPath)
            self.image = pygame.transform.scale(self.image, (width, height))
            self.rect = pygame.Rect(x, y - yOffset, width, height)
            self.yOffset = yOffset

        def draw(self, surface, camera_y):
            surface.blit(self.image, (self.rect.x, self.rect.y - camera_y))

        def changeSprite(self, imgPath, yOffset=None):
            self.image = pygame.image.load(imgPath)
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            if yOffset is not None:
                self.rect.y -= (yOffset - self.yOffset)
                self.yOffset = yOffset

    # Load background (do NOT scale)
    background = pygame.image.load("pygame/real_background.png")
    BG_WIDTH, BG_HEIGHT = background.get_width(), background.get_height()

    # Camera offset (start at bottom)
    camera_y = BG_HEIGHT - SCREEN_HEIGHT

    # Initialize player at the bottom of the image
    player = gameObj(400, BG_HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, "pygame/idle.png", yOffset=0)

    # Initialize platforms near the bottom
    numPlatforms = 4
    platforms = []
    platformX = []
    platformY = []

    for i in range(numPlatforms):
        platformX.append(random.randint(100, 400))
        platformY.append(random.randint(BG_HEIGHT - 700, BG_HEIGHT - 100))
        if i > 0:
            while abs(platformX[i] - platformX[i - 1]) <= 125 or abs(platformY[i] - platformY[i - 1]) <= 125:
                platformX[i] = random.randint(200, 750)
                platformY[i] = random.randint(BG_HEIGHT - 700, BG_HEIGHT - 100)

    for i in range(numPlatforms):
        plat = gameObj(platformX[i], platformY[i], PLATFORM_WIDTH, PLATFORM_HEIGHT, "pygame/platform.png")
        platforms.append(plat)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Raccoon Jumper")
    clock = pygame.time.Clock()

    isRunning = True
    isJumping = False
    jumpSpeed = 0

    def endGame():
        nonlocal isRunning
        isRunning = False
        pygame.quit()
        sys.exit()

    while isRunning:
        # Draw background with camera offset
        screen.blit(background, (0, -camera_y))

        # Draw player and platforms with camera offset
        player.draw(screen, camera_y)
        for plat in platforms:
            plat.draw(screen, camera_y)

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
        if player.rect.y >= BG_HEIGHT - PLAYER_HEIGHT:
            player.rect.y = BG_HEIGHT - PLAYER_HEIGHT
            jumpSpeed = 0
            onPlat = True
            player.changeSprite("pygame/idle.png", yOffset=0)

        isJumping = not onPlat

        # Update camera position based on player
        camera_y = max(0, min(BG_HEIGHT - SCREEN_HEIGHT, player.rect.y - SCREEN_HEIGHT // 2))

        # Recycle platforms for infinite generation as you scroll up/down
        minSpacing, maxSpacing = 100, 200
        highestY = min(p.rect.y for p in platforms)
        lowestY = max(p.rect.y for p in platforms)

        for plat in platforms:
            # If platform goes off the bottom of the visible screen, move it above the highest platform
            if plat.rect.y - camera_y > SCREEN_HEIGHT:
                plat.rect.x = random.randint(100, 600)
                plat.rect.y = highestY - random.randint(minSpacing, maxSpacing)
            # If platform goes off the top of the visible screen, move it below the lowest platform
            elif plat.rect.y - camera_y < -PLATFORM_HEIGHT:
                plat.rect.x = random.randint(100, 600)
                plat.rect.y = lowestY + random.randint(minSpacing, maxSpacing)

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    # Start camera processes AFTER initializing pygame
    p1 = Process(target=camera_process, args=(delta_x, delta_y), daemon=True)
    p2 = Process(target=game_process, args=(delta_x, delta_y), daemon=True)
    p1.start()
    p2.start()
    run()