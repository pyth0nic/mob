import pulsar
from pulsar.schema import *
from simulator.simulation.simulation import Simulator, Cycle, Food, Agent
import logging
import json
import sys
from schema.simulation import SimulationRequestV1, FoodV1, AgentV1, CycleV1, ToDTO

class MessageClient:
    def __init__(self):
        self.client = pulsar.Client('pulsar://localhost:6650')
        self.logger = logging.getLogger(__name__)

    def sendRequest(self):
        req = SimulationRequestV1(simId="asd",
                              cycles = 10,
                              environmentSize= 10, 
                              agentStartingHealth= 10, 
                              agentCategories= [2,3], 
                              edibleThreshold= 5,
                              agentSight= 5, 
                              foodSpawnRate= 5, 
                              startingAgentCount= 5,
                              decayRate = 1)
        
        producer = self.client.create_producer('simulation-request', schema=JsonSchema(SimulationRequestV1))
        producer.send(req)

    def runSimulation(self, request : SimulationRequestV1):
        sim = Simulator(request)
        i = 0
        producer = self.client.create_producer('simulation-result', schema=JsonSchema(CycleV1))
        for i in range(request.cycles):
            cycle = sim.step(i)
            cyclev1 = ToDTO.toCycle(cycle)
            producer.send(cyclev1, partition_key=request.simId, sequence_id=i)

    # subscribe to a simulation request topic
    def listen(self):
        consumer = self.client.subscribe(
                  topic='simulation-request',
                  subscription_name='simulator',
                  schema=JsonSchema(SimulationRequestV1))

        while True:
            msg = consumer.receive()
            request = msg.value()
            try:
                consumer.acknowledge(msg)
                self.runSimulation(request)
                # Acknowledge successful processing of the message
            except:
                # Message failed to be processed
                consumer.negative_acknowledge(msg)