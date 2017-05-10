'''
Created on Dec 16, 2016

@author: xiaozhang
'''
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint


def createTeam(firstIndex, secondIndex, isRed,
               first = 'myAgent', second = 'myAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


class myAgent(CaptureAgent):
    isPowerful = False
    powerfulTime = 0.0
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.mods = util.Counter()
        for enemy in self.getOpponents(gameState):
            self.mods[enemy] = PacmanInference(enemy, self.index, gameState)
        #self.isPowerful = False
        #self.powerfulTime = 0.0
    
    def getWeights(self, gameState, action):    
        return {'food': 100, 'capsule': 100, 'opponent': -50, 'caught': -99999, 'Power': 2000, 'score': 1000, 'coop': -5, 'stop': -50 , 'corner': -10}
    
    def getFeatures(self, gameState, action):
        features = util.Counter()
        myPos = gameState.getAgentPosition(self.index)
        
        foodList = self.getFood(gameState).asList()
        minFoodDist = min(self.getMazeDistance(myPos,p) for p in foodList)
        features['food'] = 1.0 / minFoodDist
        
        capsuleList = self.getCapsules(gameState)
        if len(capsuleList) == 0: 
            features['capsule'] = 100
        else:
            minCapDist = min(self.getMazeDistance(myPos, p) for p in capsuleList)
            features['capsule'] = 1.0 / (minCapDist + 1)
            
        
        oppPositions = [self.mods[enemyIndex].getMostLikelyPosition() for enemyIndex in self.mods]
        minOppoDist = min(self.getMazeDistance(myPos, oppPosition) for oppPosition in oppPositions)
        minOppoPos = oppPositions[0]
        for oppPos in oppPositions:
            if self.getMazeDistance(myPos, oppPos) == minOppoDist:
                minOppoPos = oppPos
                break    
        if myAgent.isPowerful and self.statusCheck(gameState) != -1:
            features['opponent'] = 0
        else:
            features['opponent'] = (-6 if self.checkArea(gameState, minOppoPos)== -1 else 1) * 1.0 / (minOppoDist + 1) # if minOppoDist is 0
        
        if minOppoDist == 0:
            if self.statusCheck(gameState) == -1:
                features['caught'] = -1
            else:
                features['caught'] = 0 if myAgent.isPowerful else 1
        else:
            features['caught'] = 0
        
        features['Power'] = 1.0 if myAgent.isPowerful else 0
        features['score'] = (1.0 if self.red else -1.0) * gameState.getScore()
        
        friendPos = gameState.getAgentPosition([index for index in self.getTeam(gameState) if index != self.index][0])
        friendDis = self.getMazeDistance(myPos, friendPos)
        features['coop'] = (0 if self.statusCheck(gameState) == -1 else 1) / (friendDis + 1)
        
        features['stop'] = 1 if action == Directions.STOP else 0
        if len(gameState.getLegalActions(self.index)) < 3:
            features['corner'] = 1 
        else:
            features['corner'] = 0
        return features
    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        #print (actions)
        stateAction = [(gameState.generateSuccessor(self.index, action), action) for action in actions]
        values = [(self.evaluate(state, action), action) for state,action in stateAction]
        
        print (values)
        #maxValue = max(values)
        #bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        #print (bestActions)
        curAction = max([(self.evaluate(state, action), action) for state, action in stateAction])[1]
        #print (curAction)
        if gameState.generateSuccessor(self.index, curAction).getAgentPosition(self.index) in self.getCapsules(gameState):
            myAgent.isPowerful = True
            myAgent.powerfulTime = 160
        
        if myAgent.isPowerful and myAgent.powerfulTime > 0:
            myAgent.powerfulTime -= 2
            if (myAgent.powerfulTime == 0):
                myAgent.isPowerful = False
        
        
        return curAction
    
    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        print (action)
        print (features)
        weights = self.getWeights(gameState, action)
        for i in self.mods:
            self.mods[i].process(gameState)
        
        return features * weights
    def checkArea(self,gameState,enemyPos):
        #same side -1 diff side 1
        width, height = gameState.data.layout.width, gameState.data.layout.height
        if self.red:
            return -1.0 if enemyPos[0] < width / 2 else 1.0
        else:
            return -1.0 if enemyPos[0] > width / 2 else 1.0
    
    def statusCheck(self, gameState):
        width, height = gameState.data.layout.width, gameState.data.layout.height
        myPos = gameState.getAgentPosition(self.index)
        if self.red:
            return -1.0 if myPos[0] < width / 2 else 1.0
        else:
            return -1.0 if myPos[0] > width / 2 else 1.0
        
    
class PacmanInference:


    def __init__(self, _enemyIndex, _selfIndex, gameState):
       
        self.selfIndex = _selfIndex;
        self.enemyIndex = _enemyIndex;
        self.legalPositions = [p for p in gameState.getWalls().asList(False)]
        
        #print(self.legalPositions)
        #self.walls = gameState.getWalls()
        self.initializeUniformly(gameState)
           
    def initializeUniformly(self, gameState):
        self.beliefs = util.Counter()
        for p in self.legalPositions: 
            self.beliefs[p] = 1.0
        self.beliefs.normalize()
          
    def getMostLikelyPosition(self):
        return self.beliefs.argMax()
       
    def process(self, gameState):
        noisyDistance = gameState.getAgentDistances()
        #print (noisyDistance)
        self.elapseTime(gameState)
        self.observe(noisyDistance,gameState)
#              
    def observe(self, observation, gameState):
        noisyDistance = observation[self.enemyIndex]
        enemyPosition = gameState.getAgentPosition(self.enemyIndex)
        myPosition = gameState.getAgentPosition(self.selfIndex)
        #print(self.beliefs.keys())
        #print(self.legalPositions)
        if enemyPosition == None:   #cannot observe enemy
            
            for p in self.legalPositions:
                trueDistance = util.manhattanDistance(myPosition, p)
                self.beliefs[p] *= gameState.getDistanceProb(trueDistance, noisyDistance)
            self.beliefs.normalize()
        else:
            #self.beliefs = util.Counter()
            for p in self.legalPositions:
                self.beliefs[p] = 0
            self.beliefs[enemyPosition] = 1


    def elapseTime(self, gameState):



        updateBeliefs = util.Counter()
    
        for p in self.legalPositions:
            if self.beliefs[p] == 0:
                continue
            updatePositions={}
            x,y=p
            for dx,dy in ((-1,0),(0,0),(1,0),(0,-1),(0,1)):
                newX = x + dx
                newY = y + dy
                if (newX, newY) in self.legalPositions:
                    updatePositions[(newX, newY)] = 1
            prob = 1.0 / len(updatePositions)
            
            for pos in updatePositions:
                updateBeliefs[pos] += prob*self.beliefs[p]
        
        updateBeliefs.normalize()
        
        if self.beliefs.totalCount() == 0.0:
            self.initializeUniformly(gameState)       
        else:
            self.beliefs=updateBeliefs    
            