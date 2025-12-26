# IMPORTS --------------------------------------------------------------------------------------------------
import copy
import random
from template import Agent
from Sequence.sequence_model import SequenceGameRule
from Sequence.sequence_model import COORDS, EMPTY
import time
import numpy as np
import traceback


# CONSTANTS -------------------------------------------------------------------------------------------------
NUM_PLAYERS = 2


def generate_pos_weight(size=10, sigma=3.5, peak=15):

    ax = np.arange(size) - (size - 1) / 2.0
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2))
    kernel = kernel / kernel.max() * peak
    return kernel.round().astype(int).tolist()

# POS_WEIGHT IS THE IDEA BORROWED FROM TAOYUAN LIU
POS_WEIGHT = generate_pos_weight(size=10, sigma=3.5, peak=15)
class myAgent(Agent):

    def __init__(self, _id):
        super().__init__(_id)
        self.id = _id
        self.game_rule = SequenceGameRule(NUM_PLAYERS)
        self.opp_actions = set()
        self.cached_opp_score = {}
        self.cached_my_score = {}


    def DoAction(self, board, chips, action, my_colour):

        if action['type'] == 'place':
            r, c = action['coords']
            board[r][c] = 1
            chips[r][c] = my_colour

        elif action['type'] == 'remove':
            r, c = action['coords']
            board[r][c] = 0
            chips[r][c] = EMPTY

        return board, chips

    def SelectAction(self, actions, game_state):
        start_time = time.time()

        my_id = self.id
        my_state = game_state.agents[my_id]
        my_colour = my_state.colour
        opp_colour = my_state.opp_colour
        chips = game_state.board.chips

        # used to look up cache
        board_np = np.array(chips)
        mapped = np.where(board_np == my_colour, 1,
                          np.where(board_np == opp_colour, -1, 0)).astype(int)

        # observe opp's last action
        opp_id = abs(1 - self.id)
        try:
            opp_action = game_state.agents[opp_id].last_action
            opp_play_card = opp_action['play_card']
            opp_draft_card = opp_action['draft_card']
            opp_type = opp_action['draft_card']
            opp_coords = opp_action['coords']
            # UPDATE OPP's possible actions
            if (opp_play_card, opp_type, opp_coords) in self.opp_actions:
                self.opp_actions.remove((opp_play_card, opp_type, opp_coords))
            if opp_draft_card and opp_draft_card not in ('jd', 'jc', 'jh', 'js'):
                for (r, c) in COORDS[opp_draft_card]:
                    if chips[r][c] == EMPTY:
                        self.opp_actions.add((opp_draft_card, "place", (r, c)))
        except Exception as e:
            print("No last action detected")


        best_action = self.MiniMax(actions, start_time, mapped, chips, my_colour, opp_colour)

        if (best_action['play_card'], "place", best_action['coords']) in self.opp_actions:
            self.opp_actions.remove((best_action['play_card'], "place", best_action['coords']))

        return best_action if best_action else random.choice(actions)

    def MiniMax(self, actions, start_time, mapped, chips, my_colour, opp_colour):
        best_action = None
        best_score = -float('inf')

        for action in actions:
            try:
                if time.time() - start_time > 0.90:
                    print("TIMEOUT")
                    break

                score = 0
                coords = action['coords']
                '''
                MAX: SEARCH for MAX possible reward among my actions
                '''
                if coords:

                    r, c = coords

                    score += POS_WEIGHT[r][c]
                    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

                    # used to search for cached score
                    lines = self.get_lines(mapped, r, c)
                    place_score = 0

                    for dr, dc in directions:
                        line_key = lines[(dr, dc)].tobytes()
                        if ((r,c), (dr, dc), line_key) in self.cached_my_score:
                            place_score += self.cached_my_score[((r,c), (dr, dc), line_key)]
                        else:
                            count, forward, backward = self.search_count(chips, 1, my_colour, opp_colour, r, c, dr, dc)
                            place_score += self.compute_score(count, forward, backward, lines, dr, dc)
                            if count == 1 and not forward and not backward:
                                place_score -= 10000
                            self.cached_my_score[((r,c), (dr, dc), line_key)] = place_score

                    score += place_score

                if action['type'] == 'remove':
                    r, c = action['coords']
                    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

                    for dr, dc in directions:
                        connect, forward, backward = self.search_count(chips, 1, my_colour, opp_colour, r, c, dr, dc)

                        if connect >= 4:
                            score += 12000
                            break

                mapped_copy, chips_copy = self.DoAction(copy.deepcopy(mapped), copy.deepcopy(chips), action, my_colour)

                '''
                MIN: FOR each action of Mine applied, compute the opponent's highest possible reward 
                '''
                max_opp_score = -float('inf')
                for play_card, action_type, coords in self.opp_actions:

                    r, c = coords

                    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                    lines = self.get_lines(mapped_copy, r, c)
                    opp_score = 0

                    for dr, dc in directions:
                        line_key = lines[(dr, dc)].tobytes()
                        if ((r, c), (dr, dc), line_key) in self.cached_opp_score:
                            opp_score += self.cached_opp_score[((r,c), (dr, dc), line_key)]
                        else:

                            count, forward, backward = self.search_count(chips_copy, 1, opp_colour, my_colour, r, c, dr, dc)
                            opp_score += self.compute_score(count, forward, backward, lines, dr, dc)

                            self.cached_opp_score[((r,c), (dr, dc), line_key)] = opp_score

                    opp_score = POS_WEIGHT[r][c]
                    if opp_score > max_opp_score:
                        max_opp_score = opp_score


                max_opp_score = 0 if max_opp_score == -float('inf') else max_opp_score

                # subtract MIN with 0.9 future decay
                score -= 0.9 * max_opp_score

                # compute draft score prefer jc, jd
                draft_card = action['draft_card']

                max_draft_score = 0

                if draft_card in ['jc', 'jd']:
                    max_draft_score += 15000
                elif draft_card in ['js', 'jh']: # 避免搜索
                    max_draft_score += 8000
                else:
                    if draft_card in COORDS:
                        for r, c in COORDS[draft_card]:
                            if chips_copy[r][c] == EMPTY:
                                draft_score = 0
                                directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                                lines = self.get_lines(mapped_copy, r, c)
                                for dr, dc in directions:
                                    line_key = lines[(dr, dc)].tobytes()
                                    if ((r, c), (dr, dc), line_key) in self.cached_my_score:
                                        draft_score += self.cached_my_score[((r,c), (dr, dc), line_key)]
                                    else:
                                        count, forward, backward = self.search_count(chips_copy, 1, my_colour, opp_colour, r, c, dr, dc)
                                        draft_score += self.compute_score(count, forward, backward, lines, dr, dc)

                                        self.cached_my_score[((r,c), (dr, dc), line_key)] = draft_score

                                draft_score += POS_WEIGHT[r][c]

                                if draft_score > max_draft_score:
                                    max_draft_score = draft_score

                score += 0.8 * max_draft_score

                if score > best_score:
                    best_score = score
                    best_action = action

            except Exception as e:
                print("ERROR!!!!")
                traceback.print_exc()

        return best_action

    def search_count(self, chips, count, my_colour, opp_colour, r, c, dr, dc):

        forward = True
        backward = True

        for i in range(1, 5):
            nr, nc = r + dr * i, c + dc * i
            if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == my_colour:
                count += 1
            elif 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == opp_colour:
                forward = False
            elif not (0 <= nr < 10) or not (0 <= nc < 10):
                forward = False
            else:
                break

        for i in range(1, 5):
            nr, nc = r - dr * i, c - dc * i
            if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == my_colour:
                count += 1
            elif 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == opp_colour:
                backward = False
            elif not (0 <= nr < 10) or not (0 <= nc < 10):
                backward = False
            else:
                break

        return count, forward, backward



    def compute_score(self, connection_count, forward, backward, lines, dr, dc):
        score = 0

        if connection_count >= 5:
            score += 20000
        elif connection_count == 4 and forward and backward:
            score += 12000
        elif connection_count == 4 and (forward or backward):
            score += 10000
        elif connection_count == 3 and forward and backward:
            score += 8000
        elif connection_count == 3 and (forward or backward) and len(lines[(dr, dc)]) >= 6:
            score += 6000
        elif connection_count == 2 and forward and backward and len(lines[(dr, dc)]) >= 5:
            score += 200
        elif connection_count == 2 and (forward or backward) and len(lines[(dr, dc)]) >= 5:
            score += 40

        return score

    def get_lines(self, chips, r, c):
        N = 10

        row = chips[r]  # (0,1)
        col = chips[:, c]  # (1,0)
        main_diag = np.diagonal(chips, c - r)  # (1,1) ↘
        anti_diag = np.diagonal(np.fliplr(chips),
                                (N - 1 - c) - r)  # (1,-1) ↙
        return {(1, 0): col,
                (0, 1): row,
                (1, 1): main_diag,
                (1, -1): anti_diag}