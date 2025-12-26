import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import glob
import time
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
from Sequence.sequence_model import SequenceGameRule
# from agents.generic.random import myAgent as OpponentAgent
from template import Agent
from Sequence.sequence_model import BOARD

from collections import deque


from agents.generic.random import myAgent as RandomAgent
from agents.t_014.BruteForceTy import myAgent as BruteForceAgent
from agents.t_014.BruteForceTyS import myAgent as BruteForceSmartAgent
from agents.t_014.HeStar import myAgent as HeStarAgent

POS_WEIGHT = np.array([
    [ 3, 4, 5, 5, 5, 5, 5, 5, 4, 3],
    [ 4, 6, 7, 7, 7, 7, 7, 7, 6, 4],
    [ 5, 7, 9,10,10,10,10, 9, 7, 5],
    [ 5, 7,10,12,12,12,12,10, 7, 5],
    [ 5, 7,10,12,15,15,12,10, 7, 5],
    [ 5, 7,10,12,15,15,12,10, 7, 5],
    [ 5, 7,10,12,12,12,12,10, 7, 5],
    [ 5, 7, 9,10,10,10,10, 9, 7, 5],
    [ 4, 6, 7, 7, 7, 7, 7, 7, 6, 4],
    [ 3, 4, 5, 5, 5, 5, 5, 5, 4, 3],
])


def evaluate_line_pattern(chips, r, c, my_colour):
    """ gomoku """
    score = 0
    for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
        line = ""
        for i in range(-4, 5):
            nr, nc = r + i * dr, c + i * dc
            if 0 <= nr < 10 and 0 <= nc < 10:
                chip = chips[nr][nc]
                if chip == my_colour:
                    line += "X"
                elif chip == '.':
                    line += "_"
                else:
                    line += "O"
            else:
                line += "O"

        if "XXXX_" in line or "_XXXX" in line:
            score += 50
        elif "XXX__" in line or "__XXX" in line:
            score += 30
        elif "XX__X" in line or "X__XX" in line:
            score += 20
    return score

def get_opponent_for_episode(_):
    return random.choice([
        RandomAgent(1),
        BruteForceAgent(1),
        HeStarAgent(1),
        BruteForceSmartAgent(1)
    ])

opponent_history = deque(maxlen=5)

os.makedirs("agents/t_014/Qmodels", exist_ok=True)

NUM_EPISODES = 10000
GAMMA = 0.99
LR = 1e-3
EPSILON_START = 1.0
EPSILON_END = 0.1
EPSILON_DECAY = 0.995
BATCH_SIZE = 64
REPLAY_SIZE = 10000


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class QNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(417 + 1, 512),     # +1 for combo flag
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 1)
        )

    def forward(self, state_action):
        return self.net(state_action)
    
    
def encode_state(game_state, agent_id, combo_flag=False):
    chips = game_state.board.chips
    my_colour = game_state.agents[agent_id].colour
    opp_colour = game_state.agents[agent_id].opp_colour

    board_planes = np.zeros((10, 10, 3))
    for r in range(10):
        for c in range(10):
            if chips[r][c] == my_colour:
                board_planes[r][c][0] = 1
            elif chips[r][c] == opp_colour:
                board_planes[r][c][1] = 1
            elif chips[r][c] != '.':
                board_planes[r][c][2] = 1
    board_flat = board_planes.flatten()

    def one_hot_cards(cards):
        deck = ['2','3','4','5','6','7','8','9','t','j','q','k','a']
        suits = ['d','c','h','s']
        all_cards = [r + s for r in deck for s in suits] + ['jc','jd','jh','js']
        vec = np.zeros(len(all_cards))
        for c in cards:
            if c in all_cards:
                vec[all_cards.index(c)] = 1
        return vec

    hand_vec = one_hot_cards(game_state.agents[agent_id].hand)
    draft_vec = one_hot_cards(game_state.board.draft)
    
    # combo flag: 0 or 1, appended as last feature
    combo_feature = np.array([1.0 if combo_flag else 0.0])
    
    return np.concatenate([board_flat, hand_vec, draft_vec, combo_feature])


def encode_action(action):
    coords = action['coords'] if action['coords'] else (-1, -1)
    draft_hash = hash(action['draft_card']) % 1000 if action['draft_card'] else 0
    return np.array([
        hash(action['play_card']) % 1000,
        hash(action['type']) % 1000,
        draft_hash,
        coords[0],
        coords[1]
    ]) / 1000.0

def evaluate_action_reward(action, state, agent_id):
    reward = 0
    my_colour = state.agents[agent_id].colour
    opp_colour = state.agents[agent_id].opp_colour
    chips = state.board.chips
    coords = action.get('coords', None)
    play_card = action.get('play_card', None)
    draft_card = action.get('draft_card', None)
    action_type = action.get('type')
    heart_coords = [(4, 4), (4, 5), (5, 4), (5, 5)]
    corner_surround = [(0,1),(1,0),(1,1),(0,8),(1,8),(1,9),(8,0),(8,1),(9,1),(8,8),(8,9),(9,8)]

    # defence
    if coords and chips[coords[0]][coords[1]] == '.':
        for dr, dc in [(1,0),(0,1),(1,1),(1,-1)]:
            block_count = 1
            for i in range(1, 3):
                nr, nc = coords[0]+dr*i, coords[1]+dc*i
                if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == opp_colour:
                    block_count += 1
                else:
                    break
            for i in range(1, 3):
                nr, nc = coords[0]-dr*i, coords[1]-dc*i
                if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == opp_colour:
                    block_count += 1
                else:
                    break
            if block_count >= 3:
                reward += 100

    # Joker award
    if play_card and play_card.startswith('j'):
        reward += 100
    if draft_card and draft_card.startswith('j'):
        reward += 50

    # defence for opp_heat
    threat_map = analyze_opponent_threats(chips, opp_colour)
    if coords:
        r, c = coords
        if threat_map[r][c] > 0:
            reward += 40 * threat_map[r][c]

    # center control
    if coords:
        dist_to_center = ((coords[0] - 4.5) ** 2 + (coords[1] - 4.5) ** 2) ** 0.5
        reward += max(0, 15 - dist_to_center * 2.5)  # 控制在 0~15 范围

    # 4-sides
    if coords in corner_surround:
        reward += 25

    # heart of board
    if coords in heart_coords:
        reward += 50
        if threat_map[r][c] > 0:
            reward += 30

    # my_line + Potential line score + backgammon line recognition
    if action_type == 'place' and coords:
        r, c = coords
        for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            count = 1
            for i in range(1, 5):
                nr, nc = r + dr * i, c + dc * i
                if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == my_colour:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                nr, nc = r - dr * i, c - dc * i
                if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == my_colour:
                    count += 1
                else:
                    break
            if count >= 5:
                reward += 300
            elif count == 4:
                reward += 150
            elif count == 3:
                reward += 60
            elif count == 2:
                reward += 20

        # backgammon line recognition
        reward += evaluate_line_pattern(chips, r, c, my_colour)

    # backgammon line recognition --- post
    if coords:
        reward += POS_WEIGHT[coords[0]][coords[1]]

    return reward


# -------------------------------------

from Sequence.sequence_model import SequenceGameRule
from agents.t_014.BruteForceTyS import myAgent as BruteOpponent
from copy import deepcopy

def simulate_with_opponent_response(game, state, action, agent_id):
    from copy import deepcopy
    temp_game = deepcopy(game)

    #  temp_game status --> suppose the same as now
    legal_actions = temp_game.getLegalActions(temp_game.current_game_state, agent_id)

    # find action linked 
    def is_same_action(a1, a2):
        return (
            a1['type'] == a2['type'] and
            a1['play_card'] == a2['play_card'] and
            a1.get('draft_card') == a2.get('draft_card') and
            a1.get('coords') == a2.get('coords')
        )

    matched_action = None
    for a in legal_actions:
        if is_same_action(a, action):
            matched_action = a
            break

    if matched_action is None:
        # if none --> return 0
        return 0

    # update temp_game
    temp_game.update(matched_action)
    next_state = temp_game.current_game_state

    # how opp thoughts?
    opp_id = 1 - agent_id
    opp_agent = BruteOpponent(opp_id)
    opp_actions = temp_game.getLegalActions(next_state, opp_id)
    if not opp_actions:
        return 0

    opp_action = opp_agent.SelectAction(opp_actions, next_state)
    chips_before = deepcopy(next_state.board.chips)
    temp_game.current_agent_index = opp_id
    temp_game.update(opp_action)
    chips_after = temp_game.current_game_state.board.chips

    my_colour = state.agents[agent_id].colour
    opp_colour = state.agents[agent_id].opp_colour

    delta = 0
    for r in range(10):
        for c in range(10):
            before = chips_before[r][c]
            after = chips_after[r][c]
            if before == my_colour and after != my_colour:
                delta -= 1
            if before != opp_colour and after == opp_colour:
                delta += 1

    return delta * 50


# -------------------------------------



def analyze_opponent_threats(chips, opp_colour):
    """heat map"""
    threat_map = np.zeros((10, 10))
    for r in range(10):
        for c in range(10):
            if chips[r][c] == '.':
                for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    count = 0
                    for i in range(1, 3):
                        nr, nc = r + dr * i, c + dc * i
                        if 0 <= nr < 10 and 0 <= nc < 10 and chips[nr][nc] == opp_colour:
                            count += 1
                    if count >= 2:
                        threat_map[r][c] += count
    return threat_map



class DQNAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)
        self.id = _id
        self.q_net = QNetwork().to(device)
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=LR)
        self.replay = deque(maxlen=REPLAY_SIZE)
        self.epsilon = EPSILON_START

    def select_action(self, actions, state):
        start_time = time.time()
        state_vec = encode_state(state, self.id)

        if random.random() < self.epsilon:
            return random.choice(actions)

        best_score = -float('inf')
        best_action = random.choice(actions)
        for a in actions:
            if time.time() - start_time > 0.98:
                break
            action_vec = encode_action(a)
            input_vec = np.concatenate([state_vec, action_vec])
            with torch.no_grad():
                score = self.q_net(torch.tensor(input_vec, dtype=torch.float32).to(device)).item()
            if score > best_score:
                best_score = score
                best_action = a

        return best_action

    def save_model(self, path):
        torch.save(self.q_net.state_dict(), path)

    def load_model(self, path):
        self.q_net.load_state_dict(torch.load(path, map_location=device))
        self.q_net.eval()

    def train_step(self):
        if len(self.replay) < BATCH_SIZE:
            return
        batch = random.sample(self.replay, BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*batch)

        input_vecs = [np.concatenate([s, a]) for s, a in zip(states, actions)]
        input_tensor = torch.tensor(np.array(input_vecs), dtype=torch.float32).to(device)
        q_values = self.q_net(input_tensor).squeeze()

        next_qs = []
        for ns, done in zip(next_states, dones):
            dummy_a = np.zeros_like(actions[0])
            next_input = np.concatenate([ns, dummy_a])
            next_q = self.q_net(torch.tensor(next_input, dtype=torch.float32).to(device)).item() if not done else 0.0
            next_qs.append(next_q)

        targets = torch.tensor([0.4 * r + 0.6 * GAMMA * nq for r, nq in zip(rewards, next_qs)], dtype=torch.float32).to(device)
        loss = nn.MSELoss()(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def remember(self, s, a, r, s_, done):
        self.replay.append((s, a, r, s_, done))

def caused_combo(prev_score, new_score):
    return new_score > prev_score


def train():
    game = SequenceGameRule(2)
    agent = DQNAgent(0)


    for episode in range(NUM_EPISODES):
        opponent = get_opponent_for_episode(episode)
        print(f"\n=== Episode {episode+1}/{NUM_EPISODES} ===", flush=True)
        state = game.initialGameState()
        done = False
        game.current_game_state = state
        game.current_agent_index = 0

        while not game.gameEnds():
            current_id = game.current_agent_index
            actions = game.getLegalActions(game.current_game_state, current_id)

            if current_id == agent.id:
                prev_score = game.current_game_state.agents[agent.id].score
                action = agent.select_action(actions, game.current_game_state)
                s_vec = encode_state(game.current_game_state, agent.id)
                a_vec = encode_action(action)
                game.update(action)
                new_score = game.current_game_state.agents[agent.id].score 
                combo_flag = caused_combo(prev_score, new_score)
                r_imm = evaluate_action_reward(action, game.current_game_state, agent.id)
                r_opp = simulate_with_opponent_response(game, game.current_game_state, action, agent.id)
                reward = 0.4 * r_imm + 0.6 * r_opp  # mixed with weights not good still

                s1_vec = encode_state(game.current_game_state, agent.id)
                done = game.gameEnds()
                agent.remember(s_vec, a_vec, reward, s1_vec, done)
                agent.train_step()
            else:
                action = opponent.SelectAction(actions, game.current_game_state)
                game.update(action)
                
                # remeberopp does
                opponent_history.append(action)

        print(f"Episode {episode + 1} finished. Score = {game.current_game_state.agents[agent.id].score}")
        agent.epsilon = max(EPSILON_END, agent.epsilon * EPSILON_DECAY)

        if (episode + 1) % 500 == 0:
            try:
                existing = glob.glob("agents/t_014/Qmodels/dqn_model_ep*.pth")
                indices = [int(f.split("ep")[1].split(".")[0]) for f in existing if "ep" in f]
                next_idx = max(indices) + 500 if indices else 500
            except Exception as e:
                print("Error determining model index:", e)
                next_idx = 500

            save_path = f"agents/t_014/Qmodels/dqn_model_ep{next_idx}.pth"
            agent.save_model(save_path)
            agent.save_model("agents/t_014/Qmodels/dqn_model_latest.pth")

class myAgent(DQNAgent):
    def __init__(self, _id):
        super().__init__(_id)
        self.load_model("agents/t_014/Qmodels/dqn_model_latest.pth")

if __name__ == '__main__':
    train()
