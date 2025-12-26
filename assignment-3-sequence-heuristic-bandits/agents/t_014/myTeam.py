# IMPORTS --------------------------------------------------------------------------------------------------
import random
from template import Agent
from Sequence.sequence_model import SequenceGameRule
from Sequence.sequence_model import COORDS, EMPTY
import time

# CONSTANTS -------------------------------------------------------------------------------------------------
NUM_PLAYERS = 2
THINKTIME = 0.98  # time limitation

# heat map
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

class myAgent(Agent):

    def __init__(self, _id):
        super().__init__(_id)
        self.id = _id
        self.game_rule = SequenceGameRule(NUM_PLAYERS)

    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    def DoAction(self, state, action):
        prev_score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        new_score = state.agents[self.id].score
        return new_score > prev_score

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

        for action in actions:
            if time.time() - start_time > 0.90:
                break

            score = 0
            coords = action['coords']
            if coords:
                r, c = coords
                score += POS_WEIGHT[r][c]
                directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                for dr, dc in directions:
                    count = 1
                    for i in range(1, 5):
                        nr, nc = r + dr*i, c + dc*i
                        if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == my_colour:
                            count += 1
                        else:
                            break
                    for i in range(1, 5):
                        nr, nc = r - dr*i, c - dc*i
                        if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == my_colour:
                            count += 1
                        else:
                            break
                    if count >= 5:
                        score += 15000
                    elif count == 4:
                        score += 10000
                    elif count == 3:
                        score += 9000
                    elif count == 2:
                        score += 40

            if action['type'] == 'remove':
                score -= 100  # discourage random remove
                r, c = action['coords']
                directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                for dr, dc in directions:
                    connect = 1
                    for i in range(1, 5):
                        nr, nc = r + dr*i, c + dc*i
                        if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == opp_colour:
                            connect += 1
                        else:
                            break
                    for i in range(1, 5):
                        nr, nc = r - dr*i, c - dc*i
                        if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == opp_colour:
                            connect += 1
                        else:
                            break
                    if connect >= 4:
                        score += 12000
                        break

            draft_card = action['draft_card']
            if draft_card in ['jc', 'jd', 'jh', 'js']:
                score += 1000
            elif draft_card in COORDS:
                for r, c in COORDS[draft_card]:
                    if chips[r][c] == EMPTY:
                        score += POS_WEIGHT[r][c] /2

            if score > best_score:
                best_score = score
                best_action = action

        return best_action if best_action else random.choice(actions)
