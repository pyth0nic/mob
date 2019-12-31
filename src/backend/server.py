from sanic import Sanic
from sanic.response import json
from sanic.websocket import WebSocketProtocol
from os.path import dirname, abspath, join
import json

from schema.simulation import SimulationRequestV1, FoodV1, AgentV1, CycleV1, ToDTO
from backend.messaging.client import SimulationClient
import ray

_CURDIR = dirname(abspath(__file__))

app = Sanic()
app.static('/', join(_CURDIR, './dist'))

@app.websocket('/environment')
async def environment(request, ws):
    await SimulationClient.run(request, ws)
    del sim

def start():
    app.run(host="0.0.0.0", port=3000, protocol=WebSocketProtocol, debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, protocol=WebSocketProtocol, auto_reload=True)
