# AI Method 3 - MiniMax

# Table of Contents
  * [Motivation](#motivation)
  * [Application](#application)
  * [Solved challenges](#solved-challenges)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)
 
### Motivation 

We implemented the game-theoretic MiniMax algorithm because it evaluates every action against the opponent’s best possible replies, giving the agent deeper, more strategic insight into the board position.

We adopted a depth-2, reward-driven Minimax algorithm for the Sequence Game, using the POS_WEIGHT heatmap originally developed by Taoyuan Liu.
For every legal move (placing or removing a chip) the algorithm:
- 1. Base reward – adds the lookup-table reward for new friendly links made and enemy links broken.
- 2. Opponent reply – simulates every observed opponent move, takes the highest resulting reward, discounts it by factor 0.9 fator, and subtracts that value.
- 3. Draft card – adds the draft card’s score with a preference on two-eye jacks then one-eye jacks, discounted by factor 0.8.

Our Sequence agent had to make a legally valid move within 1s while still looking “one move ahead” and counter-planning around the opponent’s best reply. A full Minimax search is impossible—the branching factor explodes. Therefore we designed a single play Max step + single play Min step with strong score scheme and heavy memorization.  

[Back to top](#table-of-contents)

### Application  

Mini-Max normally benefits from insight into the opponent’s hidden hand—information we never truly have. What we do see, however, is the card they just played and the draft card they selected. Those clues let us narrow down which cards remain available to them when we project future turns. As we keep tracking these observations over time, our estimate of their likely moves—and even the contents of their hand—gradually improves.

Even when we have full knowledge of the cards in opponent's hand, due to the time limit it is not possible to construct a complete game tree, instead we only look one step ahead.

Rewards are calculated per placement or removal, so we inspect only the four lines—horizontal, vertical, main diagonal, and anti-diagonal—that pass through the target square. To avoid repeated searches, each of these lines is cached using a serialized NumPy representation of the board.


[Back to top](#table-of-contents)

### Solved Challenges

- Time budget – constant-time evaluation per action with cached information used,  we never timed out.
- Opponent modelling – Before deciding on a action, we retrieve the opponent’s last action and update our catalogue of their remaining possible plays. After selecting our own action, we refresh that catalogue once more to account for the new board state.
- Redundant recomputation - The board is kept as an up-to-date NumPy array for fast indexing. Whenever we examine a line (row, column, diagonal, anti-diagonal), we encode it into a byte string and cache it. If the agent later needs the same line at same coordinate, it can retrieve the result in O(1) time instead of scanning the board again.

[Back to top](#table-of-contents)


### Trade-offs  
#### *Advantages*  

- Fast - The agent complete the 1 step look-ahead evaluation within 1s
- More throughout consideration - By forecasting the opponent’s possible actions, we steer clear of actions that could give the opponent an advantage. If the evaluation predicts that a particular action could let the opponent win, that move is deliberately scored much lower, so the algorithm favors alternative moves—even those whose own immediate reward is modest.

#### *Disadvantages*

- Shallow look-ahead – Because the agent only simulates one of its own moves followed by the opponent’s immediate reply, it simply cannot see two-step or “sacrifice-then-win” tactics. For example, trading a chip now to create an uncovered four-in-a-row threat on the next turn is invisible to depth-2 search. Deeper or selective search would be required to capture such combos.

No learning – All parameters (kernel peak, decay factors, reward buckets) are hard-coded. The agent never refines them from self-play or tournament logs, so it cannot adapt if opponents discover and exploit its predictable biases (e.g., persistent centre openings). Any improvement requires manual retuning and redeployment.

[Back to top](#table-of-contents)

### Future improvements  

- Deeper but selective search: (Either approach below would let us spend our limited time budget on the most promising lines instead of exploring every legal move indiscriminately.)
    - Alpha-beta pruning: Expand the full game tree while cutting off branches that are already provably worse than alternatives, keeping computation under control.
    - Top-k expansion: Alternatively, extend only the best k candidate moves at each ply (e.g., k = 3). This beam-search style keeps branching in check while still catching critical tactical sequences.

- Numpy Vectorization/Multi-Threading: The current search_count routine examines four directions one after the other for each candidate action, but those checks are completely independent and trivial to parallelize. We can speed this up by vectorizing all directional scans in one batch with NumPy, or by distributing them across threads


[Back to top](#table-of-contents)