import pygame
import random
import os
import sys
from pygame import mixer
from pygame.locals import (
    KEYDOWN,
    K_ESCAPE,
    K_SPACE,
    K_LEFT,
    K_RIGHT
)

pygame.init()

WIDTH = 853
HEIGHT = 480

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 105, 180)
GREY = (128, 128, 128)

ALLCOLORS = [WHITE, RED, GREEN, 'yellow', PINK, 'orange']
playerColor = 0

currColor = (55, 65, 252)
secondaryColor = (48, 51, 217)
spikeColor = (38, 41, 207)

SCORE = 0
HIGHSCORE = 0

SPEEDMULTIPLIER = 0.005
SPIKESPEED = 6

screen = pygame.display.set_mode([WIDTH, HEIGHT])

# Set up file directory stuff
APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0]))
FONT_DIR = os.path.join(APP_FOLDER, "assets/Montserrat-Regular.ttf")
JUMP_DIR = os.path.join(APP_FOLDER, "assets/jump.mp3")
DEATH_DIR = os.path.join(APP_FOLDER, "assets/death.mp3")
MUSIC_DIR = os.path.join(APP_FOLDER, "assets/music.mp3")

# Set up mixer and sounds
mixer.init()

music = pygame.mixer.music.load(MUSIC_DIR)
pygame.mixer.music.play(-1)  # -1 will loop the song
pygame.mixer.music.set_volume(0.01)


jump = pygame.mixer.Sound(JUMP_DIR)
# it's not actually dying, just taking a quick breather, dying is too violent
die = pygame.mixer.Sound(DEATH_DIR)
jump.set_volume(0.1)
die.set_volume(0.3)

# Classes
colliding = False
gravityChanging = False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill(ALLCOLORS[playerColor])
        self.rect = self.surf.get_rect(topleft=(50, HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.surf)

        # print(self.mask.count())

        self.yvel = 0
        self.gravityDown = True

    def update(self, pressed):
        if self.yvel > 15:
            self.yvel = 15
        if self.yvel < -15:
            self.yvel = -15

        if not colliding:
            if self.gravityDown:
                self.yvel += 1
            else:
                self.yvel -= 1

            self.rect.move_ip(0, self.yvel)
        if pressed[K_SPACE] and colliding:
            if self.gravityDown:
                self.yvel -= 15
            else:
                self.yvel += 15

            self.rect.move_ip(0, self.yvel)
        elif colliding:
            self.yvel = 0

    def gravitySwitch(self):
        global gravityChanging
        gravityChanging = True
        self.gravityDown = not self.gravityDown

    def changeColor(self):
        self.surf.fill(ALLCOLORS[playerColor])


class Platform(pygame.sprite.Sprite):
    def __init__(self, position):
        super(Platform, self).__init__()
        global currColor

        self.w = 1000
        self.h = 50

        self.surf = pygame.Surface((self.w, self.h))
        self.surf.fill(secondaryColor)
        self.rect = self.surf.get_rect(topleft=(0, position))


class BottomSpike(pygame.sprite.Sprite):
    def __init__(self):
        super(BottomSpike, self).__init__()

        self.size = (50, 50)
        self.surf = pygame.Surface(self.size)
        self.rect = self.surf.get_rect(topleft=(300, 300))
        self.surf.fill(WHITE)  # this is only for the mask to work
        self.mask = pygame.mask.from_surface(self.surf)

        self.x = WIDTH
        self.squish = 90

    def update(self):
        self.x -= SPIKESPEED
        self.pos = [[self.x, HEIGHT - 50], [self.x + 50,
                                            HEIGHT - 50], [self.x + 25, HEIGHT - self.squish]]

        # draw triangle to screen
        pygame.draw.polygon(screen, spikeColor, self.pos)

        self.rect.x = self.x  # update collision box position
        self.rect.y = HEIGHT - self.squish

        if self.rect.right <= 0:
            self.kill()

        for spike in allSpikes:
            if self.rect.top == spike.rect.top:
                if self.rect.left < spike.rect.right and self.rect.left > spike.rect.left:
                    self.kill()


class TopSpike(pygame.sprite.Sprite):
    def __init__(self):
        super(TopSpike, self).__init__()

        self.size = (50, 50)
        self.surf = pygame.Surface(self.size)
        self.rect = self.surf.get_rect(topleft=(300, 300))
        self.surf.fill(WHITE)  # this is only for the mask to work
        self.mask = pygame.mask.from_surface(self.surf)

        self.x = WIDTH
        self.squish = 90

    def update(self):
        self.x -= SPIKESPEED
        self.pos = [[self.x, 50], [self.x + 50, 50],
                    [self.x + 25, self.squish]]

        # draw triangle to screen
        pygame.draw.polygon(screen, spikeColor, self.pos)

        self.rect.x = self.x  # update collision box position
        self.rect.y = 50

        if self.rect.right <= 0:
            self.kill()

        for spike in allSpikes:
            if self.rect.top == spike.rect.top:
                if self.rect.left < spike.rect.right and self.rect.left > spike.rect.left:
                    self.kill()


class BackgroundSquare(pygame.sprite.Sprite):
    def __init__(self):
        super(BackgroundSquare, self).__init__()
        global currColor

        self.size = random.randint(40, 60)
        self.alpha = random.randint(1, 25)
        self.speed = random.randint(1, 3)
        self.startH = random.randint(50, HEIGHT - 50)

        self.surf = pygame.Surface((self.size, self.size))
        self.surf.set_alpha(self.alpha)
        self.surf.fill(WHITE)
        self.rect = self.surf.get_rect(topleft=(WIDTH, self.startH))

    def update(self):
        self.speed += SPEEDMULTIPLIER

        if self.rect.right <= 0:
            self.kill()
        self.rect.move_ip(-self.speed, 0)


class ScoreText(pygame.sprite.Sprite):
    def __init__(self):
        super(ScoreText, self).__init__()
        self.font = pygame.font.Font(
            FONT_DIR, 32)
        self.surf = self.font.render(f"{SCORE}", True, WHITE)
        self.rect = self.surf.get_rect(center=(WIDTH / 2, 23))

    def update(self):
        global SCORE
        SCORE += 1
        self.surf = self.font.render(f"{SCORE}", True, WHITE)


class TitleScreenText(pygame.sprite.Sprite):
    def __init__(self, size):
        super(TitleScreenText, self).__init__()
        self.font = pygame.font.Font(
            FONT_DIR, size)
        self.surf = self.font.render("", True, WHITE)
        self.rect = self.surf.get_rect(center=(WIDTH / 2, HEIGHT / 2))

    def update(self, text, pos):
        self.surf = self.font.render(text, True, WHITE)
        self.rect = self.surf.get_rect(center=(WIDTH / 2, HEIGHT / 2 + pos))


class TitleScreenBackground(pygame.sprite.Sprite):
    def __init__(self):
        super(TitleScreenBackground, self).__init__()
        self.surf = pygame.Surface((1000, 1000))
        self.surf.set_alpha(128)
        self.surf.fill(BLACK)
        self.rect = self.surf.get_rect()


class CharacterSelectBox(pygame.sprite.Sprite):
    def __init__(self, color, pos):
        super(CharacterSelectBox, self).__init__()
        self.size = (35, 35)
        self.surf = pygame.Surface(self.size)
        self.color = color
        self.surf.fill(self.color)

        self.starty = HEIGHT - 60
        self.y = self.starty
        self.center = 295
        self.pos = pos
        self.yvel = 0

        self.rect = self.surf.get_rect(center=(self.pos + self.center, self.y))

    def update(self, isActive):
        if isActive:
            if self.y == self.starty - 20:
                self.yvel = 1
            elif self.y == self.starty:
                self.yvel = -1

            self.y += self.yvel
        else:
            self.yvel = 0
            self.y = self.starty

        self.rect = self.surf.get_rect(center=(self.pos + self.center, self.y))


# Init class objects
p1 = Player()
scoreText = ScoreText()
platforms = pygame.sprite.Group()
bgSquares = pygame.sprite.Group()
allSpikes = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(p1)

ts_Highscore = TitleScreenText(18)
ts_YourScore = TitleScreenText(18)
ts_PressSpace = TitleScreenText(32)
ts_CharSelect = TitleScreenText(24)
ts_CharSelectTips = TitleScreenText(14)
titleScreenBackground = TitleScreenBackground()
titleScreen = pygame.sprite.Group()
titleScreen.add(titleScreenBackground)
titleScreen.add(ts_Highscore)
titleScreen.add(ts_YourScore)
titleScreen.add(ts_PressSpace)
titleScreen.add(ts_CharSelect)
titleScreen.add(ts_CharSelectTips)

characterSelectBoxes = pygame.sprite.Group()
for i in range(len(ALLCOLORS)):
    new_char = CharacterSelectBox(ALLCOLORS[i], i * 50)
    characterSelectBoxes.add(new_char)

top = Platform(0)
bottom = Platform(HEIGHT - 50)
platforms.add(top)
platforms.add(bottom)
all_sprites.add(top)
all_sprites.add(bottom)
# Order is important to keep everything on the correct layer
all_sprites.add(scoreText)

MAKEBG = pygame.USEREVENT + 1
pygame.time.set_timer(MAKEBG, 150)

MAKEBOTTOMSPIKE = pygame.USEREVENT + 2
pygame.time.set_timer(MAKEBOTTOMSPIKE, random.randint(500, 750))
MAKETOPSPIKE = pygame.USEREVENT + 3
pygame.time.set_timer(MAKETOPSPIKE, random.randint(500, 750))

# Game loop
clock = pygame.time.Clock()

jumpTimer = pygame.time.Clock()

gameOverTimer = pygame.time.get_ticks()

running = True
gameOver = True

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:  # on quit
            running = False
        if e.type == KEYDOWN:  # on key down
            if e.key == K_ESCAPE:
                running = False
            if e.key == K_SPACE and not gravityChanging:
                jump.play()
                if jumpTimer.tick() < 400:
                    p1.gravitySwitch()
            if e.key == K_LEFT and gameOver:  # handle character customization
                if not playerColor == 0:
                    playerColor -= 1
                    p1.changeColor()
            if e.key == K_RIGHT and gameOver:
                if not playerColor == len(ALLCOLORS) - 1:
                    playerColor += 1
                    p1.changeColor()
        if e.type == MAKEBG:  # user events
            new_square = BackgroundSquare()
            bgSquares.add(new_square)
        if e.type == MAKEBOTTOMSPIKE:
            if SPIKESPEED > 16:  # if speed is high, make more spikes
                randomNumber = random.randint(100, 400)
            elif SPIKESPEED > 12:
                randomNumber = random.randint(300, 650)
            else:
                randomNumber = random.randint(500, 1000)

            pygame.time.set_timer(MAKEBOTTOMSPIKE, randomNumber)
            new_spike = BottomSpike()
            allSpikes.add(new_spike)
        if e.type == MAKETOPSPIKE:
            if SPIKESPEED > 16:  # if speed is high, make more spikes
                randomNumber = random.randint(100, 400)
            elif SPIKESPEED > 12:
                randomNumber = random.randint(300, 650)
            else:
                randomNumber = random.randint(500, 1000)

            pygame.time.set_timer(MAKETOPSPIKE, randomNumber)
            new_spike = TopSpike()
            allSpikes.add(new_spike)

    screen.fill(currColor)

    if gameOver:
        # this is where the start screen and stuff would go
        if SCORE > HIGHSCORE:
            HIGHSCORE = SCORE

        pressed = pygame.key.get_pressed()
        if pressed[K_SPACE]:
            if pygame.time.get_ticks() - gameOverTimer > 500:
                allSpikes.empty()
                pygame.time.set_timer(MAKETOPSPIKE, random.randint(600, 1000))
                pygame.time.set_timer(
                    MAKEBOTTOMSPIKE, random.randint(600, 1000))
                SPIKESPEED = 6
                SCORE = 0
                gameOver = False

        bgSquares.update()
        ts_Highscore.update(f"Highscore {HIGHSCORE}", -200)
        ts_YourScore.update(f"Your score {SCORE}", -170)
        ts_PressSpace.update("Press space to play", -25)
        ts_CharSelect.update("Character selection", 100)
        ts_CharSelectTips.update(
            "Use your arrow keys to navigate", 127)

        for square in bgSquares:
            screen.blit(square.surf, square.rect)

        for graphic in titleScreen:
            screen.blit(graphic.surf, graphic.rect)

        for character in characterSelectBoxes:
            if character.color == ALLCOLORS[playerColor]:
                character.update(True)
            else:
                character.update(False)
            screen.blit(character.surf, character.rect)

        pygame.display.flip()
        clock.tick(60)
        continue

    # Main updates
    pressed = pygame.key.get_pressed()
    p1.update(pressed)
    bgSquares.update()
    scoreText.update()

    # sense for collision with top or bottom of screen
    touching = pygame.sprite.spritecollide(p1, platforms, False)
    if touching:
        colliding = True
        gravityChanging = False
    else:
        colliding = False
    for platform in touching:
        p1.yvel = 0

        if platform.rect.top > HEIGHT / 2:
            p1.rect.bottom = platform.rect.top
        else:
            p1.rect.top = platform.rect.bottom

    # sense for collision with spikes
    spikeCollide = pygame.sprite.spritecollide(
        p1, allSpikes, False, collided=pygame.sprite.collide_mask)
    if spikeCollide:
        die.play()
        gameOver = True
        gameOverTimer = pygame.time.get_ticks()

    for square in bgSquares:  # in order to place the squares behind the player, blit them first
        screen.blit(square.surf, square.rect)

    for graphic in all_sprites:
        screen.blit(graphic.surf, graphic.rect)

    allSpikes.update()  # update spikes here as they are blitted in update function

    if not SPIKESPEED > 18:
        SPIKESPEED += SPEEDMULTIPLIER  # speed up spikes if not too fast

    # Refresh screen
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
