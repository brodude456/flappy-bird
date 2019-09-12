import pygame as pg
pg.init()

from os import path
from flappy_bird_settings import *

img_dir = path.join(path.dirname(__file__), 'img')

import random


def draw_text(surf, text, size, x, y):
    WHITE = (255, 255, 255)
    font_name = pg.font.match_font('arial')
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image


class Bird(pg.sprite.Sprite):
    def __init__(self,game):
        self.game=game
        self.game.player=self
        self.game.score=0
        self.groups=self.game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.vely=0
        self.accy=0.5
        self.frame=0
        self.animationlist=[self.game.spritesheet.get_image(566,510,122,139),self.game.spritesheet.get_image(568,1534,122,135)]
        for i in range(len(self.animationlist)):
            self.animationlist[i]=pg.transform.scale(self.animationlist[i],(63,63))
        self.image=self.animationlist[self.frame]
        self.image.set_colorkey(BLACK)
        self.rect=self.image.get_rect()
        self.rect.centery=HEIGHT//2-100
        self.rect.centerx=250
        self.rotateamount=0
        self.rotateincreaser=10
        self.timebeetweenupdates=20
        self.lastupdated=pg.time.get_ticks()-self.timebeetweenupdates
        self.timebetweenanimates=300
        self.lastanimated=pg.time.get_ticks()-self.timebetweenanimates
        self.rotate=False
        self.move=False
        self.jigglevel=3
        self.jiggleacc=-1
        self.score=0
        self.lives=3
        self.speedlimit=43.5
        self.shield=False
        self.powerup=False
        self.jumpF=-15

    def update(self):

        if self.rotateamount!=-90 and self.game.canjump or self.frame==1:

            self.animate()

        self.rotatee()

        new_image=pg.transform.rotate(self.animationlist[self.frame],self.rotateamount)
        #new_image=pg.transform.scale(new_image,(70,70))
        oldcenter=self.rect.center
        self.image=new_image
        self.image.set_colorkey(BLACK)
        self.rect=self.image.get_rect()
        self.rect.center=oldcenter


        if self.vely>self.speedlimit:
            self.vely=self.speedlimit

        if self.move:
            self.rect.centery+=self.vely
            if self.rect.centery<self.rect.height//2:
                self.rect.centery=self.rect.height//2
            elif self.rect.centery>HEIGHT-self.rect.height//2:
                self.game.playing=False
            self.vely+=self.accy

        else:self.jiggle()
        if self.powerup:
            if pg.time.get_ticks()-self.pickedtime>self.ptimer:
                self.powerup=False
                self.jumpF=-15
                self.shield=False
                self.accy=0.5

    def jump(self):
        if self.game.canjump==True:
            self.vely=self.jumpF

    def jump_cut(self):
        if self.vely<-3:
            self.vely=-3

    def animate(self):
        if pg.time.get_ticks()-self.lastanimated>self.timebetweenanimates:
            self.lastanimated=pg.time.get_ticks()
            self.frame=(self.frame+1)%len(self.animationlist)

    def rotatee(self):
        if self.rotate and pg.time.get_ticks()-self.lastupdated>self.timebeetweenupdates:
            self.lastupdated=pg.time.get_ticks()

            if self.vely>5:
                self.rotateamount-=self.rotateincreaser
                if self.rotateamount<-90:
                    self.rotateamount=-90

            elif self.vely<0:
                self.rotateamount+=self.rotateincreaser
                if self.rotateamount>45:
                    self.rotateamount=45

    def jiggle(self):
        self.rect.centery+=self.jigglevel
        self.jigglevel+=self.jiggleacc
        if self.jigglevel<-8 or self.jigglevel>8:
            self.jigglevel=(self.jigglevel/abs(self.jigglevel))*8
            self.jiggleacc*=-1

class Pipes():

    velx=-2
    width=10*5

    def __init__(self,game,centerx):
        self.game=game
        vdbps=random.choice([200,250,225])
        pip1height=random.randrange(25,HEIGHT-25-vdbps+1)
        pip2height=HEIGHT-(pip1height+vdbps)
        pip1centery=pip1height//2
        pip2centery=pip1height+vdbps+pip2height//2
        self.pipes=[OnePipe(self.game,self.game.spritesheet.get_image(0,288,380,94),pip1height,centerx,pip1centery,self.game.spritesheet.get_image(0,768,380,94)),
                    OnePipe(self.game,self.game.spritesheet.get_image(0,768,380,94),pip2height,centerx,pip2centery,self.game.spritesheet.get_image(0,288,380,94))]
        self.centerx=centerx
        self.width=Pipes.width
        self.spawn_new=False
        self.past=False

    def update(self):
        for pipe in self.pipes:
            pipe.rect.centerx+=Pipes.velx
        self.centerx+=Pipes.velx
        if self.centerx<-self.width//2:
            for pipe in self.pipes:
                pipe.kill()
            self.game.pipess.remove(self)
        elif self.centerx+self.width//2<self.game.player.rect.centerx-self.game.player.rect.width//2 and not self.past:
            if Pipes.velx>-10 and self.game.pipesnumero%3==0:
                self.game.shortestditanscebeetweenpipe+=40
                self.game.longestdistancebeetweenpipe+=10
                self.game.mediumdistance+=20
                Pipes.velx-=1
            self.past=True
            self.game.pipesnumero+=1
            if self.pipes[0].hitme==False and self.pipes[0].hitme==False:
                self.game.player.score+=1
                self.game.playerpast+=1
            else:self.game.playerpast=0
        elif self.centerx-self.width//2<self.game.whentospawn and self.spawn_new==False:
            self.spawn_new=True
            self.game.pipess.append(make_pipe(self.game))
            self.game.whentospawn=random.choice([self.game.player.rect.centerx+375,self.game.player.rect.centerx+400,self.game.player.rect.centerx+350])

        if self.game.playerpast==6:
                self.game.player.lives+=1
                if self.game.player.lives>5:
                    self.game.player.lives=5
                self.game.playerpast=0

class OnePipe(pg.sprite.Sprite):

    def __init__(self,game,img,height,centerx,centery,otherimage):
        self.game=game
        pg.sprite.Sprite.__init__(self,(self.game.pipes,self.game.all_sprites))
        self.image=pg.transform.rotate(img,90)
        self.image=pg.transform.scale(self.image, (Pipes.width, height))
        self.image.set_colorkey(BLACK)
        self.rect=self.image.get_rect()
        self.rect.centerx=centerx
        self.rect.centery=centery
        self.hitme=False
        self.myimage=img
        self.height=height
        self.otherimage=pg.transform.rotate(otherimage,90)
        self.otherimage.set_colorkey(BLACK)

    def update(self):

        if self.hitme==True:
            oldcenter=self.rect.center
            self.image=pg.transform.scale(self.otherimage,(Pipes.width,self.height))
            self.rect=self.image.get_rect()
            self.rect.center=oldcenter

class Powerup(pg.sprite.Sprite):
    def __init__(self,pipe):
        pg.sprite.Sprite.__init__(self,(pipe.game.all_sprites,pipe.game.powerups))
        self.pipe=pipe
        self.powerlist=["jetpack","incgravity","shield"]
        self.duration=random.randrange(2000,7501)
        self.power=random.choice(self.powerlist)
        self.imagelist=[random.choice([self.pipe.game.spritesheet.get_image(563,1843,133,160),self.pipe.game.spritesheet.get_image(820,1805,71,70)]),
             self.pipe.game.spritesheet.get_image(826,1220,71,70),
             self.pipe.game.spritesheet.get_image(826,134,71,70)]
        self.imageorig=self.imagelist[self.powerlist.index(self.power)]
        self.image=self.imageorig
        self.imageorig=pg.transform.scale(self.imageorig,(50,50))
        self.imageorig.set_colorkey(BLACK)
        self.image.set_colorkey(BLACK)
        self.rect=self.image.get_rect()
        self.rect.centerx=self.pipe.centerx
        self.rect.centery=random.randrange(25,HEIGHT-25+1)
        hitpipe=pg.sprite.spritecollideany(self,self.pipe.game.pipes,False)
        while hitpipe:
            self.rect.centery=random.randrange(25,HEIGHT-25+1)
            hitpipe=pg.sprite.spritecollideany(self,self.pipe.game.pipes,False)
        self.rotateamount=0
        self.rotateincreaser=random.randrange(-8,9)
        self.timebeetweenupdates=50
        self.lastupdated=pg.time.get_ticks()

    def update(self):
        self.rect.centerx=self.pipe.centerx
        if pg.time.get_ticks()-self.lastupdated>self.timebeetweenupdates:
            self.rotate()
            self.lastupdated=pg.time.get_ticks()

    def rotate(self):
        self.rotateamount=(self.rotateamount+self.rotateincreaser)%360
        oldcenter=self.rect.center
        self.image=pg.transform.rotate(self.imageorig,self.rotateamount)
        self.rect=self.image.get_rect()
        self.rect.center=oldcenter

def make_pipe(game):

    return  Pipes(game, random.choice([game.whentospawn + game.shortestditanscebeetweenpipe, game.whentospawn + game.longestdistancebeetweenpipe, game.whentospawn + game.mediumdistance]) + Pipes.width // 2)

class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

    def new(self):
        # start a new game
        self.all_sprites = pg.sprite.Group()
        self.player = Bird(self)
        self.all_sprites.add(self.player)
        self.pipes=pg.sprite.Group()
        self.canjump=True
        self.shortestditanscebeetweenpipe=345
        self.longestdistancebeetweenpipe=500
        self.mediumdistance=(self.shortestditanscebeetweenpipe+self.longestdistancebeetweenpipe)//2
        self.whentospawn=random.choice([self.player.rect.centerx+375,self.player.rect.centerx+400,self.player.rect.centerx+350])
        self.powerups=pg.sprite.Group()
        self.pipess=[Pipes(self, WIDTH + (Pipes.width // 2))]
        Pipes.velx=-4
        self.pipesnumero=1
        self.playerpast=0
        self.timebeetweenpowsp=random.choice([3000,5000,2000,4000])
        self.lastimepspanew=0
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            print(Pipes.velx)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        if self.player.move and self.canjump:
            for pipe in self.pipess:
                pipe.update()

        if pg.time.get_ticks()-self.lastimepspanew>self.timebeetweenpowsp:
            if self.pipess[-1].centerx>WIDTH+Pipes.width//2:
                for i in range(random.randrange(0,4)):
                    Powerup(self.pipess[-1])
                    self.lastimepspanew=pg.time.get_ticks()
                    self.timebeetweenpowsp=random.choice([1000,2000,3000,4000,5000])


        hit=pg.sprite.spritecollide(self.player,self.pipes,False)
        if hit and hit[0].hitme==False:
            if self.player.shield==False:
                self.player.lives-=1
            if self.player.lives<0:
                self.player.lives=0
            if self.player.lives==0:
                if self.canjump:
                    self.player.vely=0
                self.canjump=False
            hit[0].hitme=True

        hits=pg.sprite.spritecollide(self.player,self.powerups,True)
        if hits:
            for hit in hits:
                if hit.power=="shield":
                    self.player.shield=True
                if hit.power=="jetpack":
                   self.player.jumpF-=6.5
                   if self.player.jumpF<-30:
                       self.player.jumpF=-30
                if hit.power=="incgravity":
                    self.player.accy+=0.5
                    if self.player.accy>1:
                        self.player.accy=1
            self.player.powerup=True
            self.player.ptimer=hits[0].duration
            self.player.pickedtime=pg.time.get_ticks()

    def events(self):

        for event in pg.event.get():

            if event.type == pg.QUIT:

                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pg.KEYDOWN:

                if event.key == pg.K_SPACE:
                    self.player.move=True
                    self.player.rotate=True
                    self.player.timebetweenanimates=150
                    self.player.jump()

            if event.type == pg.KEYUP:

                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(LIGHTBLUE)
        self.all_sprites.draw(self.screen)
        draw_text(self.screen,str(self.player.score),63,WIDTH//2,50)
        draw_text(self.screen,str(self.player.lives),60,50,45)

        #draw_text(self.screen,self.player.score,55,WIDTH//2,50)

        # *after* drawing everything, flip the display
        pg.display.flip()

g = Game()
while g.running:
    g.new()
pg.quit()


