# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from game import Grid
from searchProblems import nullHeuristic, PositionSearchProblem
from util import Queue


### You might need to use
from copy import deepcopy

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""      
    util.raiseNotDefined()


def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    myPQ = util.PriorityQueue()
    startState = problem.getStartState()
    startNode = (startState, 0, [])
    myPQ.push(startNode, heuristic(startState, problem))
    best_g = dict()
    while not myPQ.isEmpty():
        node = myPQ.pop()
        state, cost, path = node
        if (not state in best_g) or (cost < best_g[state]):
            best_g[state] = cost
            if problem.isGoalState(state):
                return path
            for succ in problem.getSuccessors(state):
                succState, succAction, succCost = succ
                new_cost = cost + succCost
                newNode = (succState, new_cost, path + [succAction])
                myPQ.push(newNode, heuristic(succState, problem) + new_cost)

    return None  # Goal not found



def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """

    util.raiseNotDefined()


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    util.raiseNotDefined()


def foodHeuristic(state, problem):
    """
    Your heuristic for the FoodSearchProblem goes here.

    This heuristic must be consistent to ensure correctness.  First, try to come
    up with an admissible heuristic; almost all admissible heuristics will be
    consistent as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible!  On the
    other hand, inadmissible or inconsistent heuristics may find optimal
    solutions, so be careful.

    The state is a tuple ( pacmanPosition, foodGrid ) where foodGrid is a Grid
    (see game.py) of either True or False. You can call foodGrid.asList() to get
    a list of food coordinates instead.

    If you want access to info like walls, capsules, etc., you can query the
    problem.  For example, problem.walls gives you a Grid of where the walls
    are.

    If you want to *store* information to be reused in other calls to the
    heuristic, there is a dictionary called problem.heuristicInfo that you can
    use. For example, if you only want to count the walls once and store that
    value, try: problem.heuristicInfo['wallCount'] = problem.walls.count()
    Subsequent calls to this heuristic can access
    problem.heuristicInfo['wallCount']
    """
    "*** YOUR CODE HERE for TASK1 ***"
    
    position, foodGrid = state
    foodList = foodGrid.asList()

    if not foodList:
        return 0

    walls = problem.walls

    # Step 1: BFS 计算从当前位置出发的所有距离（考虑墙）
    visited = set()
    queue = util.Queue()
    queue.push((position, 0))
    distanceMap = {}
    # currPos 是 当前正在被扩展的位置坐标
    while not queue.isEmpty():
        currPos, dist = queue.pop()
        if currPos in visited:
            continue
        visited.add(currPos)
        distanceMap[currPos] = dist

        x, y = currPos
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            next_pos = (x + dx, y + dy)
            if 0 <= next_pos[0] < walls.width and 0 <= next_pos[1] < walls.height:
                if not walls[next_pos[0]][next_pos[1]] and next_pos not in visited:
                    queue.push((next_pos, dist + 1))

    # Step 2: 从 BFS 得到的距离中选最大（即到最远的食物）
    maxDist = 0
    for food in foodList:
        if food in distanceMap:
            maxDist = max(maxDist, distanceMap[food])
        else:
            # 如果有食物无法到达，返回无穷大（防止误导搜索）
            return float('inf')

    return maxDist
    
    
    
    
 
def lrtaStarInitial(problem, heuristic=nullHeuristic):
    return lrtaStarTrial(problem, LearningHeuristic(heuristic, problem))

def lrtakStarInitial(problem, heuristic=nullHeuristic):
    return lrtakStarTrial(problem, LearningHeuristic(heuristic, problem), k=9)

class LearningHeuristic:
    """
    This class is designed to help simplify the implementation of LTRA* 
    and LRTA*k algorithms. It allows a single transparent interface to 
    the heuristic function and the updated heuristic cache, without 
    having to initialise the cache for all possible states at the start 
    of the algorithm.

    It also allows easy checking of whether the cache has been updated
    since the last search iteration, so that the search can be stopped
    when the heuristic values have converged.

    This class is not necessary for the implementation of the algorithms,
    but it is recommended to use it to simplify the code.
    """
    def __init__(self,heuristic, problem):
        self.heuristic = heuristic
        self.problem = problem
        self.heuristicCache = {}
        self.updated = False
    
    def getHeuristic(self,state):
        if not state in self.heuristicCache:
            self.heuristicCache[state] = self.heuristic(state, self.problem)
        return self.heuristicCache[state]
    
    def setHeuristic(self,state,h):
        self.heuristicCache[state] = h
        self.updated = True

    def clearUpdates(self):
        self.updated = False

    def wasUpdated(self):
        return self.updated

def lrtaStarSearch(problem, heuristic=nullHeuristic):
    learningHeuristic = LearningHeuristic(heuristic, problem)
    "*** YOUR CODE HERE for TASK2 ***"

    # 不断重复 trial，直到 heuristic 没有更新
    while True:
        learningHeuristic.clearUpdates()  # 清空“是否更新”标记
        path = lrtaStarTrial(problem, learningHeuristic)  # 一次搜索
        if not learningHeuristic.wasUpdated():
            break  # 没有任何启发式被更新，搜索结束
    return path  
    
    

def lrtaStarTrial(problem, learningHeuristic):
    "*** YOUR CODE HERE for TASK2 ***"

    """
    Runs one trial of LRTA*, starting from the initial state,
    walking toward the goal while updating heuristic values.
    Returns the path taken in this trial.
    """
    
    # 获取初始状态
    current_state = problem.getStartState()
    # 记录走过的动作
    path = []

    if not hasattr(problem, "_expanded"):
        problem._expanded = []

    while not problem.isGoalState(current_state):
        # 唯一一次调用 getSuccessors()
        successors = problem.getSuccessors(current_state)

        # Step 1: 启发式更新（用已获取的 successors）
        lookaheadUpdate1(problem, current_state, learningHeuristic, successors)

        # Step 2: 选择最优 successor
        best_cost = float('inf')
        best_action = None
        best_successor = None

        for succ_state, action, step_cost in successors:
            h_succ = learningHeuristic.getHeuristic(succ_state)
            total_cost = step_cost + h_succ
            if total_cost < best_cost:
                best_cost = total_cost
                best_action = action
                best_successor = succ_state

        if best_successor is None:
            return []

    
        # Step 3: 实际移动
        path.append(best_action)
        
        
        # 处理int问题：
        if not hasattr(problem, "_expanded_states"):
            problem._expanded_states = []
        problem._expanded_states.append(best_successor)

        
        
        current_state = best_successor

    return path





def lookaheadUpdate1(problem, state, learningHeuristic, successors):
    if problem.isGoalState(state):
        return False

    best_cost = float('inf')

    for succState, _, stepCost in successors:
        h_succ = learningHeuristic.getHeuristic(succState)
        total_cost = stepCost + h_succ
        if total_cost < best_cost:
            best_cost = total_cost

    h_current = learningHeuristic.getHeuristic(state)

    if h_current < best_cost:
        learningHeuristic.setHeuristic(state, best_cost)
        return True
    else:
        return False
   








   
   
   
    
# Q3    

def lrtakStarSearch(problem, heuristic=nullHeuristic, k=9):
    learningHeuristic = LearningHeuristic(heuristic, problem)
    "*** YOUR CODE HERE for TASK3 ***"
    while True:
        path = lrtakStarTrial(problem, learningHeuristic, k)
        if not learningHeuristic.wasUpdated():
            return path
        learningHeuristic.clearUpdates()

def lrtakStarTrial(problem, learningHeuristic, k):
    "*** YOUR CODE HERE for TASK3 ***"
    current_state = problem.getStartState()
    path = []
    trial_visited = [current_state]

    # 用于 autograder 扩展状态记录
    while not problem.isGoalState(current_state):
        min_cost = float('inf')
        best_successor = None
        best_action = None

        # 附加的 k 轮 lookahead update
        successors = lookaheadUpdateK(problem, current_state, learningHeuristic, k, trial_visited)
        for succ_state, action, step_cost in successors:
            h = learningHeuristic.getHeuristic(succ_state)
            cost = step_cost + h
            if cost < min_cost:
                min_cost = cost
                best_successor = succ_state
                best_action = action

        path.append(best_action)
        
        # 记录最终解的扩展不在这里记录，而由 lookaheadUpdateK 记录扩展
        # 但我们仍更新 trial_visited：因为这个节点已经被实际选中
        trial_visited.append(best_successor)
        current_state = best_successor

    return path

def lookaheadUpdateK(problem, state, learningHeuristic, k, trial_visited):
    queue = [state]
    cont = k - 1
    first = True
    output_successors = []

    while queue:
        v = queue.pop(0)
        successors = problem.getSuccessors(v)

        update_flag = lookaheadUpdate3(v, problem, learningHeuristic, k=True, successors=successors)

        if first:
            output_successors = successors
            first = False

        if update_flag:
            for succ_state, _, _ in successors:
                if cont > 0 and succ_state in trial_visited: # 只加入曾经在 path 中出现的节点
                    queue.append(succ_state)
                    #不再更新 trial_visited这里，因为 w 已经在 trial_visited 中
                    cont -= 1

    return output_successors


def lookaheadUpdate3(state, problem, learningHeuristic, k=False, successors=None):
    if not successors:
        successors = problem.getSuccessors(state)
    min_cost = float('inf')
    update_flag = False
    for succ_state, _, step_cost in successors:
        cost = step_cost + learningHeuristic.getHeuristic(succ_state)
        if cost < min_cost:
            min_cost = cost
    if learningHeuristic.getHeuristic(state) < min_cost:
        learningHeuristic.setHeuristic(state, min_cost)
        learningHeuristic.updated = True
        update_flag = True
    if not k:
        return successors
    else:
        return update_flag



























# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
lrta = lrtaStarSearch
lrtak = lrtakStarSearch
lrtaTrial = lrtaStarInitial
lrtakTrial = lrtakStarInitial
