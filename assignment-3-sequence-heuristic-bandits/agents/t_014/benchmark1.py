# IMPORTS --------------------------------------------------------------------------------------------------
import random
from copy import deepcopy
from collections import deque
from template import Agent
from Sequence.sequence_model import SequenceGameRule as GameRule

# CONSTANTS ------------------------------------------------------------------------------------------------
NUM_PLAYERS = 2
THINKTIME = 0.98  

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
        goal_reached = new_score > prev_score
        return goal_reached

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
        import time
        start_time = time.time()

        best_action = None
        best_score = -float('inf')
        my_id = self.id
        my_state = game_state.agents[my_id]
        my_colour = my_state.colour
        opp_colour = my_state.opp_colour
        chips = game_state.board.chips
    
        # Heart of the board center positions
        heart_coords = [(4, 4), (4, 5), (5, 4), (5, 5)]

        for action in actions:
            if action['type'] == 'trade' and action['play_card']:
                return action  # trade dead card


        for action in actions:
            if time.time() - start_time > 0.98:
                break

            score = 0
            coords = action['coords']
            r, c = coords if coords else (-1, -1)

            if coords in heart_coords:
                score += 50

            if action['type'] == 'place':
                score += 10
                directions = [(1,0), (0,1), (1,1), (1,-1)]
                for dr, dc in directions:
                    count = 1
                    count += self.count_in_direction(chips, r, c, dr, dc, my_colour)
                    count += self.count_in_direction(chips, r, c, -dr, -dc, my_colour)

                    if count >= 5:
                        score += 1000
                    elif count == 4:
                        score += 500
                    elif count == 3:
                        score += 120
                    elif count == 2:
                        score += 40
                    elif count == 1:
                        score += 10

            elif action['type'] == 'remove':
                score -= 100


                directions = [(1,0), (0,1), (1,1), (1,-1)]
                for dr, dc in directions:
                    count = 1
                    count += self.count_in_direction(chips, r, c, dr, dc, opp_colour)
                    count += self.count_in_direction(chips, r, c, -dr, -dc, opp_colour)
                    if count >= 4:
                        score += 800  
                        break
                    elif count == 3:
                        score += 300

                heart_enemy = [pos for pos in heart_coords if chips[pos[0]][pos[1]] == opp_colour]
                if coords in heart_coords and len(heart_enemy) >= 2:
                    score += 600  
            

            if score > best_score:
                best_score = score
                best_action = action

        return best_action if best_action else random.choice(actions)





#####################################################
#####################################################

#####################################################
#####################################################

#####################################################
#####################################################















