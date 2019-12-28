export default class Cycles {
    constructor(cycles) {
        this.websocket = new WebSocket("ws://" + window.location.hostname + ":8080" + "/environment")

        this.websocket.onopen = function (e) {
            console.log("OPEN")
        }

        this.websocket.onmessage = function (e) {
            let message = JSON.parse(e.data);
            cycles.push(message);
        }
    }
}