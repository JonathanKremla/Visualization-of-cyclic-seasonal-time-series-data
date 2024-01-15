<template>
  <div>
    <h2>Choose data set:</h2>
    <div>
      <v-btn-toggle v-model="chosenDataSet">
        <v-btn
          @click="getMessage(1)"
          value="Weather data of max temperatures per day from Raleigh Durham in Fahrenheit from 2017 to 2022"
          >Get Data 1</v-btn
        >
        <v-btn @click="getMessage(2)" value="2">Get Data 2</v-btn>
      </v-btn-toggle>
      <h2 v-if="chosenDataSet">Chosen Data Set:</h2>
      <pre>{{ chosenDataSet }}</pre>
    </div>

    <div v-if="chosenDataSet">
      <h2>Choose displayment:</h2>
      <router-link to="/lineAndCyclePlot">
        <v-btn>Display data as line plot and cyle plot</v-btn>
      </router-link>
      <router-link to="/lineAndSpiralPlot">
        <v-btn>Display data as line plot and spiral plot</v-btn>
      </router-link>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ManageData",
  data() {
    return {
      chosenDataSet: null,
      data: "",
      customData: "",
    };
  },
  methods: {
    getMessage(id) {
      const path = `http://localhost:5001/sample/sampleData${id}`;
      axios
        .get(path)
        .then((res) => {
          console.log(res)
          localStorage.setItem("data", JSON.stringify(eval(`res.data.sampleData${id}`)));
        })
        .catch((error) => {
          console.error(error);
        });
    },
    sendCustomData() {
      const path = "http://localhost:5001/custom/customData1";
      axios
        .put(path, { data: this.customData })
        .then((res) => {
          localStorage.setItem("data", JSON.stringify(res.data));
        })
        .catch((error) => {
          console.error("Error sending custom data:", error);
        });
    },
  },
  created() {
    // You can choose to load data for a default button here, or leave it empty
  },
};
</script>


