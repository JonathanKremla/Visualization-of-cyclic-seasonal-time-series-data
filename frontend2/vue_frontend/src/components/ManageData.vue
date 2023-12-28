<template>
  <div>
    <button @click="getMessage(1)">Get Data 1</button>
    <button @click="getMessage(2)" disabled="true">Get Data 2</button>
    <button @click="getMessage(3)" disabled="true">Get Data 3</button>
    <div>
      <router-link to="/lineplot"> 
      <button>Display data as line plot</button>
      </router-link>
    </div>

    <div>
      <label for="customData">Enter Custom Data:</label>
      <input type="text" id="customData" v-model="customData" />
      <button @click="sendCustomData">Send Custom Data</button>
    </div>
  </div>


</template>

<script>
import axios from 'axios';
import LinePlotView from './LinePlotView.vue';

export default {
  components: { LinePlotView },
  name: 'ManageData',
  data() {
    return {
      data: '',
      customData: '',
    };
  },
  methods: {
    getMessage(id) {
      const path = `http://localhost:5001/sample/sampleData${id}`;
      axios.get(path)
        .then((res) => {
          localStorage.setItem("data", JSON.stringify(res.data.sampleData1))
        })
        .catch((error) => {
          console.error(error);
        });
    },
    sendCustomData() {
      const path = 'http://localhost:5001/custom/customData1';
      axios.put(path, { data: this.customData })
        .then((res) => {
          localStorage.setItem("data", JSON.stringify(res.data))
        })
        .catch((error) => {
          console.error('Error sending custom data:', error);
        });
    },
  },
  created() {
    // You can choose to load data for a default button here, or leave it empty
  },
};
</script>


