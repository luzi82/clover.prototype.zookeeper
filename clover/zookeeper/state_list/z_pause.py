from clover.common import draw_util
import os
import sys

MY_NAME = 'z_pause'
BUTTON_XYZ = 320, -100, 0

def init(bot_logic):
    bot_logic.v[MY_NAME] = {}
    vv = bot_logic.v[MY_NAME]
    vv['cooldown_0'] = 0
    vv['cooldown_1'] = 0
    vv['cooldown_2'] = 0

def start(bot_logic, t):
    vv = bot_logic.v[MY_NAME]
    vv['cooldown_0'] = t+0
    vv['cooldown_1'] = t+3
    vv['cooldown_2'] = t+6

def tick(bot_logic, img, arm, t, ret):
    vv = bot_logic.v[MY_NAME]
    if t < vv['cooldown_0']:
        return True
    elif t < vv['cooldown_1']:
        ret['arm_move_list'] = [
            (arm['xyz'][:2])+(0,),
            BUTTON_XYZ
        ]
        vv['cooldown_0'] = 0
        vv['cooldown_1'] = 0
        vv['cooldown_2'] = t+3
        return True
    elif t < vv['cooldown_2']:
        return True
    else:
        vv['cooldown_0'] = t+0
        vv['cooldown_1'] = t+3
        vv['cooldown_2'] = t+6
        return True

def draw(screen, tick_result):
    pass
