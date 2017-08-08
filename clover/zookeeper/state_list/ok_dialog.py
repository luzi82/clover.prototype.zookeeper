import os
import sys
import numpy as np
import pygame

from zookeeper_screen_recognition import classifier_ok
from clover.common import draw_util
from clover.zookeeper import bot

IMG_SHAPE = (bot.VIDEO_SIZE[1], bot.VIDEO_SIZE[0], 3)

def init(bot_logic):
    bot_logic.battle_result_cooldown_0 = 0
    bot_logic.battle_result_cooldown_1 = 0
    bot_logic.battle_result_cooldown_2 = 0

    bot_logic.ok_clr = classifier_ok.OkClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_ok.MODEL_PATH))

    dummy_img = np.zeros(IMG_SHAPE)
    bot_logic.ok_clr.get_ok(dummy_img)

def tick(bot_logic, img, arm, t, ret):
    if t < bot_logic.battle_result_cooldown_0:
        return False
    elif t < bot_logic.battle_result_cooldown_1:
        y,_ = bot_logic.ok_clr.get_ok(img)

        ret['ok_dialog_y'] = y
        
        if y != None:
            x = 320
            y *= 1136 # hardcode
            y /= bot.VIDEO_SIZE[1]
        
            ret['arm_move_list'] = [
                (arm['xyz'][:2])+(0,),
                (x,y,0),
                (x,y,1),
                (x,y,0)
            ]
            
            bot_logic.battle_result_cooldown_0 = 0
            bot_logic.battle_result_cooldown_1 = 0
        return True
    elif t < bot_logic.battle_result_cooldown_2:
        return False
    else:
        bot_logic.battle_result_cooldown_0 = t+3
        bot_logic.battle_result_cooldown_1 = t+6
        bot_logic.battle_result_cooldown_2 = t+9
        return False

DRAW_SCREEN_XY = np.array([120,0])

def draw(screen, tick_result):
    if 'ok_dialog_y' in tick_result:
        y = tick_result['ok_dialog_y']
        if y != None:
            xy = np.array([60,(tick_result['ok_dialog_y'])])
            draw_xy = xy + DRAW_SCREEN_XY
            draw_xy00 = draw_xy+np.array([-4,-4])
            draw_xy01 = draw_xy+np.array([-4, 4])
            draw_xy10 = draw_xy+np.array([ 4,-4])
            draw_xy11 = draw_xy+np.array([ 4, 4])
            pygame.draw.line(screen, (255,0,0), tuple(draw_xy00), tuple(draw_xy11), 4)
            pygame.draw.line(screen, (255,0,0), tuple(draw_xy01), tuple(draw_xy10), 4)
        else:
            screen.blit(draw_util.text('y==None',(0,0,0)), (240,20))
