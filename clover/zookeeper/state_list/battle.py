from zookeeper_screen_recognition import classifier_board_animal
from clover.zookeeper import zookeeper_solver
import os
import json
import pygame

SIZE = 8

BOARD_RECT = (0,332,640,972) # x0,y0,x1,y1

def init(bot_logic):
    bot_logic.board_animal_clr = classifier_board_animal.BoardAnimalClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_board_animal.MODEL_PATH))

def tick(bot_logic, img, ret):
    return False

    ret['battle_data'] = {}
    ret = ret['battle_data']

    #if not hasattr(bot_logic, 'board_animal_clr'):
    #    bot_logic.board_animal_clr = classifier_board_animal.BoardAnimalClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_board_animal.MODEL_PATH))
    board_animal_list, _ = bot_logic.board_animal_clr.predict(img)
    board_animal_list_list = [[board_animal_list[i+j*SIZE] for j in range(SIZE)] for i in range(SIZE)]
    ret['board_animal_list_list'] = board_animal_list_list
    
    _, move_list = zookeeper_solver.solve(board_animal_list_list)
    if len(move_list) > 0:
        best_score = max([move['score'] for move in move_list])
        for move in move_list:
            move['is_best'] = move['score'] >= best_score
    ret['move_list'] = move_list


SCREEN_DISPLAY_X0 = 120 # hardcode
BOARD_X0 = 0
DRAW_X0 = SCREEN_DISPLAY_X0+BOARD_X0

SCREEN_DISPLAY_Y0 = 0
BOARD_Y0 = 62 # hardcode
DRAW_Y0 = SCREEN_DISPLAY_Y0+BOARD_Y0

CELL_SIZE = 120 / SIZE

def draw(screen, tick_result):
    #print(json.dumps(tick_result))
    ret = tick_result['battle_data']
    
    for move in ret['move_list']:
        x0 = (move['x0']+0.5) * CELL_SIZE + DRAW_X0
        y0 = (move['y0']+0.5) * CELL_SIZE + DRAW_Y0
        x1 = (move['x1']+0.5) * CELL_SIZE + DRAW_X0
        y1 = (move['y1']+0.5) * CELL_SIZE + DRAW_Y0
        color = (255,0,0) if move['is_best'] else (0,0,255)
        pygame.draw.line(screen, color, (x0,y0), (x1,y1), 2)

def _item_xy(col, row):
    dx = (BOARD_RECT[2] - BOARD_RECT[0]) / SIZE
    dy = (BOARD_RECT[3] - BOARD_RECT[1]) / SIZE
    return ((col+0.5)*dx+BOARD_RECT[0],(row+0.5)*dy+BOARD_RECT[1])
    