import os
import json
import pygame
import numpy as np
import random
import copy
import sys
import time

from zookeeper_screen_recognition import classifier_board_animal
from zookeeper_screen_recognition import classifier_battle_second
from clover.zookeeper import zookeeper_solver
from clover.zookeeper import bot
from clover.common import draw_util

SIDE_COUNT = 8
IMG_SHAPE = (bot.VIDEO_SIZE[1], bot.VIDEO_SIZE[0], 3)

PHI = (1+5**0.5)/2

ARM_BOARD_RECT = (0,332,640,972) # x0,y0,x1,y1
ARM_BOARD_NE_XY = np.array([ARM_BOARD_RECT[0],ARM_BOARD_RECT[1]])
ARM_BOARD_SW_XY = np.array([ARM_BOARD_RECT[2],ARM_BOARD_RECT[3]])
ARM_BOARD_CENTER_XY = (ARM_BOARD_NE_XY+ARM_BOARD_SW_XY)/2
ARM_BOARD_PARK_XY = ((ARM_BOARD_RECT[0]+ARM_BOARD_RECT[2])/2), (ARM_BOARD_RECT[1]/PHI + ARM_BOARD_RECT[3]/PHI/PHI)
ARM_BOARD_PARK0_XY = ((ARM_BOARD_RECT[0]+ARM_BOARD_RECT[2])/2), 0
ARM_CELL_STEP = 640 / SIDE_COUNT
MOVE_LEN = 640

EAT_FALL_DELAY = 0.9

def init(bot_logic):
    bot_logic.board_animal_clr = classifier_board_animal.BoardAnimalClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_board_animal.MODEL_PATH))
    bot_logic.battle_second_clr = classifier_battle_second.BattleSecondClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_battle_second.MODEL_PATH))

    # warm up clr
    dummy_img = np.zeros(IMG_SHAPE)
    bot_logic.board_animal_clr.predict(dummy_img)
    bot_logic.battle_second_clr.predict(dummy_img)

    # var
    bot_logic.battle_target_move = None
    bot_logic.battle_target_move_last = None
    bot_logic.cell_age = [[0 for _ in range(SIDE_COUNT)] for _ in range(SIDE_COUNT)]
    
    bot_logic.battle_s00_park_timeout = 0

    bot_logic.battle_s30_park_timeout = 0
    bot_logic.battle_last_s30_time = 0

def tick(bot_logic, img, arm, t, ret):
    if arm and (arm['is_busy']):
        return False

    #print('{:.3f} VQSRVEVBZG battle logic free'.format(time.time()))

    if bot_logic.battle_target_move_last:
        last_move = bot_logic.battle_target_move_last
        if (last_move['type'] == 'h') or (last_move['type'] == 'v'):
            bot_logic.cell_age[last_move['x0']][last_move['y0']] = t + EAT_FALL_DELAY
            bot_logic.cell_age[last_move['x1']][last_move['y1']] = t + EAT_FALL_DELAY
            for x,y in last_move['clear_animal_list']:
                bot_logic.cell_age[x][y] = t + EAT_FALL_DELAY
        elif last_move['type'] == 'i':
            bot_logic.cell_age[last_move['x0']][last_move['y0']] = t + EAT_FALL_DELAY
        bot_logic.battle_target_move_last = None

    ret['battle_data'] = {}
    ret_root = ret
    ret = ret['battle_data']
    
    battle_second, _ = bot_logic.battle_second_clr.predict(img)
    ret['battle_second'] = battle_second

    # park pen
    if (battle_second == 's00') and (bot_logic.battle_s00_park_timeout < t):
        ret_root['arm_move_list'] = [
            ARM_BOARD_PARK0_XY+(0,)
        ]
        bot_logic.battle_s00_park_timeout = t+5
        return True
    if (battle_second == 's30') and (bot_logic.battle_s30_park_timeout < t):
        ret_root['arm_move_list'] = [
            ARM_BOARD_PARK_XY+(0,)
        ]
        bot_logic.battle_s30_park_timeout = t+30
        return True

    if (battle_second == 's30'):
        bot_logic.battle_last_s30_time = t

    if battle_second != 'sxx':
        #print('{:.3f} MNRPKGALAW battle non sxx'.format(time.time()))
        bot_logic.battle_target_move = None
        return True

    #print('{:.3f} YWNYWWSISL battle logic start'.format(time.time()))

    board_animal_list, _ = bot_logic.board_animal_clr.predict(img)
    board_animal_list_list = [[board_animal_list[i+j*SIDE_COUNT] for j in range(SIDE_COUNT)] for i in range(SIDE_COUNT)]
    age_list_list = [[False for _ in range(SIDE_COUNT)] for _ in range(SIDE_COUNT)]
    for i in range(SIDE_COUNT):
        for j in range(SIDE_COUNT):
            if bot_logic.cell_age[i][j] > t:
                board_animal_list_list[i][j] = 'z_chao'
                age_list_list[i][j] = True
    ret['board_animal_list_list'] = board_animal_list_list
    ret['age_list_list'] = age_list_list
    
    _, move_list = zookeeper_solver.solve(board_animal_list_list, t>bot_logic.battle_last_s30_time+25)
    if len(move_list) > 0:
        best_score = max([move['score'] for move in move_list])
        for move in move_list:
            move['is_best'] = move['score'] >= best_score
    ret['move_list'] = move_list

    if arm:
        arm_xy = np.array(arm['last_pos'][:2])

        #if arm['xyz'][2] > 0.5:
        #    print('{:.3f} FEUFVDWOBD arm[xyz][2] > 0.5'.format(time.time()),file=sys.stderr)
        #    ret_root['arm_move_list'] = [np.append(arm_xy,[0])]

        if (bot_logic.battle_target_move == None) and (len(move_list)<=0):
            #print('{:.3f} DDMKUKDGPG bot_logic.battle_target_move == None'.format(time.time()),file=sys.stderr)
            #tar_xy, already_arrive, _ = _move(arm_xy, ARM_BOARD_CENTER_XY)
            #if (not already_arrive):
            #    ret_root['arm_move_list'] = [np.append(tar_xy,[0])]
            pass

        elif bot_logic.battle_target_move == None:
            #print('{:.3f} MZANYUGXDN bot_logic.battle_target_move == None'.format(time.time()),file=sys.stderr)
            _best_move_list = list(filter(lambda move:move['is_best'],move_list))
            best_move_list = []
            for move in _best_move_list:
                if (move['type'] == 'h') or (move['type'] == 'v'):
                    xy0 = _logic2arm(move['x0'],move['y0'])
                    xy1 = _logic2arm(move['x1'],move['y1'])
            
                    if move['i0'][:2] == 'a_':
                        m = copy.copy(move)
                        m['xy0'] = xy0
                        m['xy1'] = xy1
                        best_move_list.append(m)
            
                    if move['i1'][:2] == 'a_':
                        m = copy.copy(move)
                        m['xy0'] = xy1
                        m['xy1'] = xy0
                        best_move_list.append(m)

                elif move['type'] == 'i':
                    xy0 = _logic2arm(move['x0'],move['y0'])
                    move['xy0'] = xy0
                    best_move_list.append(move)
        
            for move in best_move_list:
                move['dist'] = np.linalg.norm(move['xy0']-arm_xy)
                
            min_dist = min([move['dist'] for move in best_move_list])
            best_move_list = list(filter(lambda move:move['dist']==min_dist,best_move_list))
            selected_move = random.choice(best_move_list)

            tar_xy, already_arrive, will_arrive = _move(arm_xy, selected_move['xy0'])
            if already_arrive:
                #print('ZJAKDJQCNC',file=sys.stderr)
                bot_logic.battle_target_move = selected_move
            elif will_arrive:
                print('KGDDSKPDMA',file=sys.stderr)
                bot_logic.battle_target_move = selected_move
                ret_root['arm_move_list'] = [np.append(tar_xy,[0])]
            else:
                #print('FWRFDBXSPK',file=sys.stderr)
                ret_root['arm_move_list'] = [np.append(tar_xy,[0])]
            
        elif bot_logic.battle_target_move != None:
            #print('{:.3f} NJHLCUZTAL bot_logic.battle_target_move != None'.format(time.time()),file=sys.stderr)
            my_move = bot_logic.battle_target_move
            
            #_, already_arrive, _ = _move(arm_xy, my_move['xy0'])
            #assert(already_arrive)

            same_move_list = move_list
            same_move_list = filter(lambda m:m['type']==my_move['type'],same_move_list)
            same_move_list = filter(lambda m:m['x0']==my_move['x0'],same_move_list)
            same_move_list = filter(lambda m:m['y0']==my_move['y0'],same_move_list)
            if (my_move['type'] == 'h') or (my_move['type'] == 'v'):
                same_move_list = filter(lambda m:m['x1']==my_move['x1'],same_move_list)
                same_move_list = filter(lambda m:m['y1']==my_move['y1'],same_move_list)
            same_move_list = list(same_move_list)
            if len(same_move_list) > 0:
                if (my_move['type'] == 'h') or (my_move['type'] == 'v'):
                    ret_root['arm_move_list'] = [
                        np.append(my_move['xy0'],[1]),
                        np.append(my_move['xy1'],[1]),
                        np.append(my_move['xy1'],[0]),
                    ]
                elif my_move['type'] == 'i':
                    ret_root['arm_move_list'] = [
                        np.append(my_move['xy0'],[1]),
                        np.append(my_move['xy0'],[0]),
                    ]

            bot_logic.battle_target_move_last = bot_logic.battle_target_move
            bot_logic.battle_target_move = None
        else:
            #print('{:.3f} DJZOJBEWKW wtf?'.format(time.time()),file=sys.stderr)
            pass

    #print('{:.3f} LHWIGLYADK battle logic end'.format(time.time()))

    return True

DRAW_SCREEN_XY = np.array([120,0])
DRAW_BOARD_XY  = DRAW_SCREEN_XY+np.array([0,62])
DRAW_CELL_STEP = 120 / SIDE_COUNT

def draw(screen, tick_result):
    #print(json.dumps(tick_result))
    ret = tick_result['battle_data']

    screen.blit(draw_util.text(ret['battle_second'],(0,0,0)), (240,20))
    
    if 'move_list' in ret:
        for move in ret['move_list']:
            if (move['type'] == 'h') or (move['type'] == 'v'):
                xy0 = _logic2draw(move['x0'],move['y0'])
                xy1 = _logic2draw(move['x1'],move['y1'])
                color = (255,0,0) if move['is_best'] else (0,0,255)
                pygame.draw.line(screen, color, tuple(xy0), tuple(xy1), 2)
            elif (move['type'] == 'i'):
                xy0 = _logic2draw(move['x0'],move['y0'])
                xy00 = xy0[0]-2,xy0[1]-2
                xy01 = 4,4
                color = (255,0,0) if move['is_best'] else (0,0,255)
                pygame.draw.rect(screen, color, tuple(xy00)+tuple(xy01), 1)

    if 'board_animal_list_list' in ret:
        board_animal_list_list = ret['board_animal_list_list']
        age_list_list = ret['age_list_list']
        for i in range(SIDE_COUNT):
            for j in range(SIDE_COUNT):
                if board_animal_list_list[i][j] == 'z_chao':
                    xy = _logic2draw(i,j)
                    x0,y0 = x1,y1 = xy
                    x0-=4
                    x1+=4
                    y0-=4
                    y1+=4
                    color,line_width = ((0,0,0),4) if age_list_list[i][j] else ((31,31,31),2)
                    pygame.draw.line(screen, color, (x0,y0), (x1,y1), line_width)
                    pygame.draw.line(screen, color, (x0,y1), (x1,y0), line_width)

def _logic2draw(x,y):
    xy = np.array([x+0.5,y+0.5])
    xy = xy * DRAW_CELL_STEP
    xy = xy + DRAW_BOARD_XY
    return xy

LOGIC2ARM_OFFSET = np.array([ARM_BOARD_RECT[0],ARM_BOARD_RECT[1]])
def _logic2arm(x,y):
    xy = np.array([x+0.5,y+0.5])
    xy = xy * ARM_CELL_STEP
    xy = xy + LOGIC2ARM_OFFSET
    return xy

EPSILON = 1
# return: (next_xy, already_arrive , will_arrive)
def _move(xy0,xy1,dist=MOVE_LEN,epsilon=EPSILON):
    xy10 = xy1-xy0
    len_xy10 = np.linalg.norm(xy10)
    if len_xy10 <= epsilon:
        return xy1, True, True
    if len_xy10 <= dist:
        return xy1, False, True
    xy10n = xy10 / len_xy10
    xy10nd = xy10n * dist
    ret = xy0 + xy10nd
    return ret, False, False
