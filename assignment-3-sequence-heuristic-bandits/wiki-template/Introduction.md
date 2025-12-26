# Home and Introduction

This project implements three distinct AI strategies to compete in the Sequence game, each designed to balance efficiency, adaptability, and tactical depth. The game of Sequence is inherently complex due to its mix of randomness (via card draws) and spatial strategy (board control and blocking). We explored different approaches to tackle these challenges from both theoretical and practical angles.

### Method 1: Greedy Heuristic Agent

This lightweight agent uses a greedy best-first approach guided by a custom heuristic function. It scores each move based on a combination of a positional heatmap and direction-based link counting (inspired by Gomoku). This model emphasizes speed, stability, and strong opening control through center dominance. It also includes intelligent draft evaluation and Jack card usage policies, achieving highly consistent results in tournament simulations.

### Method 2: SARSA Reinforcement Learning

We trained a reinforcement learning agent using the SARSA algorithm. The model learns from interaction with the environment by updating Q-values for state-action pairs, using an epsilon-greedy policy. Though slower to converge and dependent on careful reward shaping, it adapts well to long-term strategies and generalizes across various board states.

### Method 3: Minimax with Depth-2 Evaluation

This agent evaluates each move by simulating the opponent’s best reply (depth-2 lookahead). It calculates scores based on friendly chain formation, opponent counterplay, and draft potential. Despite time limitations, the agent manages to simulate one step of opponent response and adjusts its strategy accordingly. This provides better long-term planning compared to greedy models, though at the cost of increased computation.

Together, these three methods demonstrate a spectrum of strategy: from fast heuristics to learning-based adaptation and limited-depth foresight. We compare them in head-to-head matchups and analyze performance across key scenarios.