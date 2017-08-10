from clover.common import draw_util
import os
import sys

BUTTON_XY = ((40+(48/2))*640/120, (147+(18/2))*1136/213)

def init(bot_logic):
    bot_logic.battle_result_cooldown_0 = 0
    bot_logic.battle_result_cooldown_1 = 0
    bot_logic.battle_result_cooldown_2 = 0

def tick(bot_logic, img, arm, t, ret):
    if t < bot_logic.battle_result_cooldown_0:
        return True
    elif t < bot_logic.battle_result_cooldown_1:
        ret['arm_move_list'] = [
            (arm['xyz'][:2])+(0,),
            BUTTON_XY+(0,),
            BUTTON_XY+(1,),
            BUTTON_XY+(0,)
        ]
        bot_logic.battle_result_cooldown_0 = 0
        bot_logic.battle_result_cooldown_1 = 0
        return True
    elif t < bot_logic.battle_result_cooldown_2:
        return True
    else:
        bot_logic.battle_result_cooldown_0 = t+3
        bot_logic.battle_result_cooldown_1 = t+6
        bot_logic.battle_result_cooldown_2 = t+9
        return True

def draw(screen, tick_result):
    pass
