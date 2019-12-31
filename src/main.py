# main should 
import sys
from simulator.messaging.messaging import MessageClient 
from schema.simulation import SimulationRequestV1, FoodV1, AgentV1, ToDTO
from backend.server import start
import argparse

def getArgs():
    parser = argparse.ArgumentParser(description='Start frontend or workers. Add --frontend for server.')
    parser.add_argument('--frontend',
                   default=False, 
                   action="store_true",
                   help='start socket server and front end app')
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    if not args.frontend:
        client = MessageClient()
        client.listen()
    else:
        start()