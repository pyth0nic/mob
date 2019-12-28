<template>
  <div>
    <div :class="{ count: currentCycle > 0, start: currentCycle == 0 }">
      <p>
        {{ currentCycle == 0 ? "Double click to start" : "Current Cycle:" + currentCycle }}
      </p>
    </div>
    <div class="simulation"> 
      <div class="canvas">
        <vue-p5
            @setup="setup"
            @draw="draw"
            @mouseclicked="mouseClicked"
            >
        </vue-p5>
      </div>
      <div class="side-bar">
        <div v-if="cycles.length > 0 && currentAgents.length > 0">
          <div v-for="agent in currentAgents" v-bind:key="agent.id">
            <p>{{namesMap[agent.id] + " - " + agent.health }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.start {
  text-align: center;
}

.count {
  text-align: right;
}

.simulation {
  display: flex;
  align-items: center;
  justify-content: center;
  border-color: darkorange;
  border-style: solid;
  border-width: 0.1em;
  padding-top: 0.25em
}

.side-bar {
  min-width: 12em;
  max-height: 50em;
}

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

<script>
const { uniqueNamesGenerator, names, adjectives, colors } = require('unique-names-generator');

class Food {
    constructor(food, sketch) {
        this.sketch = sketch;
        this.x = (food.x * 50) + 25;
        this.y = (food.y * 50) + 25;
        this.id = food.id;
    }

    run(sketch) {
      this.display(sketch);
    }

    // Method to display
    display(sketch) {
      sketch.fill("yellow")
      sketch.strokeWeight(2);
      sketch.ellipse(this.x, this.y, 5, 5);
    }
}

class Agent {
  constructor(agent, sketch, namesMap) {
        this.sketch = sketch;
        this.id = agent.id;
        this.alive = agent.alive;
        this.x = (agent.x * 50) + 25;
        this.y = (agent.y * 50) + 25;
        this.health = agent.health;
        this.namesMap = namesMap;
        this.category = agent.category;
        this.generateDisplayName();
    }
  
  generateDisplayName(namesMap) {
    if (!this.namesMap[this.id]) {
          this.namesMap[this.id] = uniqueNamesGenerator({
            dictionaries: [adjectives, colors],
            separator: '-',
            length: 2,
          });
        }
  }

  run(sketch) {
    this.display(sketch);
  }

  // Method to display
  display(sketch) {
    if (this.health == 0) {
      sketch.text(this.health, this.x, this.y)
      return;  
    }
    if (this.category == 1) {
      sketch.fill("blue");
    } else {
      sketch.fill("black");
    }
    sketch.strokeWeight(2);
    let radius = Math.max(10, this.health * 5);
    sketch.ellipse(this.x, this.y, radius, radius);
    sketch.fill("black");
    sketch.text(this.namesMap[this.id] + "::" + this.health, this.x, this.y)
  }

  // Is the particle still useful?
  isDead() {
    return this.health <= 0;
  }
}

class Cycle {

  constructor(cycle, agents, foods, sketch, namesMap) {
    this.sketch = sketch;
    this.cycle = cycle;
    this.agents = agents;
    this.foods = foods;
    this.namesMap = namesMap;
  }

  getAgents() {
    return this.agents || [];
  }

  run(sketch) {
    if (this.foods && this.foods.length > 0) {
        for (let i = 0; i < this.foods.length; i++) {
          let food = new Food(this.foods[i], sketch);
          food.run(sketch);
        }
    }

    if (this.agents && this.agents.length > 0) {
      for (let i = this.agents.length-1; i >= 0; i--) {
        let agent = new Agent(this.agents[i], sketch, this.namesMap);
        agent.run(sketch);
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
    currentCycle: 0,
    currentAgents: {},
    cycleSocket: {},
    paused: false,
    sketch: {},
    namesMap: {}
  }),
  computed: {

  },
  methods: {
    mouseClicked(sketch) {
      sketch.ellipse(sketch.mouseX, sketch.mouseY, 5, 5);
      this.paused = !this.paused;
      if (this.paused) {
        sketch.noLoop();
      } else {
        sketch.loop();
      }
    },
    setup(sketch) {
      sketch.noLoop();
      sketch.createCanvas(575, 525);
      this.cycleSocket = new Cycles(this.cycles);
      this.sketch = sketch;
    },
    draw(sketch) {
        sketch.frameRate(1);
        sketch.background(51);

        if (this.cycles && this.cycles[this.currentCycle]) {
          let cycle = this.cycles[this.currentCycle];
          this.cycles[this.currentCycle].display = this.cycles[this.currentCycle].display || new Cycle(cycle.cycle, cycle.agents, cycle.foods, sketch, this.namesMap);
          this.currentAgents = this.cycles[this.currentCycle].display.agents;
          this.cycles[this.currentCycle].display.run(sketch);

          this.currentCycle = (this.currentCycle < this.cycles.length - 1) ? this.currentCycle + 1 : 0;
        }
    },
  }
};
</script>
