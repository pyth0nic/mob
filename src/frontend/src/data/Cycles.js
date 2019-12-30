import uuid from 'uuid'
export default class Cycles {
    constructor(cycles) {
        let websocket = new WebSocket("ws://" + window.location.hostname + ":3000" + "/environment")

        websocket.onopen = function (e) {
            console.log("OPEN")
            let a = {
                simId: uuid(),
                cycles: 10,
                environmentSize: 10, 
                agentStartingHealth: 10, 
                agentCategories: [2,3], 
                edibleThreshold: 5,
                agentSight: 5, 
                foodSpawnRate: 5, 
                startingAgentCount: 5,
                decayRate : 1
            }
            console.log(websocket)
            websocket.send(JSON.stringify(a));
        }

        websocket.onmessage = function (e) {
            console.log(e);
            let message = JSON.parse(e.data);
            message.agents = message.agents.map(x=> JSON.parse(x));
            message.foods = message.foods.map(x=> JSON.parse(x));
            cycles.push(message);
        }
        this.websocket = websocket
    }
}