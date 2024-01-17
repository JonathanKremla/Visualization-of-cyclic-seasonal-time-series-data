<template>
  <div>
    <router-link to="/">
      <button>Home</button>
    </router-link>
    <CustomRangeSlider 
    v-if="this.dataSize"
    :data="this.data"
    :max="this.dataSize"
    :granularity="this.granularity"
    v-on:updatedRange="updateRange"
    ></CustomRangeSlider>
    <h2>Line Plot</h2>
    <LinePlotView v-if="this.displayedData" 
      :displayedData="this.displayedData"
      :updatedGranularity="this.updatedGranularity"
      v-on:selectedData="this.updateData"
    >
    </LinePlotView>

    <h2>Spiral Plot</h2>
    <div>
      <SpiralPlotView
        v-if="this.displayedData"
        :baseGranularity="this.granularity"
        :displayedData="this.selectedData ? this.selectedData : this.displayedData"
        v-on:updateGranularity="updateGranularity"
      ></SpiralPlotView>
    </div>
  </div>
</template>

<script>
import CustomRangeSlider from './CustomRangeSlider.vue';
import LinePlotView from "./LinePlotView.vue";
import SpiralPlotView from "./SpiralPlotView.vue";
export default {
  components: { LinePlotView, SpiralPlotView, CustomRangeSlider},
  data() {
    return {
      ticks: {},
      displayedRange: [0, 0],
      data: null,
      displayedData: null,
      dataSize: 0,
      granularity: undefined,
      updatedGranularity: undefined,
      selectedData: undefined,
    };
  },
  watch: {
    displayedRange: "sliceData",
  },
  computed: {},
  mounted() {
    this.cycles = this.displayedData / this.segmentsPerCycle;
    this.retrieveData();
    this.checkGranularity();
  },
  methods: {
    updateData(data) {
      this.selectedData = data;
    },
    updateGranularity(newGranularity) {
      this.updatedGranularity = newGranularity;
    },
    checkGranularity(){
      var days = [];
      this.data.forEach((el) => {
        var day = new Date(el.date).getDate();
        var month = new Date(el.date).getMonth();
        var year = new Date(el.date).getFullYear();
        var dateString = `${day} ${month} ${year}`
        if(dateString in days){
          days[dateString] += 1
        } else {
          days[dateString] = 1
        }
      })
      var average = 0;
      var length = 0;
      Object.values(days).forEach((count) => {
        average += count
        length += 1
      })
      //calculate rounded average to account for missing values
      average = Math.ceil(average/length)

      switch (average) {
        case 1:
          this.granularity = "Days"
          break;
        case 24:
          this.granularity = "Hours"
          break;
        default:
          console.error("Unknown granularity or too many missing values")
          break;
      }
    },
    updateRange(updatedRange) {
      this.displayedRange = updatedRange
    },
    sliceData() {
      if (this.displayedData !== null) {
        clearTimeout(this.watcherTimeout);
        // Set a new timeout to debounce the watcher function after 300 milliseconds of inactivity
        this.watcherTimeout = setTimeout(() => {
          this.displayedData = this.data.slice(
            this.displayedRange[0]-1,
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
        this.displayedData = this.data;
        this.dataSize = this.data.length;
        this.displayedRange = [0, this.dataSize];
      } catch (error) {
        console.error("Error retrieving data from local storage:", error);
      }
    },
  },
};
</script>