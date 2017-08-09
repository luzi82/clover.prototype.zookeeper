import numpy as np
import pygame
import os
import json
from clover.common import draw_util

from zookeeper_screen_recognition import classifier_state
from clover.zookeeper.state_list import battle
from clover.zookeeper.state_list import battle_result
from clover.zookeeper.state_list import limited_time_sale
from clover.zookeeper.state_list import main_menu
from clover.zookeeper.state_list import ok_dialog
from clover.zookeeper.state_list import title
from clover.zookeeper.state_list import z_pause
from . import bot
from clover import common

SCREEN_SIZE = bot.SCREEN_SIZE
STATE_CLR_MODEL_PATH = os.path.join('dependency','zookeeper_screen_recognition','model')

BTN_SIZE = 30
PLAY_BTN_RECT = (SCREEN_SIZE[0]-BTN_SIZE,SCREEN_SIZE[1]-BTN_SIZE,SCREEN_SIZE[0],SCREEN_SIZE[1])

class BotLogic:

    def __init__(self):
        self.state_op_dict = {}
        self.state_op_dict['battle'] = battle
        self.state_op_dict['battle_result'] = battle_result
        self.state_op_dict['limited_time_sale'] = limited_time_sale
        self.state_op_dict['main_menu'] = main_menu
        self.state_op_dict['ok_dialog'] = ok_dialog
        self.state_op_dict['title'] = title

        self.play = False

    def init(self):
        self.state_clr = classifier_state.StateClassifier(STATE_CLR_MODEL_PATH)
        for _, state_op in self.state_op_dict.items():
            state_op.init(self)

    def on_event(self,event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if common.in_rect(pos,PLAY_BTN_RECT):
                self.play = not self.play

    def tick(self,img,arm_data,time_s):
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

#    def render_state(self, screen, state):
#        if not hasattr(self, 'state_render_dict'):
#            self.state_render_dict = {}
#        if not hasattr(self, 'state_render_font'):
#            self.state_render_font = pygame.font.SysFont("monospace", 15)
#        if not state in self.state_render_dict:
#            self.state_render_dict[state] = self.state_render_font.render(state, 1, (0,0,0))
#        screen.blit(self.state_render_dict[state], (240,0))
            
