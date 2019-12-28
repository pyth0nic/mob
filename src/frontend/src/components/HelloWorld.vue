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
class Particle {
  constructor(position, sketch) {
    this.sketch = sketch;
    this.acceleration = sketch.createVector(0, 0.05);
    this.velocity = sketch.createVector(sketch.random(-1, 1), sketch.random(-1, 0));
    this.position = position.copy();
    this.lifespan = 255;
    this.particles = [];
    this.origin = position;
  }

  run(sketch) {
    this.update();
    this.display(sketch);
  }

  // Method to update position
  update() {
    this.velocity.add(this.acceleration);
    this.position.add(this.velocity);
    this.lifespan -= 2;
  }

  // Method to display
  display(sketch) {
    sketch.stroke(200, this.lifespan);
    sketch.strokeWeight(2);
    sketch.fill(127, this.lifespan);
    sketch.ellipse(this.position.x, this.position.y, 12, 12);
  }

  // Is the particle still useful?
  isDead(){
    return this.lifespan < 0;
  }
}

class ParticleSystem {

  constructor(position, sketch) {
    this.sketch = sketch;
    this.origin = position.copy();
    this.particles = []
  }

  addParticle(sketch) {
    this.particles.push(new Particle(this.origin, sketch));
  };

  run(sketch) {
    for (let i = this.particles.length-1; i >= 0; i--) {
      let p = this.particles[i];
      p.run(sketch);
      if (p.isDead()) {
        this.particles.splice(i, 1);
      }
    }
  }
}

import VueP5 from "vue-p5";

export default {
  name: "HelloWorld",
  components: {
    "vue-p5": VueP5
  },
  data: () => ({
    system: {}
  }),
  computed: {

  },
  methods: {
    setup(sketch) {
      sketch.createCanvas(500, 500);
      this.system = new ParticleSystem(sketch.createVector(250 / 2, 50), sketch);
      console.log(this.system)
    },
    draw(sketch) {
        sketch.background(51);
        this.system.addParticle(sketch);
        this.system.run(sketch);
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
