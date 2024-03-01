<template>
  <div>
    <h2>Choose data set:</h2>
    <div>
      <v-btn-toggle v-model="chosenDataSet">
        <v-btn
          @click="getMessage(1)"
          :value= "this.dataOneDisplayText"
          >Get Data 1</v-btn
        >
        <v-btn
          @click="getMessage(2)"
          :value= "this.dataTwoDisplayText"
          >Get Data 2</v-btn
        >
      </v-btn-toggle>
      <h2 v-if="chosenDataSet">Chosen Data Set:</h2>
      <pre>{{ chosenDataSet }}</pre>
    </div>

    <div v-if="chosenDataSet">
      <h2>Choose displayment:</h2>
      <v-container>
        <router-link to="/lineAndCyclePlot">
          <v-btn>Display data as line plot and cyle plot</v-btn>
        </router-link>
        <router-link to="/lineAndSpiralPlot">
          <v-btn>Display data as line plot and spiral plot</v-btn>
        </router-link>
        <router-link to="/cycleAndSpiralPlot">
          <v-btn>Display data as cycle plot and spiral plot</v-btn>
        </router-link>
        <router-link to="/allViews">
          <v-btn>Display data in all plots</v-btn>
        </router-link>
      </v-container>
    </div>
  </div>
</template>

<script>
import axios from "axios";

const dataOneDisplayText = "Weather data of max temperatures per day from Raleigh Durham in Fahrenheit from 2017 to 2022"
const dataTwoDisplayText = "Room temperature Data measured hourly from January to November 2022                            "

export default {
  name: "ManageData",
  data() {
    return {
      dataOneDisplayText: dataOneDisplayText,
      dataTwoDisplayText: dataTwoDisplayText,
      chosenDataSet: null,
      data: "",
      customData: "",
    };
  },
  mounted() {
    this.getData()
  },
  methods: {
    getData() {
      var d= localStorage.getItem("data");
      if(d[7] == 7){
        this.chosenDataSet = dataOneDisplayText;
      } else if(d) {
        this.chosenDataSet = dataTwoDisplayText;
      }
    },
    getMessage(id) {
      var address = ""
      if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        address = "localhost:8080";
      } else {
        address = "lavender-swan-81598.zap.cloud";
      }
      console.log(window.location.host)


      const path = `http://${address}/sample/sampleData${id}`;
      axios
        .get(path)
        .then((res) => {
          localStorage.setItem(
            "data",
            JSON.stringify(eval(`res.data.sampleData${id}`))
          );
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
