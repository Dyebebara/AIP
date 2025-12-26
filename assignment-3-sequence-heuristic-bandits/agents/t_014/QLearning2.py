from template import Agent
import random
import math
import copy
from collections import defaultdict
from Sequence.sequence_model import SequenceGameRule as GameRule
from Sequence.sequence_model import COORDS
from Sequence.sequence_utils import *
import os
import json
from agents.t_014.score import DirectionInfo
import re

import heapq
import time
import random
from copy import deepcopy

# run with:
# python general_game_runner.py -g Sequence -l -q -p -a agents.t_014.QLearning2

#python general_game_runner.py -g Sequence -a agents.t_014.myTeam --agent_names=Q

# python general_game_runner.py -g Sequence -a [agents.t_014.A_star_3,agents.t_014.QLearning2 --agent_names=[A_star,Q] -n 2 -p -q

# python general_game_runner.py -g Sequence -a agents.t_014.A_star_3,agents.t_014.QLearning2 --agent_names=A_star,Q -n 2  -q

# python general_game_runner.py -g Sequence -a agents.t_014.QLearning2 --agent_names=Q -p -q
# git tag -d 1415524
# git push origin --delete tag 1415524
# git tag 1415524
# git push origin 1415524

# git tag -d test-submission
# git push origin --delete tag test-submission
# git tag test-submission
# git push origin test-submission



# git tag -d tournament-submission
# git push origin --delete tag tournament-submission
# git tag tournament-submission
# git push origin tournament-submission

MAX_THINK_TIME = 0.89
NUM_PLAYERS = 2
Training = False


class myAgent(Agent):
    def __init__(self, _id, alpha=0.2, gamma=0.7, epsilon=0.01):
        super().__init__(_id)
        self.id = _id
        self.rule = GameRule(NUM_PLAYERS)
        self.debug = False
        
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # exploration rate
        self.q_table = {}

        self.prev_state = None
        self.prev_action_state = None
        self.prev_reward = 0.0
        self.prev_Q_value = 0.0

        self.q_table_file = "./agents/t_014/q_learning_weights_win32.json"
        self.load()


    def SelectAction(self, actions, game_state):

        # start_time = time.time()
        # print(f"SelectAction Available actions: {actions}")
        if Training and self.prev_state is not None and self.prev_action_state is not None and self.prev_reward is not None:
            self.update(self.prev_state, self.prev_action_state, self.prev_reward, self.prev_Q_value, game_state, actions)
        # print(f'time for update: {time.time() - start_time}')
        # Exploration
        if Training and random.random() < self.epsilon:
            action = random.choice(actions)
        else:
            action_state, action = self.check_actions(actions, game_state, True)
            # print(f"Selected action: {action} with state: {action_state}")

        return action

    def update(self, prev_state, prev_action_state, prev_reward, prev_Q_value, current_state, current_actions):

        print(f"Updating Q-value for previous state")
        # print(f"update Available actions: {current_actions}")
        default_action_state = {
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
        if  json.dumps(prev_action_state, sort_keys=True) == json.dumps(default_action_state, sort_keys=True):
            print(f'prev_action_state is default, setting to None')
            return
        if json.dumps(prev_action_state, sort_keys=True) == '{\"CHONG_FOUR\": 0, \"LIVE_FIVE\": 0, \"LIVE_FOUR\": 0, \"LIVE_THREE\": 0, \"LIVE_TWO\": 0, \"OPP_CHONG_FOUR\": 0, \"OPP_LIVE_FIVE\": 0, \"OPP_LIVE_FOUR\": 0, \"OPP_LIVE_THREE\": 0, \"SLEEP_THREE\": 0, \"SLEEP_TWO\": 0, \"TRADE\": false}':
            print(f'prev_action_state is default, setting to None')
            return
        # Encode the old state and action
        prev_state_encoding = self.encode_state(prev_state)

        # next_state_encoding = self.encode_state(current_state)

        old_q = self.get_q_value(prev_state_encoding, prev_action_state)
        # print(f'Old Q-value: {old_q}')

        if old_q is None:
            print(f"Old Q-value not found, initializing")
            last_action = current_state.agents[self.id].last_action
            action_state, old_q = self.check_actions([last_action], prev_state, False)
                # self.update_q_value(prev_state_encoding, prev_action_state, 0)
                # old_q = 0

        # Find max‐Q in the next state Sarsa
        next_actions = current_actions

        print(f'start to choose next action from {len(next_actions)}')
        if random.random() < self.epsilon:
            # Exploration: choose a random action
            next_action = random.choice(next_actions)
            next_q = self.check_actions([next_action], current_state, False) #q value for the next action best_next_q

            print(f"random Next Q-value (exploration): {next_q}")
        else:
            next_q = self.check_actions(next_actions, current_state, False)
            print(f"Next Q-value (exploitation): {next_q}")

        # 3) Q‐learning Bellman update
        print(f'Old Q-value: {old_q} {prev_Q_value}')
        print(f'prev_reward: {prev_reward}, next_q: {next_q}')
        delta = prev_reward + self.gamma * next_q - old_q
        # self.q_table[(prev_state_encoding, prev_action_state)] = old_q + self.alpha * delta
        self.update_q_value(prev_state_encoding, prev_action_state, old_q + self.alpha * delta)

        if self.q_table_file:
            self.save()

    def encode_state(self, game_state):

        state = {
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
        r_patterns = {
            "SLEEP_TWO": r"((^|[bXO])r{2}_|_r{2}([bXO]|$)|#r{2}_|_r{2}#)",
            "LIVE_TWO": r"(_r{2}_)",
            "SLEEP_THREE": r"((^|[bXO])r{3}_|_r{3}([bXO]|$)|#r{2}_|_r{2}#)|(^|[bXO])rr_r_|_rr_r_([bXO]|$)|(^|[bXO])r_rr_|_r_rr_([bXO]|$)",
            "LIVE_THREE": r"(_r{3}_)",
            "OPP_LIVE_FOUR": r"(_b{4}_)",
            "LIVE_FOUR": r"(_r{4}_)",
            "CHONG_FOUR":     r"((^|[bXO])r{4}_|_r{4}([bXO]|$)|#r{3}_|_r{3}#)|(^|[bXO])rr_rr_|_rr_rr([bXO]|$)|(^|[bXO])r_rrr_|_r_rrr([bXO]|$)|(^|[bXO])rrr_r_|_r_rrr([bXO]|$)|_rr_rr_",
            "OPP_CHONG_FOUR": r"((^|[rXO])b{4}_|_b{4}([rXO]|$)|#b{3}_|_b{3}#)|(^|[rXO])bb_bb_|_bb_bb([rXO]|$)|(^|[rXO])b_bbb_|_b_bbb([rXO]|$)|(^|[rXO])bbb_b_|_b_bbb([rXO]|$)|_bb_bb_",
            "OPP_LIVE_THREE": r"(_b{3}_)",
            "OPP_LIVE_FIVE": r"(_b{5}_)",
            "LIVE_FIVE": r"(_r{5}_)"
        }

        b_patterns = {
            "SLEEP_TWO": r"((^|[rXO])b{2}_|_b{2}([rXO]|$)|#b{2}_|_b{2}#)",
            "LIVE_TWO": r"(_b{2}_)",
            "SLEEP_THREE": r"((^|[rXO])b{3}_|_b{3}([rXO]|$)|#b{2}_|_b{2}#)|(^|[rXO])bb_b_|_bb_b_([rXO]|$)|(^|[rXO])b_bb_|_b_bb_([rXO]|$)",
            "LIVE_THREE": r"(_b{3}_)",
            "OPP_LIVE_FOUR": r"(_r{4}_)",
            "LIVE_FOUR": r"(_b{4}_)",
            "CHONG_FOUR":     r"((^|[rXO])b{4}_|_b{4}([rXO]|$)|#b{3}_|_b{3}#)|(^|[rXO])bb_bb_|_bb_bb([rXO]|$)|(^|[rXO])b_bbb_|_b_bbb([rXO]|$)|(^|[rXO])bbb_b_|_b_bbb([rXO]|$)|_bb_bb_",
            "OPP_CHONG_FOUR": r"((^|[bXO])r{4}_|_r{4}([bXO]|$)|#r{3}_|_r{3}#)|(^|[bXO])rr_rr_|_rr_rr([bXO]|$)|(^|[bXO])r_rrr_|_r_rrr([bXO]|$)|(^|[bXO])rrr_r_|_r_rrr([bXO]|$)|_rr_rr_",
            "OPP_LIVE_THREE": r"(_r{3}_)",
            "OPP_LIVE_FIVE": r"(_r{5}_)",
            "LIVE_FIVE": r"(_b{5}_)"
        }
        # print(f"Encoding state for player {self.id}, {game_state}")
        board = game_state.board.chips
        my_colour = game_state.agents[self.id].colour
        # print(f"Current player: {self.id}, Colour: {my_colour}")
        opponent_colour = game_state.agents[self.id].opp_colour
        if my_colour == 'r':
            patterns = r_patterns
        else:
            patterns = b_patterns


        # # row
        # board = game_state.board.chips
        # for r in board:
        #     print(r)
        for row in board:
            line = ''.join(row)
            # print(f'Encoding row: {line}')
            for k, pat in patterns.items():
                state[k] += len(re.findall(pat, line))
                # print(f'Pattern {k}: {pat}, Count: {state[k]}')

        # # column

        # board = game_state.board.chips
        # for r in board:
        #     print(r)
        for c in range(10):
            line = ''.join(board[r][c] for r in range(10))
            # print(f'Encoding column: {line}')
            for k, pat in patterns.items():
                state[k] += len(re.findall(pat, line))
                # print(f'Pattern {k}: {pat}, Count: {state[k]}')

        # diagonal from top-left to bottom-right

        # board = game_state.board.chips
        # for r in board:
        #     print(r)
        for d in range(-5, 6):
            diag = [board[r][r-d] for r in range(max(0, d), min(10, 10+d))]
            line = ''.join(diag)
            # print(f'Encoding diagonal0: {line}')
            for k, pat in patterns.items():
                state[k] += len(re.findall(pat, line))
                # print(f'Pattern {k}: {pat}, Count: {state[k]}')

        # # diagonal from top-right to bottom-left

        # board = game_state.board.chips
        # for r in board:
        #     print(r)
        for d in range(4, 15):
            diag = [board[r][d-r] for r in range(max(0, d-9), min(10, d+1)) if 0 <= d-r < 10]
            line = ''.join(diag)
            # print(f'Encoding diagonal1: {line}')
            for k, pat in patterns.items():
                state[k] += len(re.findall(pat, line))
                # print(f'Pattern {k}: {pat}, Count: {state[k]}')

        return state
        
    def get_q_value(self, state_rep, action):
        
        key = json.dumps(state_rep, sort_keys=True) + '||' + json.dumps(action, sort_keys=True)
        # print(f"Getting Q-value for state: {key} {self.q_table.get(key, None)}")
        return self.q_table.get(key, None)

    def update_q_value(self, state_rep, action, value):
        """Update Q-value for a given state and action."""
        key = json.dumps(state_rep, sort_keys=True) + '||' + json.dumps(action, sort_keys=True)
        self.q_table[key] = value
        # print(f"Updated Q-value {value} for {key} to {value}")


    def save(self):
        """Save Q-table as JSON."""

        # print(f"Saving Q-table with {len(self.q_table)} entries.")
        filepath = self.q_table_file
        dirpath = os.path.dirname(filepath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.q_table, f, indent=4)
        # print(f"Saving Q-table with {len(self.q_table)} entries.")

    def load(self):
        filepath = self.q_table_file
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    loaded = json.load(f)
                self.q_table = loaded
                print(f"Loaded Q-table with {len(self.q_table)} entries from {filepath}.")  
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {filepath}. Initializing empty Q-table.")
                self.q_table = {}
        else:
            print(f"Q-table file {filepath} does not exist. Initializing empty Q-table.")
            dirpath = os.path.dirname(filepath)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({}, f)
            self.q_table = {}


    def check_actions(self, actions, game_state, update_global_state):  
        if self.debug:
            print(f"Checking actions")
            print(game_state)
            print(f"Available actions: {actions}")
        # reset for each turn
        self.draw_card = {}
        self.place_score = {}
        self.trade_card = {}
        self.remove_score = {}
        self.best_draw_card = None
        self.test_draw_card = True

        start_time = time.time()
        best_action = None
        best_action_state = None
        best_score = 0

        best_current_action_reward = 0
        best_current_action_Q_value = 0

        board = deepcopy(game_state.board.chips)

        board_state = self.encode_state(game_state)
        if self.debug:
            print(f"Encoded board state: {board_state}")
        my_colour = game_state.agents[self.id].colour
        opponent_colour = game_state.agents[self.id].opp_colour
        
        # print(f"Opponent player: {self.id}, Colour: {opponent_colour}")
        for action in actions:
            if time.time() - start_time > MAX_THINK_TIME:
                print(f"Action: {action}") 
                print(f"Time limit reached. Best action so far: {best_action}, Score: {best_score}")
                return best_action if best_action else random.choice(actions)
            
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

            default_action_state = {
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

            action_type = action['type']
            action_coords = action['coords']
            action_play_card = action['play_card']
            action_draft_card = action['draft_card']
            score = 0
            draw_weight = 0.3

            current_action_reward = 0

            # print(f"Action: {action}")
            draw_score = self.draw_card.get(action_draft_card, None)
            if self.debug:
                print(f"Draw score: {draw_score}, Test draw card: {self.test_draw_card}")
            if self.test_draw_card:
                if  draw_score is None:

                    _, self.draw_card[action_draft_card] = self.evaluate_draw_score(action, board, game_state, my_colour, opponent_colour)
                    score += self.draw_card[action_draft_card] * draw_weight
                    # print(f"Draw score calculated: {self.draw_card[action_draft_card]}")
                else:
                    score += draw_score * draw_weight
            else:
                if action_draft_card != self.best_draw_card:
                    continue
                else:
                    score += self.draw_card[self.best_draw_card] * draw_weight

            self.set_best_draw_card()

            
            remove_key = (action_play_card, action_coords)
            if action_type == 'remove': 
                if remove_key in self.remove_score:
                    # print(f"Remove score found: {self.remove_score[remove_key]}")
                    score += self.remove_score[remove_key]
                    current_action_reward = self.remove_score[remove_key]
                else:
                    action_state, rev_score = self.evaluate_remove_score(action, board, game_state, my_colour, opponent_colour)
                    score += rev_score
                    current_action_reward = rev_score



            if action_type == 'trade':
                if not update_global_state:
                    print(f"Skip update Trade action: {action}")
                    continue
                best_trade_card = self.trade_card.get(action_draft_card, None)  
                if not self.test_draw_card and action_draft_card == self.best_draw_card:
                    action_state['TRADE'] = True
                    return action_state, action
                elif not self.test_draw_card and best_trade_card is not None:
                    # print(f"Trade card found: {best_trade_card}")
                    action_state['TRADE'] = True
                    return action_state, best_trade_card
                else:
                    self.trade_card[action_draft_card] = action
                    continue



            key = (action_play_card, action_coords)
            if action_type == 'place':
                if key in self.place_score:
                    # print(f"Place score found: {self.place_score[key]}")
                    score += self.place_score[key]
                    current_action_reward = self.place_score[key]
                else:
                    action_state, place_score = self.evaluate_place_score(action, board, game_state, my_colour, opponent_colour)
                    score += place_score
                    current_action_reward = place_score


            # if self.debug:
            #     print(f"Action: {action}, Score: {score}")

            q_value = self.get_q_value(board_state, action_state)
            print(f'Qvalue:{q_value} for action: {action} {action_state}')
            if q_value is None:
                print(f"Q-value not found for action: {action} {action_state}")
                if  json.dumps(action_state, sort_keys=True) != json.dumps(default_action_state, sort_keys=True):
                    print(f'prev_action_state is default, setting to None')
                    self.update_q_value(board_state, action_state, max(0, current_action_reward))
                    # print(f"Q-value not found, setting to score: {score}")
                    # print(self.q_table)
                    q_value = current_action_reward
                else:
                    q_value = 0

            final_score = 0.6 * q_value + 0.4 * score

            if final_score > best_score:
                best_score = final_score
                best_action = action
                best_action_state = action_state
                best_current_action_reward = current_action_reward
                best_current_action_Q_value = q_value

                if self.debug:
                    print(f"Best action: {best_action}, Score: {best_score}")
                if best_score >= 17000:

                    if update_global_state:
                        self.prev_state = copy.deepcopy(game_state)
                        self.prev_action_state = copy.deepcopy(best_action_state)
                        self.prev_reward = best_current_action_reward
                        self.prev_Q_value = best_current_action_Q_value
                        
                    else:
                        return best_current_action_Q_value
                    
                    # print(f'return best action: {best_action} {best_score} \n')
                    return best_action_state, best_action
            else:
                continue
        if self.debug:
            print(f'return best action: {best_action} {best_score} \n')

        if update_global_state:
            self.prev_state = copy.deepcopy(game_state)
            self.prev_action_state = copy.deepcopy(best_action_state)
            self.prev_reward = best_current_action_reward
            self.prev_Q_value = best_current_action_Q_value
        else:
            # print(f'global {update_global_state}, best_score: {best_score}')
            return best_current_action_Q_value

        return best_action_state, best_action


    def evaluate_place_score(self, action, board, game_state, my_colour, opponent_colour):
        r, c = action['coords']
        # draw_card = action['draft_card']
        # print(action)
        key = (action['play_card'], action['coords'])
        if action['type'] == 'place':
            action_state, score = self.test_my_current_score(r, c, board, my_colour, opponent_colour)
            if self.debug:
                print(f"evaluate_place_score ({action_state}) → Score: {score}")
            self.place_score[key] = score
            return action_state, score

    def evaluate_remove_score(self, action, board, game_state, my_colour, opponent_colour):
        r, c = action['coords']
        # draw_card = action['draft_card']
        key = (action['play_card'], action['coords'])
        # print(action)
        if action['type'] == 'remove':
            action_state, score = self.test_my_remove_score(r, c, board, my_colour, opponent_colour)
            self.remove_score[key] = score
            return action_state, score
        
    def test_my_remove_score(self, r, c, board, my_colour, opponent_colour):
        # print(f"Testing remove position ({r}, {c})")
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        total_score = 0
        for dx, dy in directions:
            direction_info = DirectionInfo(dx, dy)
            direction_info.update_remove_one_side(r, c, dx, dy, board, my_colour, opponent_colour, front_back='front')
            direction_info.update_remove_one_side(r, c, -dx, -dy, board, my_colour, opponent_colour, front_back='back')
            action_state, score = direction_info.calculate_remove_score()
            total_score += score
            # if self.debug:
            #     print(f"Direction {(dx,dy)} → Shape: {shape}, Score: {score}")
        return action_state, total_score

    def evaluate_draw_score(self, action, board, game_state, my_colour, opponent_colour):

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
        best_card = ['jd', 'jh', 'js', 'jc']

        draw_card = action['draft_card']
        # print(action)
        if draw_card in self.draw_card:
            # print(f'problem in evaluate_draw_score: {draw_card} already in draw_card')
            score = self.draw_card[draw_card]
            return score
        
        if draw_card in best_card:
            self.draw_card[draw_card] = 15000
            action_state['TRADE'] = True
            return action_state, 15000

        cor_list = COORDS[draw_card]
        best_score = 0
        score = 0
        for r, c in cor_list:
            if board[r][c] != '_':
                continue
            action_state, score = self.test_my_current_score(r, c, board, my_colour, opponent_colour)
            # if self.debug:
            #     print(f"Testing draw state {action_state} → Score: {score}")
            if score > best_score:
                best_score = score
        self.draw_card[draw_card] = best_score  
        if self.debug:
            print(f"Draw card {draw_card} evaluated with score: {best_score}")     
        return action_state, best_score

    def test_my_current_score(self, r, c, board, my_colour, opponent_colour):
        # print(f"test_my_current_score ({r}, {c})")
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        total_score = 0
        for dx, dy in directions:
            direction_info = DirectionInfo(dx, dy)
            direction_info.update_direction_one_side(r, c, dx, dy, board, my_colour, opponent_colour, front_back='front')
            direction_info.update_direction_one_side(r, c, -dx, -dy, board, my_colour, opponent_colour, front_back='back')
            action_state, score = direction_info.calculate_score(r, c)
            total_score += score
            if self.debug:
                print(f"Direction {(dx,dy)} → Shape: {action_state}, Score: {score}")

        return action_state, total_score

    
    def in_board(self, r, c):
        return 0 <= r < 10 and 0 <= c < 10



    def set_best_draw_card(self):
        if len(self.draw_card.keys()) == 5 and self.test_draw_card:
            self.test_draw_card = False
            # card which has the best score
            sorted_draw_card = sorted(self.draw_card.items(), key=lambda x: x[1], reverse=True)
            self.best_draw_card = sorted_draw_card[0][0]
            if self.debug:
                print(f"test_draw_card finished,  best draw is: {self.best_draw_card} {self.draw_card}")

