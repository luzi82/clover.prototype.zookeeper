import copy
import numpy as np
import json
import sys

SIZE = 8

def solve(board, is_end):

    board = copy.copy(board)

    # fill z_chao over z_chao
    chao_list = []
    for x in range(SIZE):
        chao = -1
        for y in reversed(range(SIZE)):
            if board[x][y] == 'z_chao':
                chao = y
                break
        if chao != -1:
            for y in range(chao):
                board[x][y] = 'z_chao'
        chao_list.append(chao)

    h_move_list = get_h_move_list(board,'h')
    v_move_list = t1(get_h_move_list(t0(board),'v'))
    i_move_list = get_i_move_list(board)

    move_list = h_move_list+v_move_list+i_move_list
    
    if len(move_list) <= 0:
        return None, move_list

    rank_list = get_rank_list(move_list,chao_list,END_WEIGHT if is_end else NORMAL_WEIGHT)
    best_move_idx = rank_list.index(max(rank_list))
    
    return move_list[best_move_idx], move_list

def get_h_move_list(board,type):
    move_list = []
    for x in range(SIZE-1):
        for y in range(SIZE):
            i0 = get_animal(board,x,y)
            i1 = get_animal(board,x+1,y)
            if (i0 == 'z_chao') or (i1 == 'z_chao'):
                #print('chao',fp=sys.stderr)
                continue
            if (i0 == i1):
                continue
            i0_clear_animal_list, i0_combo = check_clear(board,x,y,-1,i1)
            i1_clear_animal_list, i1_combo = check_clear(board,x+1,y,+1,i0)
            combo = i0_combo+i1_combo
            if combo <= 0:
                continue
            move_list.append({
                'i0':i0,'i1':i1,
                'x0':x,'y0':y,'x1':x+1,'y1':y,
                'clear_animal_list':i0_clear_animal_list+i1_clear_animal_list,
                'combo':combo,
                'type':type
            })
    return move_list

def check_clear(board,x,y,dx,i0):
    clear_animal_list = []
    combo = 0
    if (i0[:2]!='a_'):
        return clear_animal_list, combo
    if (get_animal(board,x,y-1)==i0):
        clear_animal_list.append((x,y-1))
        if (get_animal(board,x,y-2)==i0):
            clear_animal_list.append((x,y-2))
    if (get_animal(board,x,y+1)==i0):
        clear_animal_list.append((x,y+1))
        if (get_animal(board,x,y+2)==i0):
            clear_animal_list.append((x,y+2))
    if len(clear_animal_list)<2:
        clear_animal_list = []
    else:
        combo += len(clear_animal_list)-1
    if (get_animal(board,x+dx,y)==i0) and (get_animal(board,x+dx*2,y)==i0):
        clear_animal_list.append((x+dx,y))
        clear_animal_list.append((x+dx*2,y))
        combo += 1
    if combo > 0:
        clear_animal_list.append((x,y))
    return clear_animal_list, combo

def t0(board):
    out = [[None for _ in range(SIZE)] for _ in range(SIZE)]
    for x in range(SIZE):
        for y in range(SIZE):
            out[x][y] = board[y][x]
    return out

def t1(move_list):
    ret = []
    for move in move_list:
        move0 = copy.copy(move)
        move0.update({
            'x0':move['y0'],'y0':move['x0'],'x1':move['y1'],'y1':move['x1'],
            'clear_animal_list':[(j,i) for i,j in move['clear_animal_list']]
        })
        ret.append(move0)
    return ret

def get_i_move_list(board):
    move_list = []
    for x in range(SIZE):
        for y in range(SIZE):
            i0 = get_animal(board,x,y)
            if (i0[:2] != 's_'):
                continue
            move_list.append({
                'i0':i0,
                'x0':x,'y0':y,
                i0:1,
                'type':'i'
            })
    return move_list

def get_animal(board,x,y):
    if x < 0 or x >= SIZE:
        return None
    if y < 0 or y >= SIZE:
        return None
    return board[x][y]

def get_rank_list(move_list,chao_list,weight):
    busy_list = [99 for _ in range(SIZE)]
    for move in move_list:
        if (move['type'] == 'h') or (move['type'] == 'v'):
            top_list = {}
            deep = -1
            for x,y in move['clear_animal_list'] + [(move['x0'],move['y0']),(move['x1'],move['y1'])]:
                if x not in top_list:
                    top_list[x] = 999
                top_list[x] = min(y,top_list[x])
                busy_list[x] = min(y,busy_list[x])
                chao_create = y-chao_list[x]
                deep = max(chao_create,deep)
            move['top_list'] = top_list
            move['a_deep'] = deep
        elif move['type'] == 'i':
            x,y = move['x0'],move['y0']
            # busy_list[x] = min(y,busy_list[x]) # item do not crash other
            move['top_list'] = { x: y }
            move['s_deep'] = move['y0']-chao_list[x]

    for move in move_list:
        crash = 0
        for x,y in move['top_list'].items():
            if busy_list[x] <= y-1:
                crash = 1
                break
        move['crash'] = crash

    for move in move_list:
        move['score'] = sum([w * if0(move,key) for key, w in weight])

    rank_list = [ move['score'] for move in move_list]
    return rank_list

NORMAL_WEIGHT = [
    ('combo',     1),
    ('a_deep',    10),
    ('s_deep',   -10),
    ('crash',    -1000),
    ('s_bino',   -10000),
    ('s_boss',   -10000+100),
    ('s_bucket', -10000+100),
    ('s_clear',  -10000-100),
    ('s_heart',  -10000+100)
]

END_WEIGHT = [
    ('combo',     1),
    ('a_deep',    10),
    ('s_deep',   -10),
    ('crash',    -1000),
    ('s_bino',   -10000),
    ('s_boss',    10000+100),
    ('s_bucket',  10000+100),
    ('s_clear',   10000-100),
    ('s_heart',   10000+100)
]

def if0(d,key):
    if key in d:
        return d[key]
    return 0

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='zookeeper solver')
    parser.add_argument('file', help='input file')
    args = parser.parse_args()

    with open(args.file,'r') as fin:
        j = json.load(fin)

    jout = {
        'zookeeper_solver':[]
    }
    for guess_board_animal in j['guess_board_animal_list']:
        board = guess_board_animal['board']
        best_move, move_list = solve(board)
        jout['zookeeper_solver'].append({
            'fn':guess_board_animal['fn'],
            'best_move':best_move,
            'move_list':move_list
        })
    json.dump(jout,sys.stdout,indent=2,sort_keys=True)
    sys.stdout.write('\n')
