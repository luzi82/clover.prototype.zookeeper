from zookeeper_screen_recognition import classifier_main_menu_button
from clover.common import draw_util
import os

def init(bot_logic):
    bot_logic.main_menu_button_clr = classifier_main_menu_button.MainMenuButtonClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_main_menu_button.MODEL_PATH))

def tick(bot_logic, img, ret):
    ret['main_menu_data'] = {}
    ret = ret['main_menu_data']

    button_label, _ = bot_logic.main_menu_button_clr.predict(img)
    ret['button_label'] = button_label

def draw(screen, tick_result):
    ret = tick_result['main_menu_data']

    screen.blit(draw_util.text(ret['button_label'],(0,0,0)), (240,20))
