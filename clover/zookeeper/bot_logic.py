import numpy as np
import pygame
import os

from zookeeper_screen_recognition import classifier_state

STATE_CLR_MODEL_PATH = os.path.join('dependency','zookeeper_screen_recognition','model')

class BotLogic:

    def __init__(self):
        pass

    def init(self):
        self.state_clr = classifier_state.StateClassifier(STATE_CLR_MODEL_PATH)

    def tick(self,img):
        img = img.astype('float32')*2/255-1
        
        state, _ = self.state_clr.get_state(img)

        return {
            'state': state
        }
    
    def draw(self, screen, tick_result):
        self.render_state(screen, tick_result['state'])

    def render_state(self, screen, state):
        if not hasattr(self, 'state_render_dict'):
            self.state_render_dict = {}
        if not hasattr(self, 'state_render_font'):
            self.state_render_font = pygame.font.SysFont("monospace", 15)
        if not state in self.state_render_dict:
            self.state_render_dict[state] = self.state_render_font.render(state, 1, (0,0,0))
        screen.blit(self.state_render_dict[state], (240,0))
            
            