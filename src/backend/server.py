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
        data = 'hello!'
        print('Sending: ' + data)
        await run(ws)
        await ws.send(json.dumps(AgentState("",True, 1,1,10).__dict__))
        data = await ws.recv()
        print('Received: ' + data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, protocol=WebSocketProtocol)