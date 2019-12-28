<template>
  <div id="app">
    <Environment />
  </div>
</template>

<script>
import Environment from './components/Environment.vue'

export default {
  name: 'app',
  components: {
    Environment
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
