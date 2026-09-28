#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jump
# Copyright (C) 2008, Joshua Seaver, Bimal Sadhwani, Natalie Rusk
# Copyright (C) 2012, 2013, Alan Aguiar
# Based on the original code in Logo of Natalie Rusk.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Alan Aguiar alanjas@hotmail.com

import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import pygame
import random
from pygame.locals import *
from cur import *
from gettext import gettext as _


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

BROWN_COLOR = (88, 47, 27)
doneTest = 0
global myMatrix

myMatrix = [[2,2,0,0,0,2,2],
           [2,2,0,1,0,2,2],
           [0,0,1,1,1,0,0],
           [0,0,0,1,0,0,0],
           [0,0,0,1,0,0,0],
           [2,2,0,0,0,2,2],
           [2,2,0,0,0,2,2]]

global myMatrix_colors
myMatrix_colors=[[0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0]]
   

myMatrixGridSize = len(myMatrix[0])
marblesLeft = 0
movesLeft = 0
_font = 'VeraSe.ttf'
color=(0,0,0)
#color=(255,255,255)
play_var=0
button1=None
helpoff=None
count=0
marbleColor=0
special_x=0 
special_y=0
next_marble=0

global sound_enable
sound_enable = True

def load_image(name, colorkey=None):
    
    fullname = os.path.join(DATA_DIR, name)
    
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', fullname)
        raise SystemExit(message)

    image = image.convert()
    if colorkey:
        image.set_colorkey(colorkey)
    return image


class NoneSound:
    def play(self):
        pass

def load_sound(name):

    sound = NoneSound()

    fullname = os.path.join(DATA_DIR, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Cannot load sound:', fullname)

    return sound

class board(object):
    
    def __init__(self):
        self.RESERVED = 0
        self.EMPTY = 1
        self.MARBLE = 2
    
    def getLayout(self):
        return [[0,0,2,2,2,0,0],\
                [0,2,2,2,2,2,0],\
                [2,2,2,2,2,2,2],\
                [2,2,2,2,2,2,2],\
                [2,2,2,2,2,2,2],\
                [0,2,2,2,2,2,0],\
                [0,0,2,2,2,0,0]]
    

#need to somehow load in random marble images from data folder

class Marble(pygame.sprite.Sprite):
        
    def __init__(self, rect=None):
        pygame.sprite.Sprite.__init__(self)
        marbleColor = random.random()
        marbleColor = marbleColor * 10
        marbleColor = int(marbleColor)
        if marbleColor > 23:
            marbleColor = 23 
        pngLoad = str(marbleColor)
        pngLoad = pngLoad + '.png'
        self.image = load_image(pngLoad, (255,255,255))
        self.rect = self.image.get_rect()
                
        if rect != None:
            self.rect = rect

class simple_button(pygame.sprite.Sprite):

    def __init__(self,x,y,pic,sound):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(pic)
        self.rect = self.image.get_rect()
        self.status = self.down = self.up = 0
        self.ypos = self.rect.top = y
        self.xpos = self.rect.left = x
        self.pressSound = load_sound('newboard.ogg')
        
    def press(self):
        global sound_enable
        self.status = 1
        if sound_enable:
            self.pressSound.play()
        
    def unpress(self):        
        self.status = 0
                
    def update(self):
        if self.down:
            self.press()
            self.down = 0            
            self.screen.blit(self.background,(0,0))
        elif self.up:
            self.unpress()
            self.up = 0
                        
    def is_focused(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

class SolitaireMain:
    def __init__(self, width=1200,height=825):
        self.width = width
        self.height = height

        self.actual_level = 0

    def change_sound(self, sound):
        global sound_enable
        sound_enable = sound

    def load_things(self):
        self.screen = pygame.display.get_surface()
        if (self.screen == None):
            info = pygame.display.Info()
            self.width = info.current_w
            self.height = info.current_h
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
            pygame.display.set_caption(_('Jump'))

        self.font = pygame.font.Font(None, 50)

        self.marble_images=[]

        for i in range(25):

            image = load_image(str(i) + '.png', color)
            self.marble_images.append(image)

        bl=load_image("blank.png", (255,255,255))
        z=load_image("25.png")
   
        self.marble_images.append(bl)#number25
        self.marble_images.append(z)        

        #special marbles
        self.special_marbles=[]
        for i in range(36):
            n = i + 1
            image = load_image('S' + str(n) + '.png')
            self.special_marbles.append(image)

        self.special_marbles[32] = bl #no 32
        
        #call reset funnction
        self.reset()
        self.helpscreen = load_image("Instructions.png")
        self.flags=[]
        self.flags.append(load_image("Flag01.png"))
        self.flags.append(load_image("Flag02.png"))
        self.flags.append(load_image("Flag03.png"))
        self.flags.append(load_image("Flag04.png"))
        self.flags.append(load_image("Flag05.png"))
        self.flags.append(load_image("Flag06.png"))
        self.flags.append(load_image("Flag07.png"))
        
        
        self.level_sounds=[]
        self.level_sounds.append(load_sound('0.ogg'))
        self.level_sounds.append(load_sound('1.ogg'))
        self.level_sounds.append(load_sound('2.ogg'))
        self.level_sounds.append(load_sound('3.ogg'))
        self.level_sounds.append(load_sound('4.ogg'))
        self.level_sounds.append(load_sound('5.ogg'))
        self.level_sounds.append(load_sound('6.ogg'))
        self.level_sounds.append(load_sound('7.ogg'))

        self.move_sound = load_sound('drop.ogg')
        self.picked_sound = load_sound('pop1.ogg')
        
    def reset(self):    
        global marbleColor
        #intialisation of Number for the first time ..keep a balnk png.
        self.updated_text=32
        self.updated_moves=4
        self.Number=25# 26  #25
        self.pressed=False
        self.selected= False
        self.initial_x=0
        self.initial_y=0
        
        self.final_x=0
        self.final_y=0
        self.OutofRange=True
        
        self.clickedOnce=False
        self.attached=False
        self.picked=False
        marbleColor=0

    def increase_level(self):
        self.actual_level = self.actual_level + 1
        if self.actual_level > 6:
            self.actual_level = 0

    def reset_board(self, level=None):

        if not(level == None):
            self.actual_level = level
        
        global myMatrix
        global myMatrix_colors

        # levels
        # 0:'Cross'
        # 1:'Cross 2'
        # 2:'Hearth'
        # 3:'Arrow'
        # 4:'Pyramid'
        # 5:'Diamond'
        # 6:'Solitaire'

        if self.actual_level == 6:
            myMatrix=[[2,2,1,1,1,2,2],
                      [2,2,1,1,1,2,2],
                      [1,1,1,1,1,1,1],
                      [1,1,1,0,1,1,1],
                      [1,1,1,1,1,1,1],
                      [2,2,1,1,1,2,2],
                      [2,2,1,1,1,2,2]]
     
        elif self.actual_level == 0:
            myMatrix=[[2,2,0,0,0,2,2],
                      [2,2,0,1,0,2,2],
                      [0,0,1,1,1,0,0],
                      [0,0,0,1,0,0,0],
                      [0,0,0,1,0,0,0],
                      [2,2,0,0,0,2,2],
                      [2,2,0,0,0,2,2]]

        elif self.actual_level == 1:
            myMatrix=[[2,2,0,0,0,2,2],
                      [2,2,0,1,0,2,2],
                      [0,0,0,1,0,0,0],
                      [0,1,1,1,1,1,0],
                      [0,0,0,1,0,0,0],
                      [2,2,0,1,0,2,2],
                      [2,2,0,0,0,2,2]]

        elif self.actual_level == 2:
            myMatrix=[[2,2,1,1,1,2,2],
                      [2,2,1,1,1,2,2],
                      [0,0,1,1,1,0,0],
                      [0,0,1,0,1,0,0],
                      [0,0,0,0,0,0,0],
                      [2,2,0,0,0,2,2],
                      [2,2,0,0,0,2,2]]

        elif self.actual_level == 3:
            myMatrix=[[2,2,0,1,0,2,2],
                      [2,2,1,1,1,2,2],
                      [0,1,1,1,1,1,0],
                      [0,0,0,1,0,0,0],
                      [0,0,0,1,0,0,0],
                      [2,2,1,1,1,2,2],
                      [2,2,1,1,1,2,2]]

        elif self.actual_level == 4:
            myMatrix=[[2,2,0,0,0,2,2],
                      [2,2,0,1,0,2,2],
                      [0,0,1,1,1,0,0],
                      [0,1,1,1,1,1,0],
                      [1,1,1,1,1,1,1],
                      [2,2,0,0,0,2,2],
                      [2,2,0,0,0,2,2]]

        elif self.actual_level == 5:
            myMatrix=[[2,2,0,1,0,2,2],
                      [2,2,1,1,1,2,2],
                      [0,1,1,1,1,1,0],
                      [1,1,1,1,1,1,1],
                      [0,1,1,1,1,1,0],
                      [2,2,1,1,1,2,2],
                      [2,2,0,1,0,2,2]]
 
       
        myMatrix_colors=[[0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0],
                         [0,0,0,0,0,0,0]]
        
    def change_level(self, level):
        self.play_var = 0
        self.reset()
        self.reset_board(level)
        self.SuperLooper()
        
    def checkValidMovement(self):     
        global marbleColor, sound_enable
        temp=pygame.mouse.get_pos()

        x=temp[0]    
        y=temp[1]
        x=x-300
        
        x //= 90
        y-=120
        
        y //= 90
        
        if(x>=0 and x<=6 and y>=0 and y<=6):
        
            if(myMatrix[y][x]==0):
                self.final_x=y
                self.final_y=x
            else:
                self.OutofRange=True
                self.final_x=0
                self.final_y=0
           
        
        if(self.initial_x ==0 and self.initial_y ==0):
            self.OutofRange=False
            
        w=self.initial_x
        x=self.initial_y
        self.wInput=self.initial_x
        self.xInput=self.initial_y
        
        y=self.final_x
        z=self.final_y
        
        self.yInput=self.final_x
        self.zInput=self.final_y
        neighborState = 99
        neighborStateRow = 99
        neighborStateColumn = 99
        validJump = 99
        self.matrixPosStart=myMatrix[w][x]
        self.matrixPosEnd=myMatrix[y][z]
        
        if w == y:
            if x > z:
                neighborStateRow = w
                neighborStateColumn = x - 1
                neighborState = myMatrix[neighborStateRow][neighborStateColumn]
                if (self.xInput - self.zInput) > 2:
                    validJump = 0
                else: 
                    validJump = 1
            elif x<z:
                neighborStateRow = w
                neighborStateColumn = x + 1
                neighborState = myMatrix[neighborStateRow][neighborStateColumn]
                if (self.zInput - self.xInput) > 2:
                    validJump = 0
                else: 
                    validJump = 1
        elif x==z:

            if w > y:
                neighborStateRow = w - 1
                neighborStateColumn = x
                neighborState = myMatrix[neighborStateRow][neighborStateColumn]
                if (self.wInput - self.yInput) > 2:
                    validJump = 0
                else: 
                    validJump = 1
            elif w<y:
                neighborStateRow = w + 1
                neighborStateColumn = x
                neighborState = myMatrix[neighborStateRow][neighborStateColumn]
                if (self.yInput - self.wInput) > 2:
                    validJump = 0
                else:                    
                    validJump = 1
                    
        if(validJump==99 and self.initial_x>0 and self.initial_y>0):
            self.OutofRange=True
            
        if self.matrixPosStart != 2 and self.matrixPosEnd == 0 and neighborState == 1 and validJump == 1:
            myMatrix[w][x] = 0
            myMatrix[neighborStateRow][neighborStateColumn] = 0
            myMatrix[y][z] = 1
            myMatrix_colors[y][z]=myMatrix_colors[w][x]
            if sound_enable:
                self.move_sound.play()
            
        else:             
             if(self.OutofRange==True):
                 myMatrix[w][x]=1

        self.screen.blit(self.background,(0,0))
        row=106
        for k in range(7):  
            start=292         
            for i in range(7):
                self.pngNumber=myMatrix_colors[k][i]
                      
                if(myMatrix[k][i]==1): 
                    if self.pngNumber==marbleColor:                        
                        self.screen.blit(self.marble_images[self.pngNumber],(start,row))
                    else:
        
                        self.pngNumber-=100
                        self.screen.blit(self.special_marbles[self.pngNumber],(start,row))                       
        
                start+=90                        
            row+=90        
        
        #reseting the values back
        self.OutofRange=True 
        self.initial_x=0
        self.initial_y=0      
        self.update_moves()
        self.display()
        
    def changePosition(self):
        global marbleColor,special_x,special_y
        self.x=pygame.mouse.get_pos()
        x=self.x[0]    
        y=self.x[1]
        x = (x // 90) - (300 // 90)
        y = (y // 90) - (120 // 90)
        #self.Number=0
        
        #print "marble  color is :",marbleColor
        if(x>=0 and x<7 and y>=0 and y<7):
            if self.pressed==False and myMatrix[y][x]==1:
                myMatrix[y][x]=0
                self.Number=myMatrix_colors[y][x]
         
                if self.Number>=100:
                    special_x=y
                    special_y=x
         
                self.initial_x=y
                self.initial_y=x
        
        self.selected=True
        self.pressed=True 
        if self.Number==marbleColor:
            self.marble_rect=self.marble_images[self.Number].get_rect()
        elif self.Number==25:
            self.marble_rect=self.marble_images[self.Number].get_rect()
        else:
            self.marble_rect=self.special_marbles[self.Number-100].get_rect()
            
        self.marble_rect.center=pygame.mouse.get_pos()
        self.screen.blit(self.background,(0,0))
        
        
        row=106        
        for k in range(7):
            start=292           
            for i in range(7):
                self.pngNumber=myMatrix_colors[k][i]
                                    
                if(myMatrix[k][i]==1):
        
                    if self.pngNumber==marbleColor:                        
                        self.screen.blit(self.marble_images[self.pngNumber],(start,row))
                    
                    else:
                        self.pngNumber-=100
        
                        self.screen.blit(self.special_marbles[self.pngNumber],(start,row))
                start+=90                        
            row+=90
        

        if self.Number==marbleColor:
            self.screen.blit(self.marble_images[self.Number],self.marble_rect)
        elif self.Number==25:
            self.screen.blit(self.marble_images[self.Number],self.marble_rect)
        else:

            self.screen.blit(self.special_marbles[self.Number-100],self.marble_rect)
        
    def moving(self):
        row=90
        self.screen.blit(self.background,self.marble_rect,self.marble_rect)       
       
        self.marble_rect.center=pygame.mouse.get_pos()
        self.screen.blit(self.marble_images[self.Number],self.marble_rect)

    def noMoreMoves(self):
        global button1
        rollover_once=0
        run=1
        self.alphasurface = pygame.Surface((1280,825))
        self.alphasurface.convert()
        self.alphasurfacerect = pygame.Rect(0,0,1280,825)
        self.alphasurface.fill((100,100,100))
        self.alphasurface.set_alpha(200)
        self.screen.blit(self.background, (0,0))
        row=106
        for k in range(7):  
            start=292         
            for i in range(7):
                self.pngNumber=myMatrix_colors[k][i]
                if(myMatrix[k][i]==1):   
                    if self.pngNumber==marbleColor:                        
                        self.screen.blit(self.marble_images[self.pngNumber],(start,row))
                    else:
                        self.pngNumber-=100
                        self.screen.blit(self.special_marbles[self.pngNumber],(start,row))                                
                start+=90                        
            row+=90     
        
        self.display()
        self.screen.blit(self.alphasurface,self.alphasurfacerect)
        
        while run:

            while Gtk.events_pending():
                Gtk.main_iteration()

            for event in pygame.event.get():
                
                if event.type == QUIT or (event.type == KEYDOWN and 
                                          event.key in [K_ESCAPE]):sys.exit()                                           
                
                
                elif event.type == MOUSEBUTTONDOWN:
                    if button1.is_focused():
                        button1.press()                    
                elif event.type == MOUSEBUTTONUP:
                    if button1.status == 1:
                        button1.unpress()
                        self.play_var = 1
                        run = 0                    
                
                if self.play_var==1:
                    self.play_var=0
                    self.reset()
                    self.reset_board()
                    self.SuperLooper()
                    
            if (button1.rect.collidepoint(pygame.mouse.get_pos()) and rollover_once==0):
                rollover_once=1     
                self.allsprites.remove(button1)
                button1 = simple_button(31,614,'NewBoardOn.png',None)
                self.allsprites=pygame.sprite.RenderPlain(button1)
                self.allsprites.draw(self.screen)
            elif not (button1.rect.collidepoint(pygame.mouse.get_pos())):
                rollover_once=0
                button1 = simple_button(31,614,'NewBoard.png',None)
                self.allsprites=pygame.sprite.RenderPlain(button1)
                self.allsprites.draw(self.screen)
            pygame.display.update()
            fpsClock.tick(FPS)
 
    def SuperLooper(self):
        
        global button1,helpoff,marbleColor,next_marble,count,sound_enable,FPS, fpsClock
        rollover_once=0
        run=1
        FPS = 30
        fpsClock = pygame.time.Clock()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
                break

        self.load_things()

        self.background = load_image("Background2.png")
        self.play_var=0
        self.help_var=0
        self.play_sound=False
        self.pickedSound=0
        pygame.mouse.set_cursor((32, 32), (0, 0), ARROW_0, ARROW_1)
        group=[]
        empty=()
        self.displaying_arrow=False
        self.screen.blit(self.background, (0,0))
        
        button1 = simple_button(31,614,'NewBoard.png',None)
        self.allsprites=pygame.sprite.RenderPlain(button1)
        self.allsprites.empty()
        self.allsprites.draw(self.screen)
        helpoff=simple_button(970,614,'HelpOff.png',None)
        self.allspritess=pygame.sprite.RenderPlain(helpoff)
        self.LoadSprites()
        self.marble_rect=self.marble_images[self.Number].get_rect()
        self.marble_rect.center=pygame.mouse.get_pos()
        
        #onscreen text
        marble_text = self.font.render(str(self.updated_text), 1, BROWN_COLOR)
        marble_textpos = marble_text.get_rect(topleft=(1000,50))
        #self.screen.blit(marble_text, marble_textpos)
        
        self.screen.blit(self.special_marbles[next_marble-1],(1067,45))
        
        self.rollover_images=[]
        self.rollover_images.append(load_image("Arrow1.png"))
        self.rollover_images.append(load_image("Arrow2.png"))
        self.rollover_images.append(load_image("Arrow3.png"))
        self.rollover_images.append(load_image("Arrow4.png"))
        pygame.display.update()
        fpsClock.tick(FPS)
        while run:
            #condition for checking for mouse arrows
            if(self.updated_text==32):
                if (self.displaying_arrow==False and pygame.mouse.get_pos()[0]>=550 and pygame.mouse.get_pos()[0]<=625
                    and pygame.mouse.get_pos()[1]>=550 and pygame.mouse.get_pos()[1]<=625):                                
                    self.screen.blit(self.rollover_images[3],(520,380))            
                    self.displaying_arrow=True
                    
                if (self.displaying_arrow==False and pygame.mouse.get_pos()[0]>=550 and pygame.mouse.get_pos()[0]<=625
                    and pygame.mouse.get_pos()[1]>=175 and pygame.mouse.get_pos()[1]<=275):
                    self.screen.blit(self.rollover_images[2],(550,200))
                    self.displaying_arrow=True
                    
                if (self.displaying_arrow==False and pygame.mouse.get_pos()[0]>=400 and pygame.mouse.get_pos()[0]<=450
                    and pygame.mouse.get_pos()[1]>=375 and pygame.mouse.get_pos()[1]<=425):
                    self.screen.blit(self.rollover_images[1],(400,350))
                    self.displaying_arrow=True
                    
                if (self.displaying_arrow==False and pygame.mouse.get_pos()[0]>=700 and pygame.mouse.get_pos()[0]<=800
                    and pygame.mouse.get_pos()[1]>=375 and pygame.mouse.get_pos()[1]<=450):
                    self.screen.blit(self.rollover_images[0],(550,350))
                    self.displaying_arrow=True
                    
                
            if (button1.rect.collidepoint(pygame.mouse.get_pos()) and rollover_once==0):
                rollover_once=1                                
                self.allsprites.remove(button1)
                button1 = simple_button(31,614,'NewBoardOn.png',None)
                self.allsprites=pygame.sprite.RenderPlain(button1)
                self.allsprites.draw(self.screen)
           
            elif not (button1.rect.collidepoint(pygame.mouse.get_pos())):             
                rollover_once=0
                self.allsprites.empty()
                button1 = simple_button(31,614,'NewBoard.png',None)
                self.allsprites=pygame.sprite.RenderPlain(button1)
                self.allsprites.draw(self.screen)
  
            if (helpoff.rect.collidepoint(pygame.mouse.get_pos()) and rollover_onces==0):
                rollover_onces=1
                self.allspritess.remove(button1)
                helpoff = simple_button(970,614,'HelpOn.png',None)
                self.allspritess=pygame.sprite.RenderPlain(helpoff)
                self.allspritess.draw(self.screen)
           
            elif not (helpoff.rect.collidepoint(pygame.mouse.get_pos())):             
                
                rollover_onces=0                
                helpoff = simple_button(970,614,'HelpOff.png',None)
                self.allspritess=pygame.sprite.RenderPlain(helpoff)
                self.allspritess.draw(self.screen)

            temp_pos=pygame.mouse.get_pressed()
            if temp_pos[0]==0 and self.selected==True and self.pressed==True:
                self.pressed=False
                self.selected=False
                self.checkValidMovement()
                self.Number=25#26    25
                self.picked=False
                self.displaying_arrow=False
                '''Change the cursor to an arrow'''
                pygame.mouse.set_cursor((32, 32), (0, 0), ARROW_0, ARROW_1)
                self.pickedSound=0
                
            if temp_pos[0]==1 : #and self.picked==False:
                '''Change the cursor to an X'''
                pygame.mouse.set_cursor((32, 32), (0, 0), CROSS_0, CROSS_1 )
                self.picked=True
                
                if self.pickedSound == 0:
                    if sound_enable:
                        self.picked_sound.play()
                    self.pickedSound=1
                self.changePosition()
                self.display()

            while Gtk.events_pending():
                Gtk.main_iteration()
                
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and 
                                          event.key in [K_ESCAPE]):sys.exit()                                           
                
                
                elif event.type == MOUSEBUTTONDOWN:
                    if button1.is_focused():
                        button1.press()
                    elif helpoff.is_focused():                        
                        helpoff.press()                    
                elif event.type == MOUSEBUTTONUP:
                    if button1.status == 1:
                        button1.unpress()
                        self.play_var = 1
                        run=0
                    elif helpoff.status == 1:
                        helpoff.unpress()
                        self.help_var = 1
                        #run=0                                
                
                if self.play_var==1:
                    self.play_var=0
                    self.reset()
                    self.reset_board()
                    self.SuperLooper()
                if self.help_var==1:
                    self.help_var=0
                    self.help_screen()

            pygame.display.update()
            fpsClock.tick(FPS)

            if self.updated_text==28 and self.play_sound==False and count==0:
                if sound_enable:
                    self.level_sounds[0].play()
                count+=1
                self.play_sound=True
            elif self.updated_text==24 and self.play_sound==False and count==1:
                if sound_enable:
                    self.level_sounds[1].play()
                self.play_sound=False
                count+=1
            elif self.updated_text==20 and self.play_sound==False and count==2:
                if sound_enable:
                    self.level_sounds[2].play()
                self.play_sound=True
                count+=1
            elif self.updated_text==16 and self.play_sound==False and count==3:
                if sound_enable:
                    self.level_sounds[3].play()
                self.play_sound=True
                count+=1
            elif self.updated_text==12 and self.play_sound==False and count==4:
                if sound_enable:
                    self.level_sounds[4].play()
                self.play_sound=True
                count+=1
            elif self.updated_text==8 and self.play_sound==False and count==5:
                if sound_enable:
                    self.level_sounds[5].play()
                self.play_sound=True
                count+=1
            elif self.updated_text==4 and self.play_sound==False and count==6:
                if sound_enable:
                    self.level_sounds[6].play()
                self.play_sound=True
                count+=1
                
            if self.updated_moves==0:
                if self.updated_text==1:
                    if sound_enable:
                        self.level_sounds[7].play()
                    number = 0                    
                run=0                
                self.noMoreMoves()
                
    def help_screen(self):
        
        run=True
        self.alphasurface = pygame.Surface((1280,825))
        self.alphasurface.convert()
        self.alphasurfacerect = pygame.Rect(0,0,1280,825)
        self.alphasurface.fill((100,100,100))
        self.alphasurface.set_alpha(200)
        self.screen.blit(self.alphasurface,self.alphasurfacerect)            
        self.screen.blit(self.helpscreen,(0,0))
        pygame.display.update()
        fpsClock.tick(FPS)

        while run:
            while Gtk.events_pending():
                Gtk.main_iteration()

            for event in pygame.event.get():
                
                if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                    run =0
            
        
    def update_moves(self):        
        marblesLeft = 0
        movesLeft = 0
        i = 0
        while i < myMatrixGridSize: # should eventually be length of rows
            j = 0
            while j < myMatrixGridSize: # should eventually be length of columns
                m = myMatrix[i][j]
                if m == 1: # there is a marble in the slot
                    marblesLeft = marblesLeft + 1
                    boundsCheck = i - 1
                    if boundsCheck >= 0:
                        mn = myMatrix[i -1][j]
                        if mn == 0: # no move directly above
                            pass
                        else:
                            pass
                        boundsCheck = i - 2
                        if boundsCheck >= 0:
                            mn = myMatrix[i - 2][j]
                            mn2 = myMatrix[i - 1][j]
                            if mn == 0 and mn2 == 1:
                                #print "There is a move above."
                                movesLeft = movesLeft + 1 
                            else:
                                pass
                    else: # there is a move above, but is the slot above that empty
                        pass
                    boundsCheck = i + 1
                    if boundsCheck < myMatrixGridSize: # needs to be drawn from the number of rows eventually
                        mn = myMatrix[i + 1][j]
                        if mn == 0: # no move directly below
                            pass
                        else:
                            pass
                        boundsCheck = i + 2
                        if boundsCheck < myMatrixGridSize:
                            mn = myMatrix[i + 2][j]
                            mn2 = myMatrix[i + 1][j]
                            if mn == 0 and mn2 == 1:
                                movesLeft = movesLeft + 1 
                            else:
                                pass
                    else: # there is a move below, but is the slot below that empty
                        pass
                    boundsCheck = j - 1
                    if boundsCheck >= 0: # needs to be drawn from the number of rows eventually
                        mn = myMatrix[i][j - 1]
                        if mn == 0: # no move directly to the left
                            pass
                        else:
                            pass
                        boundsCheck = j - 2
                        if boundsCheck >= 0:
                            mn = myMatrix[i][j - 2]
                            mn2 = myMatrix[i][j - 1]
                            if mn == 0 and mn2 == 1:
                                movesLeft = movesLeft + 1 
                            else:
                                pass
                    else: # there is a move below, but is the slot below that empty
                        pass
                    #check right
                    boundsCheck = j + 1
                    if boundsCheck < myMatrixGridSize: # needs to be drawn from the number of rows eventually
                        mn = myMatrix[i][j + 1]
                        if mn == 0: # no move directly to the right
                            pass
                        else:
                            pass
                        boundsCheck = j + 2
                        if boundsCheck < myMatrixGridSize:
                            mn = myMatrix[i][j + 2]
                            mn2 = myMatrix[i][j + 1]
                            if mn == 0 and mn2 == 1:
                                movesLeft = movesLeft + 1 
                            else:
                                pass
                    else: # there is a move below, but is the slot below that empty
                        pass
                else: # There is no marble in the slot
                    pass
    
                        
                j = j + 1
            i = i + 1
        
        self.updated_text=marblesLeft
        
        self.updated_moves= movesLeft
        return

    def display(self):
        global button1,helpoff,next_marble
        marble_text = self.font.render(str(self.updated_text), 1, BROWN_COLOR)
        marble_textpos = marble_text.get_rect(topleft=(1000,50))
        #self.screen.blit(marble_text, marble_textpos)
        #flag conditions
        if(self.updated_text<=28 and self.updated_text>24):# and count==0):
            self.screen.blit(self.flags[0],(1038,110))
                        
        elif(self.updated_text<=24 and self.updated_text>20):# and count==2):
            self.screen.blit(self.flags[1], (1038,110))
            self.play_sound=False
        elif(self.updated_text<=20 and self.updated_text>16):
            self.screen.blit(self.flags[2], (1038,110))
            self.play_sound=False
        elif(self.updated_text<=16 and self.updated_text>12):
            self.screen.blit(self.flags[3],(1038,110))
            self.play_sound=False
        elif(self.updated_text<=12 and self.updated_text>8):
            self.screen.blit(self.flags[4],(1038,110))
            self.play_sound=False
        elif(self.updated_text<=8 and self.updated_text>4):
            self.screen.blit(self.flags[5],(1038,110))
            self.play_sound=False
        elif(self.updated_text<=4 and self.updated_text>1):
            self.screen.blit(self.flags[6], (1038,110))
            self.play_sound=False           
        
        self.screen.blit(self.special_marbles[next_marble-1],(1067,45)) 
        self.allsprites.draw(self.screen)
        if self.updated_moves>0:
            self.allspritess.draw(self.screen)
        
    def LoadSprites(self):
        global marbleColor,next_marble
        """Create the Marbles group"""         
        n=7        
        row=106 #120        
        
        marbleColor = random.randrange(0,23)

        number=0

        next_marble=number+1
        
        row=106           
        #function for generating the dots using matrix method
        for k in range(7):  
            start=292
            for i in range(7):     
                if(myMatrix[k][i]==1):
                    pngNumber=marbleColor                            
                    myMatrix_colors[k][i]=pngNumber
                    self.screen.blit(self.marble_images[pngNumber],(start,row))
                start+=90
            row+=90
            
        
        for k in range(7):        
            for i in range(7):     
                if(myMatrix[k][i]==3):
                    myMatrix[k][i]=1
        
        
        
def main():
    pygame.init()
    MainWindow = SolitaireMain()    
    MainWindow.SuperLooper()
       
if __name__=="__main__":
    main()
