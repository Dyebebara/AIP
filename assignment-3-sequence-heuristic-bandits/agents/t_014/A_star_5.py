from template import Agent
from Sequence.sequence_model import SequenceGameRule as GameRule
import heapq
import time
import random
from copy import deepcopy
from Sequence.sequence_model import COORDS 

from agents.t_014.score import DirectionInfo
# run with:
# python general_game_runner.py -g Sequence -l -q -p -a agents.t_014.A_star1.0

# python general_game_runner.py -g Sequence --saveLog -p -a agents.t_014.A_star_5 --agent_names=astar 

# git tag -d 1415524
# git push origin --delete tag 1415524
# git tag 1415524
# git push origin 1415524
MAX_THINK_TIME = 0.90

class myAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)
        self.id = _id
        self.rule = GameRule(2)
        self.debug = False


        self.draw_card = {}
        self.place_score = {}
        self.remove_score = {}
        self.best_draw_card = None # card string
        self.test_draw_card = True
        self.trade_card = {}

    
    def set_best_draw_card(self):
        if len(self.draw_card.keys()) == 5 and self.test_draw_card:
            self.test_draw_card = False
            # card which has the best score
            sorted_draw_card = sorted(self.draw_card.items(), key=lambda x: x[1], reverse=True)
            self.best_draw_card = sorted_draw_card[0][0]
            if self.debug:
                print(f"test_draw_card finished,  best draw is: {self.best_draw_card} {self.draw_card}")


    def SelectAction(self, actions, game_state):

        # reset for each turn
        self.draw_card = {}
        self.place_score = {}
        self.trade_card = {}
        self.remove_score = {}
        self.best_draw_card = None
        self.test_draw_card = True

        start_time = time.time()
        best_action = None
        best_score = 0
        board = deepcopy(game_state.board.chips)
        my_colour = game_state.agents[self.id].colour
        opponent_colour = game_state.agents[self.id].opp_colour
        visualize_board = False
        

        # if visualize_board:
        #     print(f"Current player: {self.id}, Colour: {my_colour}")
        #     self.visualize_board(board)
        
        # print(f"Opponent player: {self.id}, Colour: {opponent_colour}")
        for action in actions:
            print(f"Action: {action}")
            if time.time() - start_time > MAX_THINK_TIME:
                print(f"Action: {action}") 
                print(f"Time limit reached. Best action so far: {best_action}, Score: {best_score}")
                return best_action if best_action else random.choice(actions)
            
            action_type = action['type']
            action_coords = action['coords']
            action_play_card = action['play_card']
            action_draft_card = action['draft_card']
            score = 0
            count = 0

            draw_score = self.draw_card.get(action_draft_card, None)
            if self.test_draw_card:
                if  draw_score is None:
                    self.draw_card[action_draft_card] = self.evaluate_draw_score(action, board, game_state, my_colour, opponent_colour)
                    score += self.draw_card[action_draft_card]
                else:
                    score += draw_score
            else:
                if action_draft_card != self.best_draw_card:
                    continue
                else:
                    score += self.draw_card[self.best_draw_card]

            self.set_best_draw_card()

            
            remove_key = (action_play_card, action_coords)
            if action_type == 'remove': 
                if remove_key in self.remove_score:
                    # print(f"Remove score found: {self.remove_score[remove_key]}")
                    score += self.remove_score[remove_key]
                else:
                    score += self.evaluate_remove_score(action, board, game_state, my_colour, opponent_colour)


            if action_type == 'trade':
                print(f"Trade action: {action}")
                best_trade_card = self.trade_card.get(action_draft_card, None)  
                if not self.test_draw_card and action_draft_card == self.best_draw_card:
                    return action
                elif not self.test_draw_card and best_trade_card is not None:
                    print(f"Trade card found: {best_trade_card}")
                    return best_trade_card
                else:
                    self.trade_card[action_draft_card] = action
                    continue



            key = (action_play_card, action_coords)
            if action_type == 'place':
                if key in self.place_score:
                    # print(f"Place score found: {self.place_score[key]}")
                    score += self.place_score[key]
                else:
                    score += self.evaluate_place_score(action, board, game_state, my_colour, opponent_colour)

            if self.debug:
                print(f"Action: {action}, Score: {score}")
            if score > best_score:
                best_score = score
                best_action = action
                if self.debug:
                    print(f"Best action: {best_action}, Score: {best_score}")
                if best_score >= 17000:
                    print(f'return best action: {best_action} {best_score} \n')
                    return best_action
            else:
                continue
        if self.debug:
            print(f'return best action: {best_action} {best_score} \n')

        return best_action if best_action else random.choice(actions)
    

    def visualize_board(self, board):
        for row in board:
            print(row)

    def evaluate_place_score(self, action, board, game_state, my_colour, opponent_colour):
        r, c = action['coords']
        # draw_card = action['draft_card']
        # print(action)
        key = (action['play_card'], action['coords'])
        if action['type'] == 'place':
            score = self.test_my_current_score(r, c, board, my_colour, opponent_colour)
            self.place_score[key] = score
            return score

    def evaluate_remove_score(self, action, board, game_state, my_colour, opponent_colour):
        r, c = action['coords']
        # draw_card = action['draft_card']
        key = (action['play_card'], action['coords'])
        # print(action)
        if action['type'] == 'remove':
            score = self.test_my_remove_score(r, c, board, my_colour, opponent_colour)
            self.remove_score[key] = score
            return score
        
    def test_my_remove_score(self, r, c, board, my_colour, opponent_colour):
        # print(f"Testing remove position ({r}, {c})")
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        total_score = 0
        for dx, dy in directions:
            direction_info = DirectionInfo(dx, dy)
            direction_info.update_remove_one_side(r, c, dx, dy, board, my_colour, opponent_colour, front_back='front')
            direction_info.update_remove_one_side(r, c, -dx, -dy, board, my_colour, opponent_colour, front_back='back')
            shape, score = direction_info.calculate_remove_score()
            total_score += score
            # if self.debug:
            #     print(f"Direction {(dx,dy)} → Shape: {shape}, Score: {score}")
        return total_score

    def evaluate_draw_score(self, action, board, game_state, my_colour, opponent_colour):

        best_card = ['jd', 'jh', 'js', 'jc']

        draw_card = action['draft_card']
        # print(action)
        if draw_card in self.draw_card:
            score = self.draw_card[draw_card]
            return score
        
        if draw_card in best_card:
            self.draw_card[draw_card] = 15000
            return 15000

        cor_list = COORDS[draw_card]
        best_score = float('-inf')
        score = 0
        for r, c in cor_list:
            if board[r][c] != '_':
                continue
            score = self.test_my_current_score(r, c, board, my_colour, opponent_colour)
            if score > best_score:
                best_score = score

        self.draw_card[draw_card] = best_score       
        return best_score

    def test_my_current_score(self, r, c, board, my_colour, opponent_colour):
        # print(f"Testing position ({r}, {c})")
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        total_score = 0
        for dx, dy in directions:
            direction_info = DirectionInfo(dx, dy)
            direction_info.update_direction_one_side(r, c, dx, dy, board, my_colour, opponent_colour, front_back='front')
            direction_info.update_direction_one_side(r, c, -dx, -dy, board, my_colour, opponent_colour, front_back='back')
            shape, score = direction_info.calculate_score(r, c)
            total_score += score
            # if self.debug:
            #     print(f"Direction {(dx,dy)} → Shape: {shape}, Score: {score}")

        return total_score

    
    def in_board(self, r, c):
        return 0 <= r < 10 and 0 <= c < 10





