# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 10:55:06 2018

@author: len
"""

from __future__ import division
import pygame
import random
from os import path


#x = 0
#def ret_x():
#    return x
#
#def plus():
#    global x
#    x+=1
## assets folder
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

open_sound = False

#change all cooldown time from real time to FPS time
shoot_delay = 20
Time = 0

def get_time():
    return Time
###############################
## to be placed in "constant.py" later
WIDTH = 480
HEIGHT = 600
#POWERUP_TIME = 5000
POWERUP_TIME = shoot_delay*20
BAR_LENGTH = 100
BAR_HEIGHT = 10

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
###############################

###############################
## to placed in "__init__.py" later
## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
###############################

font_name = pygame.font.match_font('arial')

def main_menu():
    global screen

    menu_song = pygame.mixer.music.load(path.join(sound_folder, "menu.ogg"))
    if open_sound:
        pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "main.png")).convert()
    title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)

    screen.blit(title, (0,0))
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
                pygame.quit()
                quit() 
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, WIDTH/2, HEIGHT/2)
            draw_text(screen, "or [Q] To Quit", 30, WIDTH/2, (HEIGHT/2)+40)
            pygame.display.update()

    #pygame.mixer.music.stop()
    ready = pygame.mixer.Sound(path.join(sound_folder,'getready.ogg'))
    if open_sound:
        ready.play()
    screen.fill(BLACK)
    draw_text(screen, "GET READY!", 40, WIDTH/2, HEIGHT/2)
    pygame.display.update()
#    
#
def draw_text(surf, text, size, x, y):
    ## selecting a cross platform font to display the score
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)       ## True denotes the font to be anti-aliased 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    # if pct < 0:
    #     pct = 0
    pct = max(pct, 0) 
    ## moving them to top
    # BAR_LENGTH = 100
    # BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect= img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
#        self.last_update = pygame.time.get_ticks()
        self.last_update = Time
#        self.frame_rate = 75#should change to count by FPS
        self.frame_rate = shoot_delay*3/10.
        

    def update(self):
#        now = pygame.time.get_ticks()
        now = Time
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self,all_sprites,bullets):
        pygame.sprite.Sprite.__init__(self)
        ## scale the player img down
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0 
        self.shield = 100
#        self.shoot_delay = 250#this delay should not be decided by real time,because it invole accelerating when train
        self.shoot_delay = shoot_delay#FPS
#        self.last_shot = pygame.time.get_ticks()
        self.last_shot = Time
        self.lives = 1
        self.hidden = False
#        self.hide_timer = pygame.time.get_ticks()
        self.hide_timer = Time
        self.power = 1
#        self.power_timer = pygame.time.get_ticks()
        self.all_sprites = all_sprites
        self.bullets = bullets
        

    def update(self):
        ## time out for powerups
#        if self.power >=2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
        if self.power >=2 and Time - self.power_time > POWERUP_TIME:
            self.power -= 1
#            self.power_time = pygame.time.get_ticks()
            self.power_time = Time

        ## unhide 
#        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
        if self.hidden and Time - self.hide_timer > shoot_delay*4:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30

#        self.speedx = 0     ## makes the player static in the screen by default. 
        # then we have to check whether there is an event hanlding being done for the arrow keys being 
        ## pressed 

#        ## will give back a list of the keys which happen to be pressed down at that moment
#        keystate = pygame.key.get_pressed()     
#        if keystate[pygame.K_LEFT]:
#            self.speedx = -5
#        elif keystate[pygame.K_RIGHT]:
#            self.speedx = 5
#
#        #Fire weapons by holding spacebar
#        if keystate[pygame.K_SPACE]:
#            self.shoot()

        ## check for the borders at the left and right
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

    def shoot(self):
        ## to tell the bullet where to spawn
#        now = pygame.time.get_ticks()
        now = Time
        if now - self.last_shot > self.shoot_delay:
#        if now - self.last_shot > 0:
            self.last_shot = now
            if self.power == 1:
                self.bullet = Bullet(self.rect.centerx, self.rect.top)
                self.all_sprites.add(self.bullet)
                self.bullets.add(self.bullet)
                if open_sound:
                    shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                self.all_sprites.add(bullet1)
                self.all_sprites.add(bullet2)
                self.bullets.add(bullet1)
                self.bullets.add(bullet2)
                if open_sound:
                    shooting_sound.play()

            """ MOAR POWAH """
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top) # Missile shoots from center of ship
                self.all_sprites.add(bullet1)
                self.all_sprites.add(bullet2)
                self.all_sprites.add(missile1)
                self.bullets.add(bullet1)
                self.bullets.add(bullet2)
                self.bullets.add(missile1)
                if open_sound:
                    shooting_sound.play()
                    missile_sound.play()

    def powerup(self):
        self.power += 1
#        self.power_time = pygame.time.get_ticks()
        self.power_time = Time

    def hide(self):
        self.hidden = True
#        self.hide_timer = pygame.time.get_ticks()
        self.hide_timer = Time
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# defines the enemies
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width *.90 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(5, 20)        ## for randomizing the speed of the Mob

        ## randomize the movements a little more 
        self.speedx = random.randrange(-3, 3)

        ## adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
#        self.last_update = pygame.time.get_ticks()  ## time when the rotation has to happen
        self.last_update = Time
        
    def rotate(self):
#        time_now = pygame.time.get_ticks()
        time_now = Time
#        if time_now - self.last_update > 50: # in milliseconds
        if time_now - self.last_update > shoot_delay/5:
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360 
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        ## now what if the mob element goes out of the screen

        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)        ## for randomizing the speed of the Mob

## defines the sprite for Powerups
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.top > HEIGHT:
            self.kill()

            

## defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.bottom < 0:
            self.kill()

        ## now we need a way to shoot
        ## lets bind it to "spacebar".
        ## adding an event for it in Game loop

## FIRE ZE MISSILES
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
            
###################################################
## Load all game images

background = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_rect = background.get_rect()
## ^^ draw this rect first 

player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()
missile_img = pygame.image.load(path.join(img_dir, 'missile.png')).convert_alpha()
# meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()
meteor_images = []
meteor_list = [
    'meteorBrown_big1.png',
    'meteorBrown_big2.png', 
    'meteorBrown_med1.png', 
    'meteorBrown_med3.png',
    'meteorBrown_small1.png',
    'meteorBrown_small2.png',
    'meteorBrown_tiny1.png'
]

for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())

## meteor explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    ## resize the explosion
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    ## player explosion
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

## load power ups
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()


###################################################


###################################################
### Load all game sounds
shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
## main background music
#pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.2)      ## simmered the sound down a little

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))
###################################################

class GameState:
    def __init__(self):
        #time count by FPS
        global Time
        Time = 0
        
        ## group all the sprites together for ease of update
        self.all_sprites = pygame.sprite.Group()
        
        ## group for bullets
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(self.all_sprites,self.bullets)
        self.all_sprites.add(self.player)
        
        ## spawn a group of mob
        self.mobs = pygame.sprite.Group()
        for i in range(8):      ## 8 mobs
            # mob_element = Mob()
            # all_sprites.add(mob_element)
            # mobs.add(mob_element)
            self.newmob()
                
        #### Score board variable
        self.score = 0
        self.score_before = 0
        
        self.player.shield_before = 100
        
        self.terminal = False
        
    def reset(self):
        #time count by FPS
        global Time
        Time = 0
        
        self.all_sprites.empty()
#        self.all_sprites = pygame.sprite.Group()
        
        ## group for bullets
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.player = Player(self.all_sprites,self.bullets)
        self.all_sprites.add(self.player)
        
        ## spawn a group of mob
        self.mobs = pygame.sprite.Group()
        for i in range(8):      ## 8 mobs
            # mob_element = Mob()
            # all_sprites.add(mob_element)
            # mobs.add(mob_element)
            self.newmob()
        
        
        #### Score board variable
        self.score = 0
        self.score_before = 0
        
        self.player.shield_before = 100
        
        self.terminal = False
        
    
    def newmob(self):
        mob_element = Mob()
        self.all_sprites.add(mob_element)
        self.mobs.add(mob_element)
    
    def step(self,input_actions):
        #2 Update
        self.all_sprites.update()
        
        self.player.speedx = 0
        global Time
        Time += 1
#        self.terminal = False
        
        # input_actions[0] == 1: do nothing
        # input_actions[1] == 1: move left
        # input_actions[2] == 1: move right
        # input_actions[3] == 1: shoot
        if input_actions[1] == 1:
            self.player.speedx = -5
        if input_actions[2] == 1:
            self.player.speedx = 5
        if input_actions[3] == 1:
            self.player.shoot()
    
    
        ## check if a bullet hit a mob
        ## now we have a group of bullets and a group of mob
        hits = pygame.sprite.groupcollide(self.mobs, self.bullets, True, True)
        ## now as we delete the mob element when we hit one with a bullet, we need to respawn them again
        ## as there will be no mob_elements left out 
        for hit in hits:
            self.score += 50 - hit.radius         ## give different scores for hitting big and small metoers
            if open_sound:
                random.choice(expl_sounds).play()
            # m = Mob()
            # all_sprites.add(m)
            # mobs.add(m)
            expl = Explosion(hit.rect.center, 'lg')
            self.all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Pow(hit.rect.center)
                self.all_sprites.add(pow)
                self.powerups.add(pow)
            self.newmob()        ## spawn a new mob
    
        ## ^^ the above loop will create the amount of mob objects which were killed spawn again
        #########################
    
        ## check if the player collides with the mob
        hits = pygame.sprite.spritecollide(self.player, self.mobs, True, pygame.sprite.collide_circle)        ## gives back a list, True makes the mob element disappear
        for hit in hits:
            self.player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            self.all_sprites.add(expl)
            self.newmob()
            if self.player.shield <= 0: 
                if open_sound:
                    player_die_sound.play()
                self.death_explosion = Explosion(self.player.rect.center, 'player')
                self.all_sprites.add(self.death_explosion)
                # running = False     ## GAME OVER 3:D
                self.player.hide()
                self.player.lives -= 1#这里有可能多个子弹打中，循环之后，live直接变成0再变成-1
                if self.player.lives >0:
                    self.player.shield = 100
    
        ## if the player hit a power up
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                self.player.shield += random.randrange(10, 30)
                if self.player.shield >= 100:
                    self.player.shield = 100
            if hit.type == 'gun':
                self.player.powerup()
    
        ## if player died and the explosion has finished, end game
#        if self.player.lives == 0 and not self.death_explosion.alive():
        if self.player.lives <=0 :#所以这个地方要用<=进行判断
            self.terminal = True
            # menu_display = True
            # pygame.display.update()
#            pygame.quit()
#            self.reset()
    
        #3 Draw/render
        screen.fill(BLACK)
        ## draw the stargaze.png image
#        screen.blit(background, background_rect)
    
        self.all_sprites.draw(screen)
#        draw_text(screen, str(self.score), 18, WIDTH / 2, 10)     ## 10px down from the screen
        pygame.display.set_caption("Space Shooter - score:"+str(self.score)+','+str(self.player.shield)+','+str(self.player.lives)+','+str(Time))
        draw_shield_bar(screen, 5, 5, self.player.shield)
    
        # Draw lives
        draw_lives(screen, WIDTH - 100, 5, self.player.lives, player_mini_img)
    
        ## Done after drawing everything to the screen
#        pygame.display.flip()
        pygame.display.update() 
        
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        reward = ((self.score - self.score_before-5) + (self.player.shield - self.player.shield_before)*2+(self.player.power-1)*10)/100.
        
#        reward = [self.score - self.score_before,self.player.shield - self.player.shield_before,self.player.shield,self.player.power]
        self.score_before = self.score
        self.player.shield_before = self.player.shield
        
        if self.terminal:
            reward = -1.
#            self.reset()
            
        
        return image_data, reward, self.terminal
            
        
    
 

















