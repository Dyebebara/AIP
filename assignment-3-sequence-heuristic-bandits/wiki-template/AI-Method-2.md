# AI Method 2 - SARSA

Your notes about this part of the project, including acknowledgement, comments, strengths and limitations, etc.

You **do not** need to explain the algorithm. Please tell us how you used it and how you applied it in your team.

If you use greed best first search, then, you can explain about what is the problem (state space model, especially how you define the state, how your define the goal), and heuristic function (as specific as possible) that you used. 

If you use MCTS, then, you can explain about what tree policy/simulation policy you used, how many iteration did you run, what is your reward function, the depth of each simulation etc.

# Table of Contents
  * [Motivation](#motivation)
  * [Application](#application)
    - [Reward system](#1-greedy-rewardscore-system-directioninfo)
    - [State representation](#2-state-representation)
    - [How Q table update](#q-table-update-mechanism)
  * [Solved challenges](#solved-challenges)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)
 
### Motivation  
Key words: Q-learning, strategy-based, feature engineering, heuristic reward, mix score

Using the full board state and discard pile directly as the state leads to an almost unmanageable number of possible states. Given the vastness of the state space and the large branching factor for actions, the total number of state-action pairs quickly becomes astronomical. In theory, multiplying approximately 10^50 or more possible board states by up to 10^3 available actions yields approximately 10^53 to 10^54 state-action pairs, which is computationally infeasible.

To address this issue, the SARSA agent uses feature engineering to compress the 10x10 board states into an eleven-dimensional feature vector. This not only reduces memory requirements dramatically but also improves the generalisation capability of the agent. 

In this design, each board configuration is converted into an abstract “strategy-based” feature vector that captures essential tactical patterns rather than memorising every possible arrangement. This enables the agent to generalise its learning across countless similar situations, making decisions based on strategic considerations rather than exhaustive enumeration. When a particular board pattern emerges, the agent selects the corresponding strategy, focusing on the most important aspect of the game at that moment.

The core of this method is the use of Q-learning with a strategy-based representation, where the scoring function combines long-term value and immediate tactical gain:
```
score = 0.6 × Q-value + 0.4 × current action reward (heuristic)
```

[Back to top](#table-of-contents)

### Application 

#### 1 Greedy Reward(Score system DirectionInfo)


To simplify the game, I first conceptualised Sequence as a variant of Gomoku (Five-in-a-Row). In this abstraction, there are no actions for drawing, discarding, or removing chips. In other words, every player is assumed to hold only "Two-Eyed Jacks" and thus can place/remove a chip freely anywhere on the board.

I designed a class DirectionInfo(dx, dy) (full version in `score.py`)to evaluate the potential score of placing a chip at a particular location in a given direction. Based on the state of connections in that direction (e.g., continuous alignment, gaps, or blocking), a score is calculated. The higher the score, the more favourable it is to place a chip at that position.

Each direction — one of [(1, 0), (0, 1), (1, 1), (1, -1)] — is evaluated using the following attributes:

- self.dx/dy: The current direction vector.

- self.connect_count = 1: The maximum uninterrupted connection with existing current agent colour chips after placing. Example: _oooo_ yields connect = 4.

- self.mid_gap_count = 0: Allows maximum two empty gaps between connected chips. Example: _oo_o_o_ implies gap = 2.

- self.discrete_count_front/back = 0 Discrete chip count on each side of the placement, at that time implies mid_gap_count > 0 : _current_ooo_  discrete_count = 3

- self.open_front/back = False Indicates whether the sequence is blocked on one end (e.g., by the board edge(include '#') or opponent's chip) _oox  connect = 2 open_back = False

These attributes are evaluated in all four directions, and the scores for each potential placement are calculated accordingly. The evaluation assigns different heuristic values:

- LIVE: Both ends are open (open_front & open_back).

- SLEEP: A relaxed version of LIVE, allowing gaps (via mid_gap_count <= 2 and open_front / open_back).

LIVE_FOUR implies two ways to win, while CHONG_FOUR (with a gap or blocked on one end) only has one, hence it receives a slightly lower score. LIVE_FIVE denotes an immediate win.


- self.NONE = 0: Both ends blocked, no useful alignment not open_front/back

- self.LIVE_ONE = 1  One chip placed with both ends open. open_front&back

- self.SLEEP_TWO = 2 wo aligned with one end blocked; may include a gap.

- self.LIVE_TWO = 30

- self.SLEEP_THREE = 40

- self.LIVE_THREE = 9000

- self.CHONG_FOUR = 9000

- self.LIVE_FOUR = 10000

- self.LIVE_FIVE = 15000

Both 'remove' & 'place' action can be used to block an opponent's action. Increasing the number of connections on your side while decreasing the number on the enemy side is a good strategy. Here are the rewards for blocking the enemy:

- self.OPP_LIVE_FOUR = 12000 
        
- self.OPP_LIVE_THREE = 1000

- self.OPP_LIVE_FIVE = 13000


##### Score Process

This scoring system will later be integrated into Q-learning(SARSA), following the earlier formulation of the problem as a Markov Decision Process (MDP).

The reward function maintains four dictionaries to ensure that scores do not need to be recalculated for repeated (card, coordinate) pairs:

- self.draw_card = {}: Scores for drawing a card; length == 5 (matching the number of draft options).

- self.place_score = {}: Keyed by (card, coordinate); stores the score of placing a card at a given position.

- self.trade_card = {}: Stores the optimal trade option based on draw value.

- self.remove_score = {}: Stores the score for removing an opponent's chip.

For each action in actions list like: {'play_card': '2s', 'draft_card': 'jd', 'type': 'place', 'coords': (0, 1)}

For the draw_card dictionary, since there are only 5 draft options, after scoring all of them, the card with the highest draw score is selected as the best_draft_card. All actions not using this card will be skipped to save computation time (if draft_card != best_draft_card: skip). If a trade action exists in the action list, the one involving the best_draft_card will be prioritised over all other actions.

For place_score, the scoring is computed using update_direction_one_side() from the DirectionInfo class for all possible placements in the actions list. The score for each state is combined with the value of the best_draft_card.

For remove_score, the score is calculated using update_remove_one_side() from DirectionInfo. The removal scoring only considers self.LIVE_FOUR; the agent will only interfere with the opponent's plans at critical moments. In all other cases, the removal score is set to 0.

#### 2 State representation


The function `encode_state(self, game_state)` is used to encode the current board state. Since the full state space of a 10x10 board is 3^96, using this directly as the state for the Q-table would render it far too large to be impractical for learning or storage purposes.  Therefore, I adopt a feature abstraction approach, representing each position by a statistical feature vector as follows:

```
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
```

Each feature represents the number of times of a certain connection pattern (e.g. "LIVE_TWO" or "LIVE_FOUR") for either the agent or the opponent on the board. For example, all cases of "LIVE_TWO" (i.e. \_oo\_) anywhere on the board are counted into the same feature, regardless of their exact position on the board.  This significantly reduces the state space and improves the generalisation ability of Q-learning.

Similarly, the action state is encoded, with an additional `TRADE` field to indicate whether the action is a trade operation. The action state is used to assess the effect of a given action on the board.

The encode_state function use regular expressions scans all the rows, columns and diagonals of the board and counts the number of occurrences of each pattern.

The Q-table uses the combination of (board state, action state) as the key to store the corresponding Q-value, thereby supporting the learning and updating of the agent's policy.


#### 3 Q-table Update Mechanism

The `check_actions function` takes the current state and a list of available actions as input.

When called during the SARSA select action phase, it returns the action with the highest score from the list.  It also updates global variables such as prev_state, prev_action_state, and prev_reward in preparation for the next Q-table update.

For each action, the algorithm keeps track of:
```
current_action_reward: the immediate reward obtained by executing the action.
q_value:  the Q-value associated with the action.

best_current_action_reward: the highest reward among all actions considered
best_current_action_Q_value: the highest Q-value among all actions considered
```

The agent evaluates each action as follows:
```
action score = current action reward + draw card(next action reward) * draw weight
final score = 0.4 * action score + 0.6 * q_value
```

During the update phase, `check_actions` provides the best Q-value for the next state. If an action does not alter any patterns on the board (i.e. if all state features remain zero), the Q-table omits this entry in order to conserve memory.

The Q-learning Bellman equation is:

$$
Q(s, a) \leftarrow Q(s, a) + \alpha \left[ \text{reward} + \gamma \cdot \max_{a'} Q(s', a') - Q(s, a) \right]
$$

Since the opponent always moves after our agent, we cannot observe $Q(s, a)$ immediately. Instead, the agent updates the Q-value for the previous action at the start of its next turn.

In practice, the update proceeds as follows:

```
update Q(s,a) value:
    old_q = self.get_q_value(prev_state_encoding, prev_action_state)
    next_q(best action) = self.check_actions(next_actions, current_state)
    delta = prev_reward + self.gamma * next_q - old_q
    self.update_q_value(prev_state_encoding, prev_action_state, old_q + self.alpha * delta)

select_action()
```


[Back to top](#table-of-contents)

### Solved Challenges

In the preliminary submission, I successfully implemented the reward function. The remaining major challenge was to complete the full Q-learning (SARSA) framework. The main challenges addressed include:

1. State definition and feature selection:
Considerable effort went into designing feature engineering for the state representation. After exploring various approaches, I decided to use an eleven-dimensional vector to abstract the board state, while omitting the discard pile for simplicity and efficiency.

2. Incorporating opponent blocking into the reward scheme:
The original reward function only considered the agent’s own patterns. I extended this by introducing logic to reward actions that effectively block the opponent, thus making the agent’s policy more robust.

3. Debugging and refining Q-learning (SARSA):
Implementing and tuning Q-learning presented significant technical challenges. For instance, I discovered that many actions with no impact were cluttering the Q-table; I addressed this by omitting any action where all features remain zero. Additionally, I identified a flaw in the reward calculation. Previously, the reward combined the current action effect and the quality of the drawn card. This could mislead the Q-value if the action itself had little impact, but the reward for drawing the card was high. I therefore revised the reward function.

[Back to top](#table-of-contents)


### Trade-offs

#### *Advantages*  

1. State space compression improves generalisation and learning efficiency: 
Feature engineering compresses the vast original board state (10x10, 3^96) into an eleven-dimensional feature vector. This abstraction greatly reduces the number of states, making the Q-table trainable and memory-efficient. It also enhances the model’s ability to generalise across different situations.

2. Action space optimisation reduces pointless exploration:
This method applies feature extraction and filtering not only to the state but also to actions, keeping only those actions that are important or have significant impact. It does not record actions that have no effect on the outcome.

3. Reward function design is practical:
The reward function combines the agent’s own pattern scores with the ability to block key patterns for the opponent. 

4. Compared to greedy or one-step lookahead methods:
Greedy algorithms focus only on immediate gain and do not consider future possibilities. In contrast, Q-learning uses a discount factor (gamma) to consider long-term rewards, and thus tends to produce more globally optimal strategies.

#### *Disadvantages*

1. State abstraction loses local information:
When a complex board is simplified into statistical features, specific positional details are inevitably lost. For example, a “LIVE THREE” in different areas might have very different strategic significance, but the feature vector cannot distinguish this. The abstraction also omits information about draft card probabilities and does not model the opponent’s possible strategies.

2. Heuristic reward shaping depends on feature accuracy:
The effectiveness of the reward function depends on how well the chosen features correlate with achieving victory. If the features are not well designed, the AI may pursue superficial scores and neglect long-term objectives.

3. It struggles to capture extremely sparse or very long-term effects:
Compared to Monte Carlo methods, feature-based Q-learning relies more on local rewards. It finds it difficult to learn from highly sparse or purely global strategies.

[Back to top](#table-of-contents)

### Future improvements  

1. Enrich state space information:
In the future, the state representation could incorporate additional information such as the discard pile and the opponent’s hand, enabling the AI to make more informed decisions.

2. Implement online Q-learning:
Consider implementing online Q-learning to allow the agent to learn and update the Q-table in real time during matches rather than relying solely on offline training.

3. Visualise learning progress and convergence:
The programme could be optimised to include visualisation tools that displaying the training process and convergence curve. This makes it easier to monitor learning progress and to analyse the model’s performance in a more intuitive way.

[Back to top](#table-of-contents)
