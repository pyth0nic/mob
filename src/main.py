# main should 
import sys
from simulator.messaging.messaging import MessageClient 
from schema.simulation import SimulationRequestV1, FoodV1, AgentV1, ToDTO

if __name__ == "__main__":
    client = MessageClient()
    client.listen()