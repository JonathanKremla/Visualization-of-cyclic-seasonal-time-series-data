<template>
  <div>
    <router-link to="/">
      <button>Home</button>
    </router-link>
    <v-range-slider
      v-model="this.displayedRange"
      step="30"
      show-ticks="always"
      :ticks="ticks"
      :max="this.dataSize"
      :min="0"
    ></v-range-slider>
    <LinePlotView v-if="this.displayedData" :displayedData="this.displayedData" >
    </LinePlotView>
    <CyclePlotView v-if="this.displayedData" :displayedData="this.displayedData" granularity='month-year'></CyclePlotView>
  </div>
</template>

<script>
import LinePlotView from "./LinePlotView.vue";
import CyclePlotView from "./CyclePlotView.vue";
export default {
  components: { LinePlotView, CyclePlotView },
  data() {
    return {
      ticks: {},
      displayedRange: [0, 0],
      data: null,
      displayedData: null,
      dataSize: 0,
    };
  },
  watch: {
    displayedRange: "sliceData",
  },
  computed: {},
  mounted() {
    this.retrieveData();
    this.calculateTicks();
  },
  methods: {
    sliceData() {
      if (this.displayedData !== null) {
        clearTimeout(this.watcherTimeout);
        // Set a new timeout to debounce the watcher function after 300 milliseconds of inactivity
        this.watcherTimeout = setTimeout(() => {
          this.displayedData = this.data.slice(
            this.displayedRange[0],
            this.displayedRange[1]
          );
        }, 100);
      }
    },
    retrieveData() {
      try {
        // Retrieve JSON string from local storage and parse it to a JavaScript object
        const jsonData = localStorage.getItem("data");
        const parsedData = JSON.parse(JSON.parse(jsonData));
        this.data = Object.entries(parsedData).map(([date, value]) => ({
          date: new Date(date).toLocaleDateString("en-US", {
            day: "numeric",
            month: "short",
            year: "numeric",
          }),
          value: parseFloat(value),
        }));
        this.displayedData = this.data;
        this.dataSize = this.data.length;
        this.displayedRange = [0, this.dataSize];
        console.log(this.data)
      } catch (error) {
        console.error("Error retrieving data from local storage:", error);
      }
    },
    calculateTicks() {
      const uniqueYears = [
        ...new Set(this.data.map((item) => new Date(item.date).getFullYear())),
      ];
      var counter = 0;
      uniqueYears.forEach((val) => {
        this.ticks[counter] = val;
        counter += 365;
      });
    },
  },
};
</script>
