import pygame
import random
import sys
from multiprocessing import Process
from camera_tracker import camera_process, game_process, delta_x, delta_y, jump_threshold

def run():
    class gameObj:
        def __init__(self, x, y, width, height, imgPath):
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
            new_image = pygame.image.load(imgPath)
            self.image = pygame.transform.scale(new_image, (self.width, self.height))

    # --- GAME SETUP ---
    isRunning = True
    isJumping = False
    jumpSpeed = 0
    playerSpeed = 10
    gravity = 0.6
    groundHeight = 700
    bgColor = (97, 86, 180)

    player = gameObj(400, 800, 100, 100, "pygame/idle.png")

    # Platforms
    platforms = []
    numPlatforms = 4
    for i in range(numPlatforms):
        platX = random.randint(100, 400)
        platY = random.randint(100, 700)
        if i > 0:
            while any(abs(platX - p.rect.x) <= 125 or abs(platY - p.rect.y) <= 125 for p in platforms):
                platX = random.randint(100, 700)
                platY = random.randint(100, 700)
        platforms.append(gameObj(platX, platY, 200, 50, "pygame/platform.png"))

    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Raccoon Jumper")
    clock = pygame.time.Clock()

    thresholdUp = 300
    thresholdDown = 500
    minSpacing = 100
    maxSpacing = 200

    def endGame():
        nonlocal isRunning
        isRunning = False
        pygame.quit()
        sys.exit()

    # --- GAME LOOP ---
    while isRunning:
        screen.fill(bgColor)
        player.draw(screen)
        for plat in platforms:
            plat.draw(screen)

        # --- EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                endGame()

        # --- CAMERA-BASED MOVEMENT ---
        # Jumping
        if delta_y.value > jump_threshold and not isJumping:
            jumpSpeed = -20
            isJumping = True
            player.changeSprite("pygame/jump.png")

        # Horizontal movement
        if delta_x.value > 8:
            player.rect.x = min(player.rect.x + playerSpeed, 700)
            player.changeSprite("pygame/right.png")
        elif delta_x.value < -8:
            player.rect.x = max(player.rect.x - playerSpeed, 0)
            player.changeSprite("pygame/left.png")
        elif not isJumping:  # idle when not moving horizontally or jumping
            player.changeSprite("pygame/idle.png")

        # --- PHYSICS ---
        player.rect.y += jumpSpeed
        jumpSpeed += gravity

        onPlat = False
        for plat in platforms:
            if jumpSpeed >= 0 and player.rect.colliderect(plat.rect) and player.rect.bottom <= plat.rect.top + jumpSpeed:
                player.rect.bottom = plat.rect.top
                jumpSpeed = 0
                onPlat = True
                player.changeSprite("pygame/idle.png")
                break

        if player.rect.y >= groundHeight:
            player.rect.y = groundHeight
            jumpSpeed = 0
            onPlat = True
            player.changeSprite("pygame/idle.png")

        isJumping = not onPlat

        # --- SCROLLING ---
        scrollAmount = 0
        if not onPlat:
            if player.rect.y < thresholdUp:
                scrollAmount = thresholdUp - player.rect.y
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
                plat.rect.y = highestY - random.randint(minSpacing, maxSpacing)
                highestY = plat.rect.y
            elif plat.rect.y < -100:
                plat.rect.x = random.randint(100, 400)
                plat.rect.y = lowestY + random.randint(minSpacing, maxSpacing)
                lowestY = plat.rect.y

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    # Start camera processes
    p1 = Process(target=camera_process, args=(delta_x, delta_y))
    p2 = Process(target=game_process, args=(delta_x, delta_y))
    p1.start()
    p2.start()

    # Start the Pygame game
    pygame.init()
    run()

    # Join camera processes
    p1.join()
    p2.join()