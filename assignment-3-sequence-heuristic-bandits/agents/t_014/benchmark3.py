# IMPORTS --------------------------------------------------------------------------------------------------
import random
from copy import deepcopy
from collections import deque
from template import Agent
from Sequence.sequence_model import SequenceGameRule as GameRule
from Sequence.sequence_model import COORDS, EMPTY
import time

# CONSTANTS -------------------------------------------------------------------------------------------------
NUM_PLAYERS = 2
THINKTIME = 0.98  

POS_WEIGHT = [
    [3, 4, 5, 5, 5, 5, 5, 5, 4, 3],
    [4, 6, 7, 7, 7, 7, 7, 7, 6, 4],
    [5, 7, 9,10,10,10,10, 9, 7, 5],
    [5, 7,10,12,12,12,12,10, 7, 5],
    [5, 7,10,12,15,15,12,10, 7, 5],
    [5, 7,10,12,15,15,12,10, 7, 5],
    [5, 7,10,12,12,12,12,10, 7, 5],
    [5, 7, 9,10,10,10,10, 9, 7, 5],
    [4, 6, 7, 7, 7, 7, 7, 7, 6, 4],
    [3, 4, 5, 5, 5, 5, 5, 5, 4, 3]
]
CORNER_SURROUND = [(0,1),(1,0),(1,1),(0,8),(1,8),(1,9),(8,0),(8,1),(9,1),(8,8),(8,9),(9,8)]




# AGENT CLASS -----------------------------------------------------------------------------------------------
class myAgent(Agent):

    def __init__(self, _id):
        super().__init__(_id)
        self.id = _id
        self.game_rule = GameRule(NUM_PLAYERS)

    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    def DoAction(self, state, action):
        prev_score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        new_score = state.agents[self.id].score
        return new_score > prev_score

    def count_in_direction(self, chips, r, c, dr, dc, my_colour):
        count = 0
        for i in range(1, 5):
            nr, nc = r + dr * i, c + dc * i
            if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == my_colour:
                count += 1
            else:
                break
        return count

    def SelectAction(self, actions, game_state):
        start_time = time.time()

        best_action = None
        best_score = -float('inf')
        my_id = self.id
        my_state = game_state.agents[my_id]
        my_colour = my_state.colour
        opp_colour = my_state.opp_colour
        chips = game_state.board.chips
        draft_choices = game_state.board.draft
        heart_coords = [(4, 4), (4, 5), (5, 4), (5, 5)]

        for action in actions:
            if action['type'] == 'trade' and action['play_card']:
                return action

        base_actions = []
        for action in actions:
            if action['type'] in ['place', 'remove']:
                base_action = {
                    'play_card': action['play_card'],
                    'type': action['type'],
                    'coords': action['coords']
                }
                base_actions.append(base_action)

        for base_action in base_actions:
            if time.time() - start_time > 0.90:
                break

            score = 0
            coords = base_action['coords']
            r, c = coords if coords else (-1, -1)

            if coords in heart_coords:
                score += 80

            if base_action['type'] == 'place':
                score += 10

                score += POS_WEIGHT[r][c]

                if coords in CORNER_SURROUND:
                    score += 20

                if coords in heart_coords:
                    score += 50

                directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                for dr, dc in directions:
                    count = 1
                    count += self.count_in_direction(chips, r, c, dr, dc, my_colour)
                    count += self.count_in_direction(chips, r, c, -dr, -dc, my_colour)
                    if count >= 5:
                        score += 1000
                    elif count == 4:
                        score += 900
                    elif count == 3:
                        score += 120
                    elif count == 2:
                        score += 40
                    elif count == 1:
                        score += 10

            elif base_action['type'] == 'remove':
                score -= 100
                directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                for dr, dc in directions:
                    count = 1
                    count += self.count_in_direction(chips, r, c, dr, dc, opp_colour)
                    count += self.count_in_direction(chips, r, c, -dr, -dc, opp_colour)
                    if count >= 4:
                        score += 800
                        break
                    elif count == 3:
                        score += 300
                        
                    if coords in heart_coords:
                        heart_enemy = [pos for pos in heart_coords if chips[pos[0]][pos[1]] == opp_colour]
                        if len(heart_enemy) >= 2:
                            score += 600
                        else:
                            score += 200  
                heart_enemy = [pos for pos in heart_coords if chips[pos[0]][pos[1]] == opp_colour]
                if coords in heart_coords and len(heart_enemy) >= 2:
                    score += 600

            best_draft = None
            best_draft_score = -float('inf')
            for draft in draft_choices:
                d_score = self.score_draft_card(draft, my_state, chips)
                if d_score > best_draft_score:
                    best_draft = draft
                    best_draft_score = d_score

            score += 0.3 * best_draft_score

            full_action = {
                'play_card': base_action['play_card'],
                'draft_card': best_draft,
                'type': base_action['type'],
                'coords': base_action['coords']
            }

            if score > best_score:
                best_score = score
                best_action = full_action

        return best_action if best_action else random.choice(actions)

    def score_draft_card(self, draft_card, my_state, board_chips):
        score = 0
        my_colour = my_state.colour
        opp_colour = my_state.opp_colour

        if draft_card in ['jc', 'jd', 'jh', 'js']:
            return 999  

        if draft_card in COORDS:
            for r, c in COORDS[draft_card]:
                if board_chips[r][c] == EMPTY:
                    score += POS_WEIGHT[r][c]
                    if (r, c) in CORNER_SURROUND:
                        score += 15

                    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                    for dr, dc in directions:
                        count = 1
                        count += self.count_in_direction(board_chips, r, c, dr, dc, my_colour)
                        count += self.count_in_direction(board_chips, r, c, -dr, -dc, my_colour)
                        if count >= 5:
                            score += 1000
                        elif count == 4:
                            score += 500
                        elif count == 3:
                            score += 120
                        elif count == 2:
                            score += 40

                    near_heart = any(abs(r - hr) <= 1 and abs(c - hc) <= 1 for hr, hc in [(4,4),(4,5),(5,4),(5,5)])
                    if near_heart:
                        score += 20
                        
            for r, c in COORDS[draft_card]:
                if board_chips[r][c] == EMPTY:
                    enemy_threat = 0
                    for dr, dc in [(1,0),(0,1),(1,1),(1,-1)]:
                        threat = 0
                        for i in range(1, 3):
                            nr, nc = r + dr*i, c + dc*i
                            if 0 <= nr < 10 and 0 <= nc < 10 and board_chips[nr][nc] == opp_colour:
                                threat += 1
                            else:
                                break
                        for i in range(1, 3):
                            nr, nc = r - dr*i, c - dc*i
                            if 0 <= nr < 10 and 0 <= nc < 10 and board_chips[nr][nc] == opp_colour:
                                threat += 1
                            else:
                                break
                        if threat >= 2:
                            enemy_threat += threat

                    score += enemy_threat * 10

        return score
