# Analysis of the problem

### Analysis of the problem


State Space Description:

1. Current Legal Actions Example: [{'play_card': '2s', 'draft_card': 'jd', 'type': 'place', 'coords': (0, 1)}, {'play_card': '2s', 'draft_card': '5s', 'type': 'place', 'coords': (0, 1)}, ]
2. Positions can be ('_', 'red', 'blue', '# (joker)') on a 10*10 Board: game_state.board.chips
3. Agent Information: Agent's ID, colour (red/blue), and current score (number of sequences formed): game_state.agents[self.id].colour/score
4. Agent's Current Hand: game_state.agents[self.id].colour: player hand: e.g. ['2s', '2c', '4c', 'ad', 'ts', '5c']
5. Draft Area (5 cards available to both agents): game_state.board.draft: ['jd', '5s', '5s', '6d', '7h']
6. Cards Currently in the Discard Area: game_state.deck.discards: {'discards': ['ts']}
7. Deck Status (not directly observable): game_state.deck.cards: The state of the deck and the next card drawn are unknown. However, the probability of drawing any specific card can be inferred by {all_cards} - {discards}.


Initial state:

1. Empty 10x10 board (all positions empty except the four corners marked as '#').
2. Each agent 6 card on hand, and score is 0.
3. Discard Area is initially empty (0 cards).

Goal state:

1. A Sequence is defined as 5 consecutive chips of the agent's colour, aligned in one of four directions: [(1, 0), (0, 1), (1, 1), (1, -1)]. The four corners marked as '#' can count as part of a sequence.
2. The first player to complete two sequences wins (the two sequences may overlap by at most one chip).

Action:

1. place(card, coords): 

    - Places a chip on an empty position on the board.

    - "Two-Eyed Jacks" can be placed on any empty position.

    - Played card goes to the Discard Area. The player then picks one card from the Draft Area, and a new card from the Deck goes in to the Draft Area randomly.

2. remove(card, coords): 

    - Only possible with "One-Eyed Jacks".

    - Removes a non-sequence chip from the board (sets position to empty '_').

    - Similar card management to Place action: played card goes to the Discard Area, selects a card from the Draft area, and Draft area replenishes randomly.

3. trade(card, draw_card): 

    - Discard one card from hand to the Discard Area.

    - Choose a card from the Draft Area.

    - Draft Area is randomly filled.


Transition function:

1. Deterministic (fully observable): 

    - Agent's action (place/remove) deterministically changes the board state.

    - Deterministic update to hand and Discard Area.

2. Non-deterministic: 

    - Draft Area is randomly filled.

    - Opponent's next action is unknown.

