from template import Agent
from Sequence.sequence_model import SequenceGameRule as GameRule
import heapq
import time
import random
from copy import deepcopy
from Sequence.sequence_model import COORDS 


POS_WEIGHT = [
    [3, 4, 5, 5, 5, 5, 5, 5, 4, 3],
    [4, 6, 7, 7, 7, 7, 7, 7, 6, 4],
    [5, 7, 9,10,10,10,10, 9, 7, 5],
    [5, 7,10,12,12,12,12,10, 7, 5],
    [5, 7,10,12,20,20,12,10, 7, 5],
    [5, 7,10,12,20,20,12,10, 7, 5],
    [5, 7,10,12,12,12,12,10, 7, 5],
    [5, 7, 9,10,10,10,10, 9, 7, 5],
    [4, 6, 7, 7, 7, 7, 7, 7, 6, 4],
    [3, 4, 5, 5, 5, 5, 5, 5, 4, 3]
]
# run with:
# python general_game_runner.py -g Sequence -l -q -p -a agents.t_014.A_star1.0

# python general_game_runner.py -g Sequence --saveLog -a agents.t_014.A_star_4 --agent_names=astar -p

# NONE = 0
# SLEEP_TWO = 1
# LIVE_TWO = 2 #live two: have two points and no block   _oo_
# SLEEP_THREE = 3  #sleep three: have three points but descrete _o_oo_b / _ooox
# # 
# LIVE_THREE = 9020 # live three: have three points and no block both sides
# CHONG_FOUR = 9020 # chong four: have one point can form five _oooox, _oo_oo_, _oo_oox
# # 
# LIVE_FOUR = 9030 # live four: have two points can form five _oooo_
# LIVE_FIVE = 15000


#{'play_card': '3s', 'draft_card': 'ah', 'type': 'place', 'coords': (0, 2)}
#{'play_card': 'jh', 'draft_card': '9d', 'type': 'remove', 'coords': (0, 1)}
# {'play_card': '2d', 'draft_card': 'ks', 'type': 'trade', 'coords': None}

#special wild cards remove opponent's card
#{'play_card': 'jh', 'draft_card': '9d', 'type': 'remove'
# {'play_card': 'js', 'draft_card': '5c', 'type': 'remove', 'coords': (8, 7)}

#place in any position
# {'play_card': 'jd', 'draft_card': 'ah', 'type': 'place', 'coords': (0, 1)}
# {'play_card': '3s', 'draft_card': 'jc', 'type': 'place', 'coords': (0, 2)}

class DirectionInfo:
    def __init__(self, dx, dy):
        self.debug = False
        self.dx = dx
        self.dy = dy
        self.connect_count = 1
        self.discrete_count_front = 0
        self.discrete_count_back = 0
        # self.discreate_count = 0
        self.open_front = False  # default is False, there is no empty space in front
        self.open_back = False
        self.mid_gap_count = 0

        self.block_component = 0

        self.connect_count_front = 0
        self.connect_count_back = 0

        # score for different shapes
        self.NONE = 0
        self.LIVE_ONE = 1
        self.SLEEP_TWO = 2
        self.LIVE_TWO = 30
        self.SLEEP_THREE = 40
        self.LIVE_THREE = 6000
        self.CHONG_FOUR = 9000
        self.LIVE_FOUR = 10000
        self.LIVE_FIVE = 15000

        self.OPP_LIVE_FOUR = 12000
        self.OPP_LIVE_THREE = 1000
        self.OPP_LIVE_FIVE = 13000

    def update_remove_one_side(self, r, c, dx, dy, board, my_colour, opponent_colour, front_back):
        current_r = r + dx
        current_c = c + dy
        while self.in_board(current_r, current_c):
            # print(f"Update remove position ({current_r}, {current_c})")
            if board[current_r][current_c] == opponent_colour or board[current_r][current_c] == "#":
                self.connect_count += 1
                if front_back == 'front': self.connect_count_front += 1
                if front_back == 'back': self.connect_count_back += 1
                current_r += dx
                current_c += dy
                continue
            elif board[current_r][current_c] == my_colour:
                if front_back == 'front': self.open_front = False
                if front_back == 'back': self.open_back = False
                return
            elif board[current_r][current_c] == '_': 
                if front_back == 'front': self.open_front = True
                if front_back == 'back': self.open_back = True
                return
            else:
                return


    def update_direction_one_side(self, r, c, dx, dy, board, my_colour, opponent_colour, front_back):
        current_r = r + dx
        current_c = c + dy
        while self.in_board(current_r, current_c):
            # print(f"Update position ({current_r}, {current_c})")
            if board[current_r][current_c] == my_colour:
                self.connect_count += 1
                current_r += dx
                current_c += dy
                continue
            elif board[current_r][current_c] == opponent_colour:
                self.block_component += 1
                current_r += dx
                current_c += dy
                while self.in_board(current_r, current_c) and board[current_r][current_c] == opponent_colour:
                    self.block_component += 1
                    current_r += dx
                    current_c += dy
                return
            elif board[current_r][current_c] == '#':
                self.connect_count += 1
                return
            
            elif board[current_r][current_c] == '_' and self.mid_gap_count >= 1: #second time meet empty
                if front_back == 'front': self.open_front = True
                if front_back == 'back': self.open_back = True
                return

            elif board[current_r][current_c] == '_' and self.mid_gap_count < 1: #first time meet empty
                current_c += dx
                current_r += dy
                if front_back == 'front': self.open_front = True
                if front_back == 'back': self.open_back = True
                if not self.in_board(current_c, current_r):
                    # detect out of board
                    if front_back == 'front': self.open_front = False
                    if front_back == 'back': self.open_back = False
                    return
                elif board[current_r][current_c] == '#':
                    if front_back ==  'front':
                        self.open_front = False
                        self.discrete_count_front += 1
                    if front_back == 'back':
                        self.open_back = False
                        self.discrete_count_back += 1
                    return
                elif board[current_r][current_c] == my_colour:
                    self.mid_gap_count += 1
                    if front_back == 'front':
                        self.discrete_count_front += 1
                    if front_back == 'back':
                        self.discrete_count_back += 1
                    current_r += dx
                    current_c += dy
                    continue
                else:
                    return
            else:
                if front_back == 'front': self.open_front = False
                if front_back == 'back': self.open_back = False
                return
        # print(f"Out of board at ({current_r}, {current_c})")
            

    def calculate_score(self, r, c):

        action_state = {
            'TRADE': False,
            'SLEEP_TWO': 0,
            'LIVE_TWO': 0,
            'SLEEP_THREE': 0,
            'LIVE_THREE': 0,
            'CHONG_FOUR': 0,
            'LIVE_FOUR': 0,
            'LIVE_FIVE': 0,
            'OPP_LIVE_FOUR': 0,
            'OPP_CHONG_FOUR': 0,
            'OPP_LIVE_THREE': 0,
            'OPP_LIVE_FIVE': 0
        }
        count_discrete = self.discrete_count_front + self.discrete_count_back
        block_score = 0
        block_score += POS_WEIGHT[r][c]
        if self.block_component >= 5:
            block_score += self.OPP_LIVE_FIVE
            action_state['OPP_LIVE_FIVE'] += 1
        elif self.block_component == 4:
            block_score += self.OPP_LIVE_FOUR
            action_state['OPP_LIVE_FOUR'] += 1
        elif self.block_component == 3:
            block_score += self.OPP_LIVE_THREE
            action_state['OPP_LIVE_THREE'] += 1

        if self.debug:
            print(f'in score.py debug')
        if self.connect_count >= 5:
            action_state['LIVE_FIVE'] += 1
            return action_state, self.LIVE_FIVE+ block_score
        elif self.connect_count == 4 and self.open_front and self.open_back:
            action_state['LIVE_FOUR'] += 1
            return action_state, self.LIVE_FOUR+ block_score
        elif (self.connect_count == 4 and (self.open_front or self.open_back)) \
                or (count_discrete == 4 and (self.open_front or self.open_back)):
            action_state['CHONG_FOUR'] += 1
            return action_state, self.CHONG_FOUR+ block_score
        elif (self.connect_count == 3 or count_discrete == 3) and (self.open_front and self.open_back):
            action_state['LIVE_THREE'] += 1
            return action_state, self.LIVE_THREE+ block_score
        elif (self.connect_count == 3 and (self.open_front or self.open_back)) \
                or (count_discrete == 3 and (self.open_front or self.open_back)):
            action_state['SLEEP_THREE'] += 1
            return action_state, self.SLEEP_THREE+ block_score

        elif (self.connect_count == 2 or count_discrete == 2) and (self.open_front and self.open_back):
            action_state['LIVE_TWO'] += 1
            if self.debug:
                print(f'score.py debug: live two {action_state}')
            return action_state, self.LIVE_TWO+ block_score
        elif (self.connect_count == 2 and (self.open_front or self.open_back)) \
                or (count_discrete == 2 and (self.open_front and self.open_back)):
            action_state['SLEEP_TWO'] += 1

            if self.debug:
                print(f'score.py debug: sleep two {action_state}')
            return action_state, self.SLEEP_TWO+ block_score
        else:
            if self.debug:
                print(f'score.py debug: no action{action_state}')
            return action_state, self.NONE+ block_score


    def calculate_remove_score(self):
        action_state = {
            'TRADE': False,
            'SLEEP_TWO': 0,
            'LIVE_TWO': 0,
            'SLEEP_THREE': 0,
            'LIVE_THREE': 0,
            'CHONG_FOUR': 0,
            'LIVE_FOUR': 0,
            'LIVE_FIVE': 0,
            'OPP_LIVE_FOUR': 0,
            'OPP_CHONG_FOUR': 0,
            'OPP_LIVE_THREE': 0,
            'OPP_LIVE_FIVE': 0
        }
        if self.connect_count >= 5 and self.open_front and self.open_back and (self.connect_count_front >= 3 or self.connect_count_back >= 3):
            action_state['OPP_LIVE_FIVE'] += 1
            return action_state, self.OPP_LIVE_FIVE
        elif self.connect_count == 4 and (self.open_front or self.open_back) and (self.connect_count_front >= 2 or self.connect_count_back >= 2):
            action_state['OPP_LIVE_FOUR'] += 1
            return action_state, self.OPP_LIVE_FOUR
        else:
            return action_state, self.NONE

    def in_board(self, r, c):
        return 0 <= r < 10 and 0 <= c < 10
    