## Conclusions and Learnings


Although both methods are based on the principle of goal-aware heuristics, they differ fundamentally in their computational approach and state representation.

The Computational Approach is essentially a highly refined greedy algorithm. It focuses exclusively on the immediate best move, explicitly calculating the potential score for each possible place or remove action based on the current board state. This method leverages handcrafted heuristics, including a carefully designed heatmap to prioritise central positions in the early game, explicit strategies for wild cards, and dynamic adjustments based on whether the agent plays first or second.It not only recognises situations involving wild cards, but also penalises their use when the anticipated reward is low. This approach effectively exploits all possible information for the next action, embodying the philosophy of 'greedy optimisation taken to the limit'. All evaluation is local and manually crafted to maximise short-term gain.

In contrast, the SARSA method incorporates a learning-based, two-step optimality. Rather than evaluating the immediate score, SARSA uses a combination of the Q-value and the current action reward to select actions. The Q-table is automatically updated as training proceeds, relying on the observed reward from the current action and the estimated value of the future state. The state and action space are represented in a compressed eleven-dimensional feature vector, greatly reducing memory overhead but also sacrificing some specific board context. Unlike the hand-designed approach, SARSA learns its own strategies through self-play, without explicit domain-specific rules for wild cards or positional priorities. This distinction clearly separates hand-designed and data-driven approaches.

### Outcome Comparison

Despite SARSA's potential for long-term optimisation,  experimental results indicate that the handcrafted Computational Approach consistently outperforms the SARSA agent, both on the server and in benchmark evaluations. This superior performance is likely due to two main reasons: Firstly, the feature-based abstraction in SARSA omits critical details about specific board positions and patterns, thereby weakening its decision-making in nuanced situations; Secondly, SARSA’s training is limited by the absence of a robust teacher model, leading to suboptimal policy learning and reduced ability to generalise when facing challenging opponents.



| Feature                   | Computational Approach (Greedy)       | SARSA (Q-learning)                      |
|---------------------------|---------------------------------------|-----------------------------------------|
| Decision scope            | Next-move only, local optimum         | Considers next two moves, learns policy |
| Strategy source           | Handcrafted, rule-based               | Data-driven, self-learned               |
| Wild card usage           | Special rules and penalties           | No explicit handling                    |
| Board representation      | Full/explicit, heatmap for early game | Compressed features (loses position)    |
| Memory usage              | Low                                   | High                                    |
| Performance vs. Benchmark | Stronger on both server and benchmark | Weaker, limited by abstraction          |