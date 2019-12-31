from pulsar.schema import *
from simulator.simulation.simulation import Simulator, Cycle, Food, Agent

class Agents(Enum):
    RANDOM = 1
    SEEING = 2
    BREEDING = 3
    ATTACKING = 4
    COMMUNICATING = 5
    BUILDING = 6

class Foods(Enum):
    GOOD = 1
    BAD = 2

class PointV1():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class FoodV1():
    def __init__(self, foodId, x, y):        
        self.foodId = foodId
        self.x = x
        self.y = y

class AgentV1():
    def __init__(self, agentId, x, y, health, category, route):
        self.agentId = agentId
        self.x = x
        self.y = y
        self.health = health
        self.category = category
        self.route = route

class CycleV1(Record):
    cycle = Integer()
    agents = Array(String())
    foods = Array(String())

class SimulationRequestV1(Record):
    simId = String()
    environmentSize = Integer()
    agentStartingHealth = Integer() 
    agentCategories = Array(Integer())
    edibleThreshold = Integer() 
    agentSight = Integer()
    foodSpawnRate = Integer()
    startingAgentCount = Integer()
    cycles = Integer()
    decayRate = Integer()

class ToDTO:
    @staticmethod
    def toCycle(c: Cycle):
        return CycleV1(
            cycle = c.cycle,
            agents = [json.dumps(ToDTO.toAgent(agent).__dict__) for agent in c.agents],
            foods = [json.dumps(ToDTO.toFood(food).__dict__) for food in c.foods]
            )

    @staticmethod
    def toAgent(a):
        return AgentV1(
            agentId = a.agentId,
            x = a.x,
            y = a.y,
            health = a.health,
            category = a.category,
            route = list(map(lambda x: json.dumps(PointV1(x=x[0], y=x[1]).__dict__), a.route))
        )

    @staticmethod
    def toFood(f):
        return FoodV1(
            foodId = f.foodId,
            x = f.x,
            y = f.y
        )