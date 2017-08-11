import os
import sys

from zookeeper_screen_recognition import classifier_main_menu_button
from clover.common import draw_util
import clover.zookeeper.state_list as state_common

MY_NAME = 'main_menu'
BUTTON_XY = (166+(308/2), 174+(188/2))
NEXT_ITEM_BUTTON_XY = (551+(60/2), 341+(54/2))

def init(bot_logic):
    bot_logic.main_menu_button_clr = classifier_main_menu_button.MainMenuButtonClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_main_menu_button.MODEL_PATH))
    bot_logic.main_menu_button_clr.predict(state_common.DUMMY_IMG)
    bot_logic.main_menu_cooldown = 0

    bot_logic.v[MY_NAME] = {}
    vv = bot_logic.v[MY_NAME]
    vv['cooldown_0'] = 0
    vv['cooldown_1'] = 0
    vv['cooldown_2'] = 0

def start(bot_logic, t):
    vv = bot_logic.v[MY_NAME]
    vv['cooldown_0'] = t+3
    vv['cooldown_1'] = t+6
    vv['cooldown_2'] = t+9

def tick(bot_logic, img, arm, t, ret):
    vv = bot_logic.v[MY_NAME]

    ret['main_menu_data'] = {}
    rret = ret['main_menu_data']

    button_label, _ = bot_logic.main_menu_button_clr.predict(img)
    rret['button_label'] = button_label

    cp, _ = bot_logic.common_cp_clr.predict(img)
    rret['cp'] = cp

    target_label = 'a_practice' if cp == 'cp0' else 'a_vs'
    #target_label = 'a_practice'
    target_xy = None

    if not arm:
        pass
    elif button_label == target_label:
        target_xy = BUTTON_XY
        #pass
    elif button_label[:2] == 'a_':
        target_xy = NEXT_ITEM_BUTTON_XY

    if t < vv['cooldown_0']:
        return True
    elif t < vv['cooldown_1']:
        ret['arm_move_list'] = [
            (arm['xyz'][:2])+(0,),
            target_xy+(0,),
            target_xy+(1,),
            target_xy+(0,)
        ]
        vv['cooldown_0'] = 0
        vv['cooldown_1'] = 0
        vv['cooldown_2'] = t+3
        return True
    elif t < vv['cooldown_2']:
        return True
    else:
        vv['cooldown_0'] = t+3
        vv['cooldown_1'] = t+6
        vv['cooldown_2'] = t+9
        return True

def draw(screen, tick_result):
    ret = tick_result['main_menu_data']

    screen.blit(draw_util.text(ret['button_label'],(0,0,0)), (240,20))
