<template>
  <div class="hello">
    <p>
      For a guide and recipes on how to configure / customize this project,<br>
      check out the
    </p>
    <vue-p5
        @setup="setup"
        @draw="draw"
        >
    </vue-p5>
  </div>
</template>

<script>
class Agent {
  constructor(agent, sketch) {
        this.sketch = sketch;
        this.name = agent.name
        this.alive = agent.alive
        this.x = agent.x
        this.y = agent.y
        this.health = agent.health
    }

  run(sketch) {
    this.display(sketch);
  }

  // Method to update position
  update(agent) {
    this.alive = agent.alive; 
    this.health = agent.health;
    this.x = agent.x; 
    this.y = agent.y;
  }

  // Method to display
  display(sketch) {
    sketch.stroke(200, this.health * 10);
    sketch.strokeWeight(2);
    sketch.fill(127, this.health * 5);
    sketch.ellipse(this.x * 100, this.y * 100, 5, 5);
    sketch.text(this.health, this.x * 100 + 5, this.y * 100 + 5)
  }

  // Is the particle still useful?
  isDead(){
    return this.health <= 0;
  }
}

class Cycle {

  constructor(cycle, agents, food, sketch) {
    this.sketch = sketch;
    this.cycle = cycle;
    this.agents = agents;
    this.food = food;
  }

  run(sketch) {
    if (!this.agents || this.agents.length == 0) {
      return;
    }
    for (let i = this.agents.length-1; i >= 0; i--) {
      let agent = new Agent(this.agents[i], sketch);
      agent.run(sketch);
      if (agent.isDead()) {
        this.agent.splice(i, 1);
      }
    }
  }
}

import VueP5 from "vue-p5";
import Cycles from '../data/Cycles';

export default {
  name: "Environment",
  components: {
    "vue-p5": VueP5
  },
  data: () => ({
    system: {},
    cycles: [],
    currentCycle: 1,
    cycleSocket: {}
  }),
  computed: {

  },
  methods: {
    setup(sketch) {
      sketch.createCanvas(500, 500);
      this.cycleSocket = new Cycles(this.cycles);
    },
    draw(sketch) {
        sketch.frameRate(1)
        sketch.background(51);
        sketch.text(this.currentCycle, 480, 480)
        console.log(this.cycles)
        if (this.cycles && this.cycles[this.currentCycle]) {
          let cycle = this.cycles[this.currentCycle];
          new Cycle(cycle.cycle, cycle.agents, cycle.food, sketch).run(sketch);
          this.currentCycle = (this.currentCycle < this.cycles.length -1) ? this.currentCycle + 1 : 0;
        }
    },
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
