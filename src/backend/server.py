from sanic import Sanic
from sanic.response import json
from sanic.websocket import WebSocketProtocol
from os.path import dirname, abspath, join
import json
import pulsar
from pulsar.schema import *
# todo make library
from schema.simulation import SimulationRequestV1, FoodV1, AgentV1, CycleV1, ToDTO
import logging
import uuid

_CURDIR = dirname(abspath(__file__))

app = Sanic()
app.static('/', join(_CURDIR, './dist'))

class SimulationClient:
    def __init__(self):
        self.client = pulsar.Client('pulsar://localhost:6650')
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.client.close()

    def request(self, request):
        producer = self.client.create_producer('simulation-request', schema=JsonSchema(SimulationRequestV1))
        producer.send(request)
        return request.simId

    async def listen(self, request, ws):
        consumer = self.client.subscribe("simulation-result", subscription_name="simulator", schema=JsonSchema(CycleV1))
        for _ in range(request.cycles):
            msg = consumer.receive()
            cycle = msg.value()
            try:
                # todo use a topic for each or key based subscription would be better
               # if msg.partition_key() == request.simId | 1 == 1:
                consumer.acknowledge(msg)
                    # Acknowledge successful processing of the message
                await ws.send(json.dumps(cycle.__dict__))
                #else:
                 #   consumer.negative_acknowledge(msg)
            except Exception as e:
                # Message failed to be processed
                print(e)
                consumer.negative_acknowledge(msg)
        consumer.close()

def requestToRequest(r):
        j = json.loads(r)
        return SimulationRequestV1(**j)

sim = SimulationClient()

@app.websocket('/environment')
async def environment(request, ws):
    while True:
        msg = await ws.recv()
        msg = requestToRequest(msg)
        id = sim.request(msg)
        await sim.listen(msg, ws)

def start():
    app.run(host="0.0.0.0", port=3000, protocol=WebSocketProtocol, debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, protocol=WebSocketProtocol, auto_reload=True)
