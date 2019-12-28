import ray
import random
import uuid
from statistics import mean
import logging
import json

logger = logging.getLogger(__name__)

class Cycle:
    def __init__(self, cycle, agents, foods):
        self.cycle = cycle
        self.agents = list(map(self.buildAgentState, agents))
        self.foods = foods
        self.type = "Cycle"

    def toJSON(obj):
        result = {}
        result["cycle"] = obj.cycle
        result["agents"] = [x.__dict__ for x in obj.agents]
        result["foods"] = [x.__dict__ for x in obj.foods]
        return result

    def buildAgentState(self, agent):
        return AgentState(agent.name, agent.alive(), agent.x, agent.y, agent.health)

class AgentState:
    def __init__(self, name, alive, x, y, health):
        self.name = name
        self.alive = alive
        self.x = x
        self.y = y
        self.health = health
        self.type = "AgentState"

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = uuid.uuid4().hex
        self.type = "Food"

class Agent(object):
    def __init__(self, name, environment):
        #self.size = 1
        self.environment = environment
        
        # should check whether there are surrounding agents by some threshold
        self.name = name
        self.x = random.randint(0, environment.size)
        self.y = random.randint(0, environment.size)
        self.health = 10
        self.state = AgentState(self.name, self.alive(), self.x, self.y, self.health)
        self.foods = []
        self.logger = logging.getLogger(__name__)
        self.type = "Agent"

    # each step should perform various combinations of each behaviour
    def step(self):
        if not self.alive():
            return self.state

        foods, agents = self.see()
        self.move(foods)
        self.health = self.health - self.environment.decayRate
        self.state = AgentState(self.name, self.alive(), self.x, self.y, self.health)
        return self.state

    def size(self):
        return len(self.foods)

    def alive(self):
        return True if self.health > 0 else False

    # Actions, should take a vector, actor accelerates in that direction
    # degrees are made up from combinations of [up right, down right, up left, down left]
    def move(self, visibleFoods):
        # need to avoid agents that are larger
        # need to eat the closest food
        # question, build a policy engine and router
        # use reinforcement learning to build policies?
        for i in range(self.environment.velocity):
            visibleFoods = self.eat(visibleFoods)
            # move one space in a random direction
            rl = random.choice([(1,0), (0,1), (-1,0),(0,-1),(2, -1), (-1, 2), (-2, 1), (1, -2)])
            self.x = self.x + rl[0]
            self.y = self.y + rl[0]
            if self.x < 0:
                self.x = self.environment.width
            if self.x > self.environment.width:
                self.x = 0
            if self.y < 0:
                self.y = self.environment.height
            if self.y > self.environment.height:
                self.y = 0


    # senses
    # get all objects that surround the agent
    # with each move the agent should update the in view list
    def see(self):
        def distance(a, b):
            return ((b.x - a.x)**2 + (b.y - a.y)**2)**1/2

        currentEnvironment = self.environment
        foods = list(filter(lambda food: distance(self, food) <= currentEnvironment.visibility, currentEnvironment.foods))
        agents = list(filter(lambda agent: currentEnvironment.agents, currentEnvironment.agents))
        return foods, agents

    # Rules/behaviours
    # each move should check whether rules
    # rules need to accept the environment 
    def eat(self, visibleFoods):
        onFood = list(filter(lambda food: self.x == food.x & self.y == food.y, visibleFoods))
        self.health = self.health + len(onFood)
        self.foods.append(onFood)
        if len(onFood) > 0:
            self.logger.debug("ATE FOOD")
        # would be better to be a dictionary and delete by id?
        self.environment.foods = list(filter(lambda food: food not in onFood, self.environment.foods))
        visibleFoods = list(filter(lambda food: food not in onFood, visibleFoods))
        return visibleFoods

# each AgarAgent needs access to the environment
@ray.remote
class Environment(object):
    def __init__(self, size, agentVelocity, agentVisibility, foodSpawnRate, numberOfAgents, decayRate):
        self.size = size
        self.width = size
        self.height = size

        # constants
        # max number of spaces an agent can move each turn
        self.velocity = agentVelocity
        # minimum size difference an agent needs to be to eat another agent
        self.edibleThreshold = 5
        # radius that agents can see other objects
        self.visibility = agentVisibility
        # number of foods spawned each cycle
        self.foodSpawnRate = foodSpawnRate
        # number of starting agents
        self.numberOfAgents = numberOfAgents

        self.decayRate = decayRate
        self.foods = []
        self.agents = []
        self.agents = [Agent(uuid.uuid4().hex, self) for i in range(self.numberOfAgents)]
        self.logger = logging.getLogger(__name__)
        self.type = "Environment"

    def printAlive(self):
        point = lambda x: 1 if x.alive() else 0
        aliveCount = sum(map(point, self.agents))
        avgHealth = mean(map(lambda x: x.health, self.agents)) if len(self.agents) > 0 else 0
        self.logger.warning("=== ALIVE c: %d h: %d ====" % (aliveCount, avgHealth))

    def run(self, itr):
        self.logger.warning("=== CYCLE %d ===" % itr)
        self.generateFood()
        [agent.step() for agent in self.agents]
        self.logger.warning("=== FOODS %d ===" % len(self.foods))
        self.printAlive()
        self.logger.warning("=== FOODS %d ===" % len(self.foods))
        self.logger.warning("\n")
        return self.agents, self.foods

    def occupiedSpot(self, x, y):
        for food in self.foods:
            if (food.x == x and food.y == y):
                return True
        for actor in self.agents:
            agent= actor
            if agent.x == x and agent.y == y:
                return True
        return False

    # add food where there currently is none and an agent is not occupying it
    def generateFood(self):
        originalFoodCount = len(self.foods)
        foodCount = len(self.foods)
        tryCount = 0
        while foodCount < originalFoodCount + self.foodSpawnRate and tryCount < 5:
            foodCount = len(self.foods)
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            if not self.occupiedSpot(x, y):
                food = Food(x, y)
                self.foods.append(food)
            else:
                tryCount += 1

# information of each cycle should be sent over socket
async def run(ws):
    ray.init()
    environment = Environment.remote(5, 5, 5, 20, 10, 1)
    for i in range(50):
        agents, foods = ray.get(environment.run.remote(i))
        await ws.send(json.dumps(Cycle(i, agents, foods), default=Cycle.toJSON))
    ray.shutdown()