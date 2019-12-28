from sanic import Sanic
from sanic.response import json
from sanic.websocket import WebSocketProtocol
from universe import Environment, AgentState, Agent, Food, run
import json

app = Sanic()

# for each iteration need agent positions and food positions
@app.websocket('/environment')
async def environment(request, ws):
    while True:
        await run(ws)
        data = await ws.recv()
        print('Received: ' + data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, protocol=WebSocketProtocol)