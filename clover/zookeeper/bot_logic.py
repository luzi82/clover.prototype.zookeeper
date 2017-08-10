import numpy as np
import pygame
import os
import json
import random
import time
import cv2

from clover.common import draw_util
from zookeeper_screen_recognition import classifier_state
import clover.zookeeper.state_list as state_common
from clover.zookeeper.state_list import battle
from clover.zookeeper.state_list import battle_result
from clover.zookeeper.state_list import boss_henchman_appeared
from clover.zookeeper.state_list import limited_time_sale
from clover.zookeeper.state_list import main_menu
from clover.zookeeper.state_list import mission_boss_invasion
from clover.zookeeper.state_list import ok_dialog
from clover.zookeeper.state_list import title
from clover.zookeeper.state_list import z_pause
from . import bot
from clover import common

SCREEN_SIZE = bot.SCREEN_SIZE
STATE_CLR_MODEL_PATH = os.path.join('dependency','zookeeper_screen_recognition','model')

class BotLogic:

    def __init__(self):
        self.state_op_dict = {}
        self.state_op_dict['battle'] = battle
        self.state_op_dict['battle_result'] = battle_result
        self.state_op_dict['boss_henchman_appeared'] = boss_henchman_appeared
        self.state_op_dict['limited_time_sale'] = limited_time_sale
        self.state_op_dict['main_menu'] = main_menu
        self.state_op_dict['mission_boss_invasion'] = mission_boss_invasion
        self.state_op_dict['ok_dialog'] = ok_dialog
        self.state_op_dict['title'] = title

        self.play = False
        self.cap_screen = False
        
        self.cap_screen_timeout = 0
        self.cap_screen_output_folder = os.path.join('dependency','zookeeper_screen_recognition','raw_image',str(int(time.time()*1000)))

    def init(self):
        self.state_clr = classifier_state.StateClassifier(STATE_CLR_MODEL_PATH)
        state_common.init(self)
        for _, state_op in self.state_op_dict.items():
            state_op.init(self)
        z_pause.init(self)

    def on_event(self,event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if common.in_rect(pos,PLAY_BTN_RECT):
                self.play = not self.play
            if common.in_rect(pos,SCREENCAP_BTN_RECT):
                self.cap_screen = not self.cap_screen

    def tick(self,img,arm_data,time_s):
        if self.cap_screen:
            if time_s >= self.cap_screen_timeout:
                t = int(time_s*1000)
                t0 = int(t/100000)
                fn_dir = os.path.join(self.cap_screen_output_folder,str(t0))
                common.makedirs(fn_dir)
                fn = os.path.join(fn_dir,'{}.png'.format(t))
                cv2.imwrite(fn,img)
                self.cap_screen_timeout = time_s + 0.5 + 0.5*random.random()

        img = img.astype('float32')*2/255-1
        
        state, _ = self.state_clr.get_state(img)
        ret = {
            'state': state,
            'play': self.play
        }

        good = False
        
        if self.play:
            if state in self.state_op_dict:
                good = self.state_op_dict[state].tick(self, img, arm_data, time_s, ret)
        else:
            good = z_pause.tick(self, img, arm_data, time_s, ret)

        #print(json.dumps(ret))

        return ret if good else None

    
    def draw(self, screen, tick_result):
        if tick_result != None:
            state = tick_result['state']
            screen.blit(draw_util.text(state,(0,0,0)), (240,0))
            if tick_result['play']:
                if state in self.state_op_dict:
                    self.state_op_dict[state].draw(screen, tick_result)

        if self.play:
            screen.blit(draw_util.text('P',(0,127,0)), PLAY_BTN_RECT[:2])
        else:
            screen.blit(draw_util.text('S',(127,0,0)), PLAY_BTN_RECT[:2])

        if self.cap_screen:
            screen.blit(draw_util.text('CAP',(127,0,0)), SCREENCAP_BTN_RECT[:2])
        else:
            screen.blit(draw_util.text('NoCAP',(0,127,0)), SCREENCAP_BTN_RECT[:2])

#    def render_state(self, screen, state):
#        if not hasattr(self, 'state_render_dict'):
#            self.state_render_dict = {}
#        if not hasattr(self, 'state_render_font'):
#            self.state_render_font = pygame.font.SysFont("monospace", 15)
#        if not state in self.state_render_dict:
#            self.state_render_dict[state] = self.state_render_font.render(state, 1, (0,0,0))
#        screen.blit(self.state_render_dict[state], (240,0))


BTN_SIZE = 30
def btn_rect(idx):
     return (SCREEN_SIZE[0]-(BTN_SIZE*(idx+1)),SCREEN_SIZE[1]-BTN_SIZE,SCREEN_SIZE[0]-(BTN_SIZE*idx),SCREEN_SIZE[1])
PLAY_BTN_RECT = btn_rect(0)
SCREENCAP_BTN_RECT = btn_rect(1)
