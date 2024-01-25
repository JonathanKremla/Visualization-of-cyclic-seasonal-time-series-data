<template>
  <div>
    <router-link to="/">
      <v-btn>
        Home
        <v-icon size="large" color="black" icon="mdi-home"></v-icon>
      </v-btn>
    </router-link>
    <CustomRangeSlider
      v-if="this.dataSize"
      v-model="this.displayedDataRange"
      :data="this.data"
      :displayedData="this.displayedData"
      :max="this.dataSize"
      :granularity="this.granularity"
      v-on:updatedRange="updateRange"
    ></CustomRangeSlider>

    <h2>Line Plot</h2>
    <LinePlotView
      v-if="this.displayedData"
      :displayedData="this.displayedData"
      :updatedGranularity="this.selectedGranularity.split('-')[0]"
      :highlightedData="this.highlightedSpiralData != undefined ? this.highlightedSpiralData : this.highlightedData"
      v-on:selectedData="this.updateData"
    >
    </LinePlotView>
    <h2>Cylce Plot</h2>

    <v-card>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col>
              <v-select
                v-model="this.firstGranularity"
                label="Select First Granularity:"
                :items="this.firstGranItems"
              ></v-select>
            </v-col>
            <v-col>
              <v-select
                v-model="this.secondGranularity"
                :disabled="!this.firstGranularity"
                label="Select Second Granularity:"
                :items="this.secondGranItems"
              ></v-select>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>

    <CyclePlotView
      v-if="this.displayedData"
      :displayedData="this.displayedData"
      :granularity="this.selectedGranularity"
      v-on:highlightedData="this.highlightData"
    ></CyclePlotView>
    <h2>Spiral Plot</h2>
    <div>
      <SpiralPlotView
        v-if="this.displayedData"
        :baseGranularity="this.granularity"
        :selectedGranularity="this.firstGranularity"
        :displayedData="
          this.selectedData ? this.selectedData : this.displayedData
        "
        :highlightData="this.highlightedData"
        v-on:highlightedData="this.highlightSpiralData"
        v-on:updateGranularity="updateGranularity"
      ></SpiralPlotView>
    </div>
  </div>
</template>
<script>
import CustomRangeSlider from "./CustomRangeSlider.vue";
import CyclePlotView from "./CyclePlotView.vue";
import SpiralPlotView from "./SpiralPlotView.vue";
import LinePlotView from "./LinePlotView.vue";
export default {
  components: {
    SpiralPlotView,
    CyclePlotView,
    CustomRangeSlider,
    LinePlotView,
  },
  data() {
    return {
      firstGranItems: undefined,
      secondGranItems: undefined,
      firstGranularity: undefined,
      secondGranularity: undefined,
      displayedRange: [0, 0],
      data: null,
      displayedData: null,
      displayedDataRange: null,
      displayedDataCycle: null,
      selectedData: null,
      dataSize: 0,
      granularity: undefined,
      highlightedData: undefined,
      highlightedSpiralData: undefined,
      selectedGranularity: "",
    };
  },
  watch: {
    displayedRange: "sliceData",
    selectedGranularity: "resetHighlighting",
    firstGranularity: "setSecondGranularityOptions",
    secondGranularity: "setGranularity",
  },
  mounted() {
    this.retrieveData();
    this.checkGranularity();
  },
  methods: {
    highlightSpiralData(data) {
      this.highlightedSpiralData = data;
    },
    updateGranularity(newGranularity) {
      this.firstGranularity = newGranularity;
    },
    setGranularity() {
      this.selectedGranularity =
        this.firstGranularity + "-per-" + this.secondGranularity;
    },
    setSecondGranularityOptions() {
      switch (this.firstGranularity) {
        case "Hours":
          this.secondGranItems = ["Day"];
          break;
        case "Days":
          this.secondGranItems = ["Week", "Month"];
          break;
        case "Weeks":
          this.secondGranItems = ["Month", "Year"];
          break;
        case "Months":
          this.secondGranItems = ["Year"];
          break;
        default:
          break;
      }
      if (this.secondGranularity) {
        this.selectedGranularity = undefined;
        this.secondGranularity = undefined;
      }
    },
    resetHighlighting() {
      this.highlightedData = null;
    },
    updateData(selectedData) {
      this.displayedData = selectedData;
      this.displayedDataRange = [
        this.data.findIndex((el) => el.date == selectedData[0].date),
        this.data.findIndex(
          (el) => el.date == selectedData[selectedData.length - 1].date
        ),
      ];
      console.log(this.displayedDataRange);
      console.log(selectedData);
      console.log(this.data);
    },
    highlightData(highlightedData) {
      this.highlightedData = highlightedData;
    },
    checkGranularity() {
      var days = [];
      this.data.forEach((el) => {
        var day = new Date(el.date).getDate();
        var month = new Date(el.date).getMonth();
        var year = new Date(el.date).getFullYear();
        var dateString = `${day} ${month} ${year}`;
        if (dateString in days) {
          days[dateString] += 1;
        } else {
          days[dateString] = 1;
        }
      });
      var average = 0;
      var length = 0;
      Object.values(days).forEach((count) => {
        average += count;
        length += 1;
      });
      //calculate rounded average to account for missing values
      average = Math.ceil(average / length);

      switch (average) {
        case 1:
          this.granularity = "Days";
          this.firstGranItems = ["Days", "Weeks", "Months"];
          break;
        case 24:
          this.granularity = "Hours";
          this.firstGranItems = ["Hours", "Days", "Weeks", "Months"];
          break;
        default:
          console.error("Unknown granularity or too many missing values");
          break;
      }
    },
    updateRange(updatedRange) {
      this.displayedRange = updatedRange;
    },
    sliceData() {
      if (this.displayedData !== null) {
        clearTimeout(this.watcherTimeout);
        // Set a new timeout to debounce the watcher function after 300 milliseconds of inactivity
        this.watcherTimeout = setTimeout(() => {
          this.displayedData = this.data.slice(
            this.displayedRange[0],
            this.displayedRange[1]
          );
        }, 300);
      }
    },
    retrieveData() {
      try {
        // Retrieve JSON string from local storage and parse it to a JavaScript object
        const jsonData = localStorage.getItem("data");
        const parsedData = JSON.parse(JSON.parse(jsonData));
        var tempDate;
        if (Object.keys(parsedData)[0].split(" ")[1] == undefined) {
          this.data = Object.entries(parsedData).map(([date, value]) => ({
            date: (() => {
              var d = new Date(date);
              d.setHours(0);
              return d.toLocaleDateString("en-US", {
                hour: "numeric",
                minute: "numeric",
                second: "numeric",
                day: "numeric",
                month: "short",
                year: "numeric",
              });
            })(),
            value: parseFloat(value),
          }));
        } else {
          this.data = Object.entries(parsedData).map(([date, value]) => ({
            date: new Date(date).toLocaleDateString("en-US", {
              hour: "numeric",
              minute: "numeric",
              second: "numeric",
              day: "numeric",
              month: "short",
              year: "numeric",
            }),
            value: parseFloat(value),
          }));
        }
        this.displayedData = this.data;
        this.dataSize = this.data.length;
        this.displayedRange = [0, this.dataSize];
        this.displayedDataRange = [0, this.dataSize];
      } catch (error) {
        console.error("Error retrieving data from local storage:", error);
      }
    },
  },
};
</script>
