<template>
  <div id="app">
    <SearchBox />
  </div>
</template>

<script>
import SearchBox from './components/SearchBox.vue'

export default {
  name: 'App',
  components: {
    SearchBox
  }
};
</script>

<style>
#app {
  font-family: Avenir, Arial, Helvetica, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>