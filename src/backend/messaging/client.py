import pulsar
from pulsar.schema import *
from schema.simulation import SimulationRequestV1, CycleV1
import logging
import uuid
import ray

@ray.remote
class SimulationClient:
    client = None
    consumer = None
    def __init__(self, request):
        self.client = pulsar.Client('pulsar://localhost:6650')
        self.logger = logging.getLogger(__name__)
        self.consumer = self.client.subscribe("simulation-result", subscription_name="simulator-%s" % request.simId, schema=JsonSchema(CycleV1))

    def __del__(self):
        if self.client:
            self.consumer.close()
            self.client.close()
        if ray.is_initialized():
            ray.shutdown()

    def request(self, request):
        producer = self.client.create_producer('simulation-request', schema=JsonSchema(SimulationRequestV1))
        producer.send(request)

    def listen(self, request):
        msg = self.consumer.receive()
        cycle = msg.value()
        try:
            # todo use a topic for each or key based subscription would be better
            # python client not caught up to java client yet
            if msg.partition_key() == request.simId:
                self.consumer.acknowledge(msg)
                return cycle
        except Exception as e:
            print(e)
            self.consumer.negative_acknowledge(msg)
            return None

    @staticmethod
    def requestToRequest(r):
        j = json.loads(r)
        return SimulationRequestV1(**j)

    @staticmethod
    async def run(request, ws):
        if not ray.is_initialized():
            ray.init()
        while True:
            msg = await ws.recv()
            msg = SimulationClient.requestToRequest(msg)
            sim = SimulationClient.remote(msg)
            sim.request.remote(msg)
            for i in range(msg.cycles):
                result = ray.get(sim.listen.remote(msg))
                if result:
                    await ws.send(json.dumps(result.__dict__))
                else:
                    i=i-1
            await ws.close()
            del sim
