import pygame
import random
import os
import time
import neat
import visualize
import pickle
pygame.font.init()  # init font

FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
PIPEGAPSIZE  = 100 
FLOOR=450

STAT_FONT = pygame.font.SysFont("comicsans", 30)
END_FONT = pygame.font.SysFont("comicsans", 35)

WIN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Flappy Bird")


pipe_imgs =  [pygame.image.load("imgs/pipe-green.png").convert_alpha()
			 ,pygame.image.load("imgs/pipe-red.png").convert_alpha()]

bird_img=[0,0,0]
bird_img[0]=[pygame.image.load("imgs/redbird-upflap.png").convert_alpha()
			,pygame.image.load("imgs/redbird-midflap.png").convert_alpha()
			,pygame.image.load("imgs/redbird-downflap.png").convert_alpha()]
			
bird_img[1]=[pygame.image.load("imgs/bluebird-upflap.png").convert_alpha()
			,pygame.image.load("imgs/bluebird-midflap.png").convert_alpha()
			,pygame.image.load("imgs/bluebird-downflap.png").convert_alpha()]
			
bird_img[2]=[pygame.image.load("imgs/yellowbird-upflap.png").convert_alpha()
			,pygame.image.load("imgs/yellowbird-midflap.png").convert_alpha()
			,pygame.image.load("imgs/yellowbird-downflap.png").convert_alpha()]
			
			
background_img= [pygame.image.load("imgs/background-day.png").convert_alpha()
				,pygame.image.load("imgs/background-night.png").convert_alpha()]
				
				
				
base_img=pygame.image.load('imgs/base.png').convert_alpha()
'''
SOUNDS={}
SOUNDS['die']    = pygame.mixer.Sound('audio/die.wav')
SOUNDS['hit']    = pygame.mixer.Sound('audio/hit.wav')
SOUNDS['point']  = pygame.mixer.Sound('audio/point.wav')
SOUNDS['swoosh'] = pygame.mixer.Sound('audio/swoosh.wav')
SOUNDS['wing']   = pygame.mixer.Sound('audio/wing.wav')
'''
gene = pickle.load(open("best.pickle", "rb"))


class Bird:
    
    MAX_ROTATION = 25
    IMGS = random.choice(bird_img)
    ROT_VEL = 10
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        
        self.vel = -7
        self.tick_count = 0
        self.height = self.y

    def move(self):
        
        self.tick_count += 1

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # terminal velocity
        if displacement >= 12:
            displacement = 12

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        
        return pygame.mask.from_surface(self.img)


class Pipe():
    GAP = 130
    VEL = 1
    
    def __init__(self, x):
        
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0
        choice = random.randint(0,1)

        self.PIPE_TOP = pygame.transform.flip(pipe_imgs[choice], False, True)
        self.PIPE_BOTTOM = pipe_imgs[1-choice]

        self.passed = False

        self.set_height()

    def set_height(self):
        
        self.height =random.randrange(30, 300)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        
        self.x -= self.VEL

    def draw(self, win):
        
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    
    VEL = 1
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

bg_img=random.choice(background_img)
def draw_window(win, bird, pipes, base, score,AIplaying):
    
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    if AIplaying:
        playerStatus = STAT_FONT.render("AI",1,(255,255,255))
    else :
        playerStatus = STAT_FONT.render("Player",1,(255,255,255))
    win.blit(score_label, (SCREENWIDTH - score_label.get_width() - 15, 10))
    win.blit(playerStatus, (5, 10))
    
    pygame.display.update()


def Play():
    
    
    AIplaying=False
    global gene
    global WIN
    win = WIN
    vel=3
    
    base = Base(450)
    pipes = [Pipe(SCREENWIDTH)]
    score = 0

    clock = pygame.time.Clock()
    bird = Bird(100,100)
    run = True
    while run :
        clock.tick(30)
        
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                break

        pipe_ind = 0
        
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
            pipe_ind = 1                                                                 # pipe on the screen for neural network input
        
        
        bird.move()
        
        
        if keys[pygame.K_SPACE]:
        	AIplaying=True
        	
			
        if AIplaying:
            output = gene.activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()
        else :
            if keys[pygame.K_UP]:
                bird.jump()
		
		
		
        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            pipe.VEL=vel
            # check for collision
            if pipe.collide(bird, win):
                run=False
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            
            if score % 5 == 0:
            	vel+=1
            	base.VEL=vel
            if vel>4:
            	vel=4
            
            pipes.append(Pipe(SCREENWIDTH))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
            run=False

        draw_window(WIN, bird, pipes, base, score,AIplaying)
        AIplaying=False

Play()   

