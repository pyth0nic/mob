import ray
import random
import uuid
from statistics import mean
import logging
import json

logger = logging.getLogger(__name__)


def distance(a, b):
    d = ((b.x-a.x)**2 + (b.y-a.y)**2)**(1/2)
    return round(d,2)

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
        return AgentState(agent.id, agent.alive(), agent.x, agent.y, agent.health, agent.category)

class AgentState:
    def __init__(self, uuid, alive, x, y, health, category):
        self.id = uuid
        self.alive = alive
        self.x = x
        self.y = y
        self.health = health
        self.category = category
        self.type = "AgentState"

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = uuid.uuid4().hex
        self.type = "Food"
        

class Agent(object):
    def __init__(self, environment):
        #self.size = 1
        self.environment = environment
        
        # should check whether there are surrounding agents by some threshold
        self.id = uuid.uuid4().hex
        self.x = random.randint(0, environment.size)
        self.y = random.randint(0, environment.size)
        self.health = 10
        self.foods = []
        self.logger = logging.getLogger(__name__)
        self.category = random.choice([1,2,3])
        self.state = AgentState(self.id, self.alive(), self.x, self.y, self.health, self.category)
        self.type = "Agent"
        self.route = []
        self.seen = []


    # each step should perform various combinations of each behaviour
    def step(self, foods):
        if not self.alive():
            return self.foods

        self.environment.foods = foods
        self.move()
        self.eat()
        self.health = self.health - self.environment.decayRate
        self.state = AgentState(self.id, self.alive(), self.x, self.y, self.health, self.category)
        return self.foods

    def size(self):
        return len(self.foods)

    def alive(self):
        return True if self.health > 0 else False

    # Actions, should take a vector, actor accelerates in that direction
    # degrees are made up from combinations of [up right, down right, up left, down left]
    def move(self):
        # need to avoid agents that are larger
        # need to eat the closest food
        # question, build a policy engine and router
        # use reinforcement learning to build policies?
        def travel(x, y):
            if x < 0:
                x = self.environment.width
            if x > self.environment.width:
                x = 0
            if y < 0:
                y = self.environment.height
            if y > self.environment.height:
                y = 0
            return x, y

        def findFoodAndDistance():
            foods, agents = self.see()
            foods = list((sorted(foods, key=lambda food: abs(distance(self, food)))))
            food = foods[1]
            d = abs(int(distance(self, food)))
            return food, d

        def route():
            self.eat()
            food, d = findFoodAndDistance()
            if d == 0:
                self.logger.warning("NOPE ROUTE HERE %d %d" % (d, self.health))
                self.eat();
                self.logger.warning("HEALTH %d " % self.health)
                food, d = findFoodAndDistance()

            x = self.x
            y = self.y
            sign = lambda n, n1 : 0 if n == n1 else (1 if n > n1 else -1)
            for i in range(d):
                xs = sign(food.x, x)
                x = x + xs
                ys = sign(food.y, y)
                y = y + ys
                #tx, ty = travel(x, y)
                self.logger.warning("%d %d" % (x, y))
                #if (tx == x & ty == y):
                self.route.append((xs, ys))

            self.logger.warning("ROUTE LENGTH %d" % len(self.route))

        def routeTraverse():
            if len(self.route) > 0:
                point = self.route.pop()
                self.x = self.x + point[0]
                self.y = self.y + point[1]
                self.eat()

        if (self.category == 1):
            # move one space in a random direction
            rl = random.choice([(1,0), (0,1), (-1,0),(0,-1),(2, -1), (-1, 2), (-2, 1), (1, -2)])
            self.x = self.x + rl[0]
            self.y = self.y + rl[0]
            x, y = travel(self.x, self.y)
            self.x = x
            self.y = y

        elif self.category == 2 | self.category == 3:
                food, d = findFoodAndDistance()
                if (len(self.route) == 0):
                    route()
                routeTraverse()
            
        self.eat()

    # senses
    # get all objects that surround the agent
    # with each move the agent should update the in view list
    def see(self):
        currentEnvironment = self.environment
        foods = list(filter(lambda food: int(distance(self, food)) <= currentEnvironment.visibility, currentEnvironment.foods))
        agents = list(filter(lambda agent: currentEnvironment.agents, currentEnvironment.agents))
        # see food diet, if I can see it, I can eat it
        self.seen = foods
        return foods, agents

    # Rules/behaviours
    # each move should check whether rules
    # rules need to accept the environment 
    def eat(self):
        currentEnvironment = self.environment
        onFoods = [food for food in self.seen if (self.x == food.x) & (self.y == food.y)]
        if len(onFoods) == 0:
            #self.logger.warning("NAH", self.x, self.y)
            return self.foods

        for onFood in onFoods:
            self.health = self.health + 1
            self.foods.append(onFood)
        return self.foods

# each AgarAgent needs access to the environment
@ray.remote
class Environment(object):
    def __init__(self, size, agentVisibility, foodSpawnRate, numberOfAgents, decayRate):
        self.size = size
        self.width = size
        self.height = size

        # constants
        # minimum size difference an agent needs to be to eat another agent
        self.edibleThreshold = 5
        # radius that agents can see other objects
        self.visibility = agentVisibility
        # number of foods spawned each cycle
        self.foodSpawnRate = foodSpawnRate
        # number of starting agents
        self.numberOfAgents = numberOfAgents

        self.decayRate = decayRate
        self.lastFoods = []
        self.foods = []
        self.agents = []
        self.agents = [Agent(self) for i in range(self.numberOfAgents)]
        self.logger = logging.getLogger(__name__)
        self.type = "Environment"

    def printAlive(self):
        point = lambda x: 1 if x.alive() else 0
        aliveCount = sum(map(point, self.agents))
        avgHealth = max(map(lambda x: x.health, self.agents)) if len(self.agents) > 0 else 0
        self.logger.warning("=== ALIVE c: %d h: %d ====" % (aliveCount, avgHealth))

    def run(self, itr):
        self.logger.warning("=== CYCLE %d ===" % itr)
        self.generateFood()
        self.lastFoods = self.foods
        self.logger.warning("=== FOODS %d ===" % len(self.foods))
        for agent in self.agents:
            foods = agent.step(self.foods)
            self.foods = list(filter(lambda f: f.id not in list(map(lambda f1: f1.id, foods)), self.foods))
        
        self.printAlive()
        self.logger.warning("=== FOODS %d ===" % len(self.foods))
        self.logger.warning("\n")
        return self.agents, self.lastFoods

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
        while (foodCount < originalFoodCount + self.foodSpawnRate) and tryCount < 5:
            foodCount = len(self.foods)
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            if not self.occupiedSpot(x, y):
                food = Food(x, y)
                self.foods.append(food)
                tryCount = 0
            else:
                tryCount += 1
        

# information of each cycle should be sent over socket
async def run(ws):
    logger = logging.getLogger(__name__)
    if not ray.is_initialized():
        ray.init()
    environment = Environment.remote(10, 20, 10, 5, 1)
    i = 0
    for i in range(1000):
        agents, foods = ray.get(environment.run.remote(i))
        if len(list(filter(lambda x : x.alive(), agents))) > 0 :
            await ws.send(json.dumps(Cycle(i, agents, foods), default=Cycle.toJSON))
        else:
            logger.warning("=== CYCLES COMPLETED %d ===" % i)

if __name__ == "__main__":
    if not ray.is_initialized():
        ray.init()
    environment = Environment(10, 20, 20, 1, 1)
    for i in range(30):
        agents, foods = environment.run(i)
        if len(list(filter(lambda x : x.alive(), agents))) == 0:
            break
    #ray.shutdown()