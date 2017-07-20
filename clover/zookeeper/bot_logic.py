import numpy as np
import pygame
import os
import json
from clover.common import draw_util

from zookeeper_screen_recognition import classifier_state
from clover.zookeeper.state_list import battle
from clover.zookeeper.state_list import main_menu

STATE_CLR_MODEL_PATH = os.path.join('dependency','zookeeper_screen_recognition','model')

class BotLogic:

    def __init__(self):
        self.state_op_dict = {}
        self.state_op_dict['battle'] = battle
        self.state_op_dict['main_menu'] = main_menu

    def init(self):
        self.state_clr = classifier_state.StateClassifier(STATE_CLR_MODEL_PATH)
        for _, state_op in self.state_op_dict.items():
            state_op.init(self)

    def tick(self,img):
        img = img.astype('float32')*2/255-1
        
        state, _ = self.state_clr.get_state(img)
        ret = {
            'state': state
        }

#        if state == 'battle':
#            battle.tick(self, img, ret)
        if state in self.state_op_dict:
            self.state_op_dict[state].tick(self, img, ret)

        #print(json.dumps(ret))

        return ret

    
    def draw(self, screen, tick_result):
        state = tick_result['state']
        screen.blit(draw_util.text(state,(0,0,0)), (240,0))
        #self.render_state(screen, state)
        if state in self.state_op_dict:
            self.state_op_dict[state].draw(screen, tick_result)
#        if tick_result['state'] == 'battle':
#            battle.draw(screen, tick_result)

#    def render_state(self, screen, state):
#        if not hasattr(self, 'state_render_dict'):
#            self.state_render_dict = {}
#        if not hasattr(self, 'state_render_font'):
#            self.state_render_font = pygame.font.SysFont("monospace", 15)
#        if not state in self.state_render_dict:
#            self.state_render_dict[state] = self.state_render_font.render(state, 1, (0,0,0))
#        screen.blit(self.state_render_dict[state], (240,0))
            
            