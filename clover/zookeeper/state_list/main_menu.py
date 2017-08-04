from zookeeper_screen_recognition import classifier_main_menu_button
from clover.common import draw_util
import os
import sys

BUTTON_XY = (166+(308/2), 174+(188/2))
NEXT_ITEM_BUTTON_XY = (551+(60/2), 341+(54/2))

def init(bot_logic):
    bot_logic.main_menu_button_clr = classifier_main_menu_button.MainMenuButtonClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_main_menu_button.MODEL_PATH))
    bot_logic.main_menu_cooldown = 0

def tick(bot_logic, img, arm, t, ret):
    if t < bot_logic.main_menu_cooldown:
        # print('IVRWEGUZPS t < bot_logic.main_menu_cooldown',file=sys.stderr)
        return False
    if arm and (arm['is_busy']):
        # print('PVQYDYNBCE is_busy',file=sys.stderr)
        return False

    ret['main_menu_data'] = {}
    rret = ret['main_menu_data']

    button_label, _ = bot_logic.main_menu_button_clr.predict(img)
    rret['button_label'] = button_label

    target_xy = None

    if not arm:
        pass
    elif button_label == 'a_practice':
        #target_xy = BUTTON_XY
        pass
    elif button_label[:2] == 'a_':
        target_xy = NEXT_ITEM_BUTTON_XY

    if target_xy:
        ret['arm'] = [
            (arm['xyz'][:2])+(0,),
            target_xy+(0,),
            target_xy+(1,),
            target_xy+(0,)
        ]
        bot_logic.main_menu_cooldown = t + 3

    return True

def draw(screen, tick_result):
    ret = tick_result['main_menu_data']

    screen.blit(draw_util.text(ret['button_label'],(0,0,0)), (240,20))
