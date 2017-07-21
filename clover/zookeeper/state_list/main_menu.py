from zookeeper_screen_recognition import classifier_main_menu_button
from clover.common import draw_util
import os

BUTTON_XY = (166+(308/2), 174+(188/2))
NEXT_ITEM_BUTTON_XY = (551+(60/2), 341+(54/2))

def init(bot_logic):
    bot_logic.main_menu_button_clr = classifier_main_menu_button.MainMenuButtonClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_main_menu_button.MODEL_PATH))
    bot_logic.main_menu_cooldown = 0

def tick(bot_logic, img, arm, t, ret):
    if t < bot_logic.main_menu_cooldown:
        return False
    if arm and (arm['is_moving']):
        return False

    ret['main_menu_data'] = {}
    rret = ret['main_menu_data']

    button_label, _ = bot_logic.main_menu_button_clr.predict(img)
    rret['button_label'] = button_label

    if arm:
        if button_label == 'a_practice':
            target_xy = BUTTON_XY
        else:
            target_xy = NEXT_ITEM_BUTTON_XY
        ret['arm_move_list'] = [
            (arm['xyz'][:2])+(0,),
            target_xy+(0,),
            target_xy+(1,),
            target_xy+(0,)
        ]
        bot_logic.main_menu_cooldown = t + 1
    
    return True

def draw(screen, tick_result):
    ret = tick_result['main_menu_data']

    screen.blit(draw_util.text(ret['button_label'],(0,0,0)), (240,20))
