# AI Method 1 - Computational Approach

Your notes about this part of the project, including acknowledgement, comments, strengths and limitations, etc.

You **do not** need to explain the algorithm. Please tell us how you used it and how you applied it in your team.

If you use greed best first search, then, you can explain about what is the problem (state space model, especially how you define the state, how your define the goal), and heuristic function (as specific as possible) that you used. 

If you use MCTS, then, you can explain about what tree policy/simulation policy you used, how many iteration did you run, what is your reward function, the depth of each simulation etc.

# Table of Contents
  * [Motivation](#motivation)
  * [Application](#application)
  * [Solved challenges](#solved-challenges)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)
 
### Motivation  

When designing my agent, I initially considered using a breadth-first search (BFS) strategy to explore the action space. My idea was to simulate not only immediate actions but also look one step ahead by evaluating draft card selection — essentially implementing a shallow two-layer lookahead. In conceptual extensions, I even experimented with deeper levels (e.g., three steps), but these proved impractical due to time constraints.

However, I quickly realized the importance of balancing decision quality with computational efficiency. To ensure my agent remained responsive and avoided timeouts in the simulation environment, I adopted a greedy approach guided by a lightweight heuristic function. This allowed the agent to make consistent and stable decisions based on local state features, while remaining fast enough for real-time gameplay.

[Back to top](#table-of-contents)

### Application  

In my implementation, all candidate actions are scored using a combination of a heatmap (POS_WEIGHT) and directional counting logic inspired by Gomoku (five-in-a-row). For each possible move, I examine up to four directions (vertical, horizontal, and two diagonals) and calculate a score based on the number of aligned pieces (from 2 to 5), with increasing weights for longer sequences. If an action achieves a higher score than the current best, it replaces the previous best_action.

Special cards, namely the two-eyed Jacks (jh and jd), are integrated with a usage cost mechanism to discourage premature or wasteful use — particularly when the board state does not justify a removal action (e.g., when the opponent only has a weak formation). A flat bonus of +1000 is assigned to each Jack card in the draft phase to represent their strategic potential.

For draft card selection, my agent traverses the 5 draft options available each round, using the POS_WEIGHT heatmap to prioritize cards that help build formations in the center of the board. This heatmap is tuned to favor central positions, especially early in the game or when forming initial two-piece combos. Inspired by Gomoku theory, this helps the agent establish strong opening control.

All logic is implemented inside the SelectAction loop directly. This avoids extra function calls and keeps complexity low, ensuring fast execution under tight time constraints.

[Back to top](#table-of-contents)

### Solved Challenges

Avoiding Timeout:

To ensure that the agent operates within the simulation's strict time constraints, all scoring logic is fully inlined inside the SelectAction method, avoiding any additional function calls. A time threshold of 0.98 seconds is enforced—once exceeded, the loop exits immediately, returning the best action found so far. After over 30 iterations of model refinement, the agent is now lightweight and stable, but this safeguard still protects against unexpected stalls or heavy board states.

Controlled Use of Double-Eyed Jacks (jh/jd):

The agent implements a score-based penalty mechanism to discourage premature or low-impact use of the powerful double-eyed Jack cards (jh and jd). Specifically, unless the evaluated score of the action surpasses a threshold (e.g., 8000), the agent avoids playing these cards. Earlier strategies that reserved these cards for theoretical "perfect combos" often resulted in them being held indefinitely, even when proactive use could offer better tempo or control. Through detailed animation reviews and empirical matches, I found that Sequence strongly rewards early board presence and central control, outweighing the benefits of excessive Jack preservation.

Preventing Misuse of Remove Actions:

To avoid random or low-impact removals using jh or jd, a base penalty (-100 or more) is applied unless the action directly counters a significant threat from the opponent, such as a four-in-a-row. This makes sure that “remove” actions are only considered when blocking a critical line, aligning with the idea that high-impact tools should be used only at high-impact moments. Experimental results showed that this approach yields better board positioning and reduces unnecessary defensive play.

Lightweight Draft Evaluation:

Initial versions of the agent considered multi-step draft lookahead (up to 2 steps), but the gains were marginal while the computational cost was significant. The final design instead uses a static center-weighted heatmap (POS_WEIGHT) to evaluate draft choices. Draft cards that align with stronger central positions receive higher scores. All Jack cards are given a fixed draft score bonus of 1000 to reflect their general utility and priority in acquisition. This simplified evaluation balances efficiency and strategic drafting without complicating the search process.

[Back to top](#table-of-contents)


### Trade-offs  
#### *Advantages*  

Stable and Fast: The agent consistently avoids runtime crashes or timeouts. Its lightweight implementation ensures timely responses under strict time constraints.

Strategically Aggressive: With a clear early-to-mid-game layout distinction, the agent demonstrates strong offensive tendencies—prioritizing quick sequence formation and focusing removal only on critical threats.

Readable and Modular Code: The logic is centralized and streamlined in SelectAction, making the agent easy to debug, fine-tune, and extend for reward-driven optimization in future iterations.

#### *Disadvantages*

Lack of Multi-step Planning: The agent does not simulate long-term consequences beyond the current move, which may lead to passive positions in prolonged games.

No Pattern Recognition: It cannot identify composite threats (e.g., two separate three-in-a-rows converging into a five-in-a-row), missing tactical explosion points.

Overemphasis on Offense: The scoring strongly favors aggressive plays, often at the expense of defense or positional restraint.

Draft Limitation in Edge Scenarios: The draft evaluation performs well during center-dominant openings, but struggles when the initial hand forces edge-based development—continuing to favor central positions regardless of actual layout.

[Back to top](#table-of-contents)

### Future improvements  

Although a multi-step draft optimization model was not successfully implemented, the current SelectAction logic transitions well from center control to line-completion strategy. However, in games where the initial hand fails to establish central dominance, the agent's draft choices continue to gravitate toward the center, ignoring the evolving spatial context. This leads to wasted draft opportunities when the active formation has shifted to edge regions.

A promising improvement would be to dynamically generate a heatmap from current placements—based on all of the agent’s chips on the board—and then use this adaptive matrix to guide draft card selection. With training, such a weight distribution model could learn to reinforce the ongoing strategy, better aligning draft choices with the agent’s actual board state rather than a static heuristic.

[Back to top](#table-of-contents)