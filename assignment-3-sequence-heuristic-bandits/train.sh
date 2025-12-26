#!/bin/bash
echo "fight random 1"
python general_game_runner.py -g Sequence -a agents.t_014.myTeam --agent_names=Q -q -m 10  
echo "fight astar 1"
python general_game_runner.py -g Sequence -a agents.t_014.A_star_3,agents.t_014.myTeam --agent_names=A_star,Q -n 2 -m 800 -q
echo "fight astar 1"
python general_game_runner.py -g Sequence -a agents.t_014.A_star_4,agents.t_014.myTeam --agent_names=A_star,Q -n 2 -m 800 -q
echo "fight astar 2"
python general_game_runner.py -g Sequence -a agents.t_014.A_star_6,agents.t_014.myTeam --agent_names=A_star,Q -n 2 -m 800 -q

python general_game_runner.py -g Sequence -a agents.t_014.benchmark3,agents.t_014.myTeam --agent_names=Bench3,Q -n 2 -m 100 -q
