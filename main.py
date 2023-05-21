import pygame
import random
import os

FPS = 60
WIDTH = 800
HEIGHT = 600

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0 , 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# game initialization and create window
pygame.init()
pygame.mixer.init()  # initialize the mixer module for loading and playing sounds
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My First Pygame Game ")
clock = pygame.time.Clock()

# load image
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))  # create a new image with the size of 25 * 19
player_mini_img.set_colorkey(BLACK)  # disable black background, making black become transpatent
pygame.display.set_icon(player_mini_img)  # set the icon of the window
# rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
expl_anim = {}  # a dictionary that stores the explosion animation
expl_anim['lg'] = []  # a list that stores the large explosion animation
expl_anim['sm'] = []  # a list that stores the small explosion animation
expl_anim['player'] = []  # a list that stores the player explosion animation
for i in range(9):
    expl_img = pygame.image.load(os.path.join('img', f'expl{i}.png')).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join('img', f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join('img', 'shield.png')).convert()
power_imgs['gun'] = pygame.image.load(os.path.join('img', 'gun.png')).convert()

# load sound
shoot_sound = pygame.mixer.Sound(os.path.join('sound', 'shoot.wav'))
die_sound = pygame.mixer.Sound(os.path.join('sound', 'rumble.ogg'))
gun_sound = pygame.mixer.Sound(os.path.join('sound', 'pow1.wav'))
shield_sound = pygame.mixer.Sound(os.path.join('sound', 'pow0.wav'))
expl_sound = [
    pygame.mixer.Sound(os.path.join('sound', 'expl0.wav')),
    pygame.mixer.Sound(os.path.join('sound', 'expl1.wav'))
]
pygame.mixer.music.load(os.path.join('sound', 'background.ogg'))

font_name = os.path.join("font.ttf") # get the font name of the system

def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "太空生存戰", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "按 a 與 d 移動飛船 空白鍵發射子彈", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "按任意鍵開始遊戲", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.update()
    waiting = True  # the game is waiting
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False
            
def draw_text(surf, text, size, x, y):  # surf -> write on which surface; text -> write what text; size -> write with what size; x, y -> write at what position
    font = pygame.font.Font(font_name, size)  # create a font object
    text_surface = font.render(text, True, WHITE)  # create a surface object with the text (The second parameter is antialiasing, which is a boolean value that determines if the text should be smoothed or not.)
    text_rect = text_surface.get_rect()  # get the rectangle obje ct that has the dimensions of the surface
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)  # draw the text surface on the surface object

def new_rock():
    r = Rock()  # create a rock object
    all_sprites.add(r)  # add the rock object to the group of sprites
    rock_sprites.add(r)  # add the rock object to the group of rock sprites

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y,BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)  # 2 is the width of the outline

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i  # 30 is the distance between each image
        img_rect.y = y
        surf.blit(img, img_rect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))  # create an object with its image
        self.image.set_colorkey(BLACK)  # disable black background, making black become transpatent
        self.rect = self.image.get_rect()  # get the rectangle object that has the dimensions of the image
        self.radius = 20  # set the radius of the circle object
        # self.rect.x = 200  # set the x position of the rectangle object
        # self.rect.y = 200  # set the y position of the rectangle object
        self.rect.centerx = WIDTH / 2  # set the center of the rectangle object
        self.rect.bottom = HEIGHT - 10  # set the bottom of the rectangle object
        self.speedx = 8  # set the speed of the rectangle object in x direction
        self.health = 100  # set the health of the player
        self.life = 3  # set the life of the player
        self.hidden = False  # set the player to be visible
        self.hide_time = 0  # set the time when the player is hidden
        self.gun = 1  # set the gun level of the player
        self.gun_time = 0

    def update(self):
        if self.gun > 1 and pygame.time.get_ticks() - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_time > 1000:  # if the player is hidden and the time interval between now and the time when the player is hidden is greater than 1000 milliseconds
            self.hidden = False  # set the player to be visible
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_press = pygame.key.get_pressed()  # get the list of keys that are pressed (a list of booleans indicating if the key in the keyboard is pressed or not)
        if key_press[pygame.K_d]:  # if the right key is pressed
            self.rect.x += self.speedx  # move the rectangle object to right
        if key_press[pygame.K_a]:  # if the left key is pressed
            self .rect.x -= self.speedx  # move the rectangle object to left
        if self.rect.right > WIDTH:  # if the rectangle object is out of the screen
            self.rect.right = WIDTH  # set the right side of the rectangle object to WIDTH
        if self.rect.left < 0:  # if the rectangle object is out of the screen
            self.rect.left = 0  # set the left side of the rectangle object to 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)  # create a bullet object
                all_sprites.add(bullet)  # add the bullet object to the group of sprites
                bullet_sprites.add(bullet)  # add the bullet object to the group of bullet sprites
                shoot_sound.play()  # play the shoot sound
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)  # create a bullet object
                bullet2 = Bullet(self.rect.right, self.rect.centery)  # create a bullet object
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullet_sprites.add(bullet1)
                bullet_sprites.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True  # set the player to be invisible
        self.hide_time = pygame.time.get_ticks()  # get the time in milliseconds
        self.rect.center = (WIDTH / 2, HEIGHT + 500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # initialize the sprite
        self.image_ori = random.choice(rock_imgs) # randomly choose a rock image
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy() # create an object with its image
        self.rect = self.image.get_rect()  # get the rectangle object that has the dimensions of the image
        self.radius = int(self.rect.width * 0.85 / 2) # set the radius of the circle object
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)  # set the x position of the rectangle object
        self.rect.y = random.randrange(-180, -100)  # set the y position of the rectangle object
        self.speedy = random.randrange(2, 10)  # set the speed of the rectangle object in y direction
        self.speedx = random.randrange(-3, 3)  # set the speed of the rectangle object in x direction
        self.total_degree = 0  # set the total degree of rotation
        self.rot_degree = random.randrange(-3, 3) # set the degree of rotation

    def rotate(self):
        self.total_degree += self.rot_degree  # add the degree of rotation to the total degree of rotation
        self.total_degree = self.total_degree % 360  # reset the total degree of rotation in the range of 0 to 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)  # rotate the image
        centeer = self.rect.center  # get the center of the rectangle object
        self.rect = self.image.get_rect()  # relocate the rectangle of the object
        self.rect.center = centeer  # reset the center of the rectangle object

    def update(self):
        self.rotate()  # rotate the rock object
        self.rect.y += self.speedy  # falling down
        self.rect.x += self.speedx  # move left and right
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:  # if the rectangle object is out of the screen
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)  # reset x position
            self.rect.y = random.randrange(-100, -40)  # reset y position
            self.speedy = random.randrange(2, 10)  # reset speed in y direction
            self.speedx = random.randrange(-3, 3)  # reset speed in x direction

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):  # x and y are the position of the Player object
        pygame.sprite.Sprite.__init__(self)  # initialize the sprite
        self.image = bullet_img  # create an object with its image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()  # get the rectangle object that has the dimensions of the image
        self.rect.centerx = x  # set the x position of the rectangle object
        self.rect.bottom = y  # set the y position of the rectangle object
        self.speedy = -10   # set the speed of the rectangle object in y direction (upward)

    def update(self):
        self.rect.y += self.speedy  # move upward
        if self.rect.bottom < 0:  # if the rectangle object is out of the screen
            self.kill()  # kill the sprite if it is out of the screen

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)  # initialize the sprite
        self.size = size
        self.image = expl_anim[self.size][0] 
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()  # get the time in milliseconds
        self.frame_rate = 50  # the time interval between each frame

    def update(self):
        now = pygame.time.get_ticks()  # get the time in milliseconds
        if now - self.last_update > self.frame_rate:  # if the time interval between now and the last update is greater than the frame rate
            self.last_update = now  # reset the last update time
            self.frame += 1
            if self.frame == len(expl_anim[self.size]): 
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)  # initialize the sprite
        self.type = random.choice(['shield', 'gun'])  # randomly choose a power type
        self.image = power_imgs[self.type]  # create an object with its image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()  # get the rectangle object that has the dimensions of the image
        self.rect.center = center
        self.speedy = 10   # set the speed of the rectangle object in y direction (downward)

    def update(self):
        self.rect.y += self.speedy  # move downward
        if self.rect.top > HEIGHT:
            self.kill()

all_sprites = pygame.sprite.Group()  # create a group of sprites
rock_sprites = pygame.sprite.Group()  # create a group of rock sprites
bullet_sprites = pygame.sprite.Group()  # create a group of bullet sprites
powers = pygame.sprite.Group()  # create a group of power sprites
player = Player()  # create a player object
all_sprites.add(player)  # add the player object to the group of sprites
for i in range(8):  # create 8 rock objects
    new_rock()  # create a new rock object
score = 0  # initialize the score
pygame.mixer.music.play(-1)  # play the background music infinitely
pygame.mixer.music.set_volume(0.5)  # set the volume of the background music

# game loop
show_init = True  # show the initial screen
running = True  # the game is running
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()  # create a group of sprites
        rock_sprites = pygame.sprite.Group()  # create a group of rock sprites
        bullet_sprites = pygame.sprite.Group()  # create a group of bullet sprites
        powers = pygame.sprite.Group()  # create a group of power sprites
        player = Player()  # create a player object
        all_sprites.add(player)  # add the player object to the group of sprites
        for i in range(8):  # create 8 rock objects
            new_rock()  # create a new rock object
        score = 0  # initialize the score

    clock.tick(FPS)  # 60 frames per second

    # event handling
    for event in pygame.event.get():  # pygame.event.get() will return all the occurring events in a list
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # if a key is pressed
            if event.key == pygame.K_SPACE:  # if the space key is pressed
                player.shoot()  # shoot the bullet

    # update game state
    all_sprites.update()  # update all the sprites in the group

    # Determine if the bullet sprite and the rock sprite collide
    hits = pygame.sprite.groupcollide(rock_sprites, bullet_sprites, True, True)  # if a rock sprite and a bullet sprite collide, kill both of them (return a dictionary)
    for hit in hits:  # for each rock sprite that is killed
        random.choice(expl_sound).play()  # play a random explosion sound
        score += hit.radius  # increase the score by the radius of the rock sprite
        expl = Explosion(hit.rect.center, 'lg')  # create a large explosion object
        all_sprites.add(expl)  # add the explosion object to the group of sprites
        if random.random() > 0.95:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()  # create a new rock sprite

    # Determine if the player sprite and the rock sprite collide
    hits = pygame.sprite.spritecollide(player, rock_sprites, True, pygame.sprite.collide_circle)  # if a rock sprite and the player sprite collide
    for hit in hits:  # for each rock sprite that collides with the player sprite
        new_rock()  # create a new rock sprite
        player.health -= hit.radius  # decrease the health of the player by the radius of the rock sprite
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)  # add the explosion object to the group of sprites
        if player.health <= 0:
            die = Explosion(player.rect.center, 'player')
            all_sprites.add(die)
            die_sound.play()
            player.life -= 1  # decrease the life of the player
            player.health = 100  # reset the health of the player
            player.hide()  # hide the player
            #running = False

    # Determine if the player sprite and the power sprite collide
    hits = pygame.sprite.spritecollide(player, powers, True)  # if a power sprite and the player sprite collide
    for hit in hits:
        if hit.type == 'shield':
            player.health += 20
            shield_sound.play()
            if player.health > 100:
                player.health = 100
        elif hit.type == 'gun':
            player.gunup()
            gun_sound.play()

    if player.life == 0 and not(die.alive()):  # if the player has no life and the player explosion animation is not playing
        show_init = True  # show the initial screen

    # draw
    screen.fill(BLACK)
    screen.blit(background_img, (0, 0))
    draw_text(screen, str(score), 18, WIDTH / 2, 10)  # draw the score on the screen
    draw_health(screen, player.health, 5, 15)  # draw the health bar on the screen
    draw_lives(screen, player.life, player_mini_img, WIDTH - 100, 15)
    all_sprites.draw(screen)  # draw all the sprites in the group 

    pygame.display.update()

pygame.quit()