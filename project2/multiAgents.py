# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
import sys

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (newFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    newFood = successorGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    
    "*** YOUR CODE HERE ***"
    food = 0
    if newPos in newFood.asList():
        food = 0.1
    else:
        food = sys.maxint
        for foodPoint in newFood.asList():
            food = min(food, util.manhattanDistance(foodPoint, newPos))
    
    penalty = 0
    minDis = sys.maxint
    for i in range(1, currentGameState.getNumAgents()):
        if (newScaredTimes[i - 1] > 1):
            continue
        minDis = min(minDis, util.manhattanDistance(newPos, successorGameState.getGhostPosition(i)))
    if minDis == 0:
        penalty = -999
    elif minDis != sys.maxint:
        penalty = -1 / minDis     
    
    return  successorGameState.getScore() + 1.0 / food + penalty  

def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
        Your minimax agent (question 2)
    """
    def getAction(self, gameState):
        """
            Returns the minimax action from the current gameState using self.depth
            and self.evaluationFunction.
            
            Here are some method calls that might be useful when implementing minimax.
            
            gameState.getLegalActions(agentIndex):
              Returns a list of legal actions for an agent
              agentIndex=0 means Pacman, ghosts are >= 1
            
            Directions.STOP:
              The stop direction, which is always legal
            
            gameState.generateSuccessor(agentIndex, action):
              Returns the successor game state after an agent takes an action
            
            gameState.getNumAgents():
              Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        
        decision = self.value(gameState, 0, 1)
        return decision[1]
     
    
    def value(self, curState, curDepth, ghostIndex):
        if curState.getNumAgents() == 1 and curDepth % 2 == 1:
            curDepth += 1
        elif ghostIndex == curState.getNumAgents():
            ghostIndex = 1
            curDepth += 1
        if curDepth == self.depth * 2 or curState.isWin() or curState.isLose():
            return (self.evaluationFunction(curState), Directions.STOP)
        elif curDepth % 2 == 0:
            return self.maxValue(curState, curDepth)
        else:
#             minV = (sys.maxint + 0.0, Directions.STOP)
#             for i in range(1, curState.getNumAgents()):
#                 curV = self.minValue(curState, curDepth, i)
#                 if (curV < minV):
#                     minV = curV
#             return minV
            return self.minValue(curState, curDepth, ghostIndex)
      
    def maxValue(self, curState, curDepth):
        actions = curState.getLegalActions(0)
        maxV = (-sys.maxint - 1.0, Directions.STOP)
        for action in actions:
            neighbor = curState.generateSuccessor(0, action)
            curV = self.value(neighbor, curDepth + 1, 1)
            if (curV[0] > maxV[0]):
                maxV = (curV[0], action)
           
        return maxV;
    def minValue(self, curState, curDepth, agentIndex):
        actions = curState.getLegalActions(agentIndex)
        minV = (sys.maxint, Directions.STOP)
        for action in actions:
            neighbor = curState.generateSuccessor(agentIndex, action)
            curV = self.value(neighbor, curDepth, agentIndex + 1)
            if (curV[0] < minV[0]):
                minV = (curV[0], action)
        return minV

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
            Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        decision = self.value(gameState, 0, 1, -sys.maxint, sys.maxint)
        return decision[1]
         
    def value(self, curState, curDepth, ghostIndex, tmpMax, tmpMin):
        if curState.getNumAgents() == 1 and curDepth % 2 == 1:
            curDepth += 1
        elif ghostIndex == curState.getNumAgents():
            ghostIndex = 1
            curDepth += 1
         
        if curDepth == self.depth * 2 or curState.isWin() or curState.isLose():
            return (self.evaluationFunction(curState), Directions.STOP)
        elif curDepth % 2 == 0:
            return self.maxValue(curState, curDepth, tmpMax, tmpMin)
        else:
            return self.minValue(curState, curDepth, ghostIndex, tmpMax, tmpMin)
      
    def maxValue(self, curState, curDepth, tmpMax, tmpMin):
        actions = curState.getLegalActions(0)
        maxV = (-sys.maxint - 1.0, Directions.STOP)
        for action in actions:
            neighbor = curState.generateSuccessor(0, action)
            curV = self.value(neighbor, curDepth + 1, 1, tmpMax, tmpMin)
            if (curV[0] > maxV[0]):
                maxV = (curV[0], action)
            if maxV[0] >= tmpMin:
                return maxV
            tmpMax = max(tmpMax, maxV[0])
        return maxV;
    
    def minValue(self, curState, curDepth, agentIndex, tmpMax, tmpMin):
        actions = curState.getLegalActions(agentIndex)
        minV = (sys.maxint, Directions.STOP)
        for action in actions:
            neighbor = curState.generateSuccessor(agentIndex, action)
            curV = self.value(neighbor, curDepth, agentIndex + 1, tmpMax, tmpMin)
            if curV[0] < minV[0]:
                minV = (curV[0], action)
            if minV[0] <= tmpMax:
                return minV
            tmpMin = min(tmpMin, minV[0])
        return minV
class ExpectimaxAgent(MultiAgentSearchAgent):
    """
        Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction
    
          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        decision = self.value(gameState, 0, 1)
        return decision[1]
     
    
    def value(self, curState, curDepth, ghostIndex):
        if curState.getNumAgents() == 1 and curDepth % 2 == 1:
            curDepth += 1
        elif ghostIndex == curState.getNumAgents():
            ghostIndex = 1
            curDepth += 1
        if curDepth == self.depth * 2 or curState.isWin() or curState.isLose():
            return (self.evaluationFunction(curState), Directions.STOP)
        elif curDepth % 2 == 0:
            return self.maxValue(curState, curDepth)
        else:
            return self.expValue(curState, curDepth, ghostIndex)
      
    def maxValue(self, curState, curDepth):
        actions = curState.getLegalActions(0)
        maxV = (-sys.maxint - 1.0, Directions.STOP)
        for action in actions:
            neighbor = curState.generateSuccessor(0, action)
            curV = self.value(neighbor, curDepth + 1, 1)
            if (curV[0] > maxV[0]):
                maxV = (curV[0], action)
           
        return maxV;
    def expValue(self, curState, curDepth, agentIndex):
        actions = curState.getLegalActions(agentIndex)
        sumV = 0
        for action in actions:
            neighbor = curState.generateSuccessor(agentIndex, action)
            curV = self.value(neighbor, curDepth, agentIndex + 1)
            sumV += curV[0]
        return (sumV / len(actions), None)

def betterEvaluationFunction(currentGameState):
    """
        Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
        evaluation function (question 5).
    
        DESCRIPTION: <write something here so we know what you did>
        We are considering three aspects in this problem.
        1. The distance to the closest pellet
        2. The distance to the closest ghost
        3. The distance to the closest power-pellet
        
        The pacman will get more bonus when it is close to (power)pellets, and will get penalty if it is close
        to ghosts. Scared ghosts are not taken into consideration. There are weights for these three aspects,
        and we are trying to modify the weights as the game continues. For example, when the pacman is very close to
        ghosts, we add the weight of penalty to make the pacman more "scared" on ghosts to avoid being caught by
        ghosts, and we add the weight of power-pellet to give pacman the motivation to eat the power-pellet and fight
        back.
      """
    "*** YOUR CODE HERE ***"  
    PacmanPos = currentGameState.getPacmanPosition()
    FoodList = currentGameState.getFood().asList()
    GhostStates = currentGameState.getGhostStates()
    ScaredTimes = [ghostState.scaredTimer for ghostState in GhostStates]
    
    foodWeight = 1.0
    if (currentGameState.getNumFood() < 5):
        foodWeight = 10.0
    PowerWeight = 10.0
    food = 0
    if PacmanPos in FoodList:
        food = 0.1
    else:
        food = sys.maxint
        for foodPoint in FoodList:
            food = min(food, util.manhattanDistance(foodPoint, PacmanPos))
    
    penalty = 0
    minDis = sys.maxint
    for i in range(1, currentGameState.getNumAgents()):
        if (ScaredTimes[i - 1] > 1):
            continue
        minDis = min(minDis, util.manhattanDistance(PacmanPos, currentGameState.getGhostPosition(i)))
    if minDis == 0:
        penalty = -999
    elif minDis > 4:
        foodWeight = foodWeight + 10.0
    elif minDis < 4:
        penalty = -4 / minDis
        PowerWeight = 100.0
    elif minDis != sys.maxint:
        penalty = -1 / minDis     
    
    PowerDots = currentGameState.getCapsules()
    PowerDist = sys.maxint
    Power = 0
    for dot in PowerDots:
        PowerDist = min(PowerDist, util.manhattanDistance(PacmanPos, dot))
    if (PowerDist != sys.maxint):
        Power = PowerWeight / PowerDist

    return  currentGameState.getScore() + foodWeight / food + penalty + Power 
# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

