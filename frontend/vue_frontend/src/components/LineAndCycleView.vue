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
    <LinePlotView v-if="this.displayedData" :displayedData="this.displayedData" v-on:selectedData="updateData">
    </LinePlotView>

    <h2>Cycle Plot</h2>
    <v-select
      v-model="this.selectedGranularity"
      label="Select Granularity:"
      :items="['Months-per-Year', 'Day-per-Week']"
    ></v-select>

    <CyclePlotView
      v-if="this.displayedData"
      :displayedData="this.displayedData"
      :granularity="this.selectedGranularity"
      :selectedData="this.selectedData"
    ></CyclePlotView>
  </div>
</template>

<script>
import LinePlotView from "./LinePlotView.vue";
import CyclePlotView from "./CyclePlotView.vue";
import CustomRangeSlider from './CustomRangeSlider.vue';
export default {
  components: { LinePlotView, CyclePlotView, CustomRangeSlider},
  data() {
    return {
      ticks: {},
      displayedRange: [0, 0],
      data: null,
      displayedData: null,
      selectedData: null,
      dataSize: 0,
      granularity: undefined,
      selectedGranularity:"",
    };
  },
  watch: {
    displayedRange: "sliceData",
  },
  computed: {},
  mounted() {
    this.retrieveData();
    this.checkGranularity();
  },
  methods: {
    updateData(selectedData) {
      console.log(selectedData)
      this.selectedData = selectedData;
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
      console.log(this.granularity)
    },
    updateRange(updatedRange){
      this.displayedRange = updatedRange
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
