<template>
  <div>
    <router-link to="/">
      <button>Home</button>
    </router-link>
    <v-range-slider
      v-model="this.displayedRange"
      step="30"
      show-ticks="always"
      :ticks = "ticks"
      :max="this.dataSize"
      :min=0
    ></v-range-slider>
    <svg></svg>
  </div>
</template>

<script >
//TODO make slider double
import * as d3 from "d3";

export default {
  components: {
  },
  data() {
    return {
      ticks: {},
      displayedRange: [0,0],
      data: null,
      displayedData: undefined,
      dataSize: 0,
    };
  },

  computed: {
    // Computed property to get the sliced data based on the slider value
    slicedData() {
      if (this.data !== null) {
        d3.select("svg").selectAll("*").remove();
        this.displayedData = this.data.slice(this.displayedRange[0], this.displayedRange[1]);
        return this.displayedData;
      }
      return [];
    },
  },
  mounted() {
    // Retrieve data from local storage when the component is mounted
    this.retrieveData();
    this.calculateTicks();
    this.renderGraph();
  },
  watch: {
    slicedData: "debouncedRenderGraph",
  },
  methods: {

    calculateTicks() {
      const uniqueYears = [...new Set(this.data.map(item => new Date(item.date).getFullYear()))];
      var counter = 0;
      uniqueYears.forEach((val) => {
        this.ticks[counter] = val;
        counter += 365;
      })
      console.log(this.ticks)

    },
    debouncedRenderGraph() {
      clearTimeout(this.watcherTimeout);

      // Set a new timeout to debounce the watcher function after 300 milliseconds of inactivity
      this.watcherTimeout = setTimeout(() => {
        this.renderGraph();
      }, 300);
    },
    renderGraph() {
      const width = 800;
      const height = 500;
      const padding = 50;

      const svg = d3.select("svg").attr("width", width).attr("height", height);
      const g = svg
        .append("g")
        .attr("transform", "translate(" + padding + "," + padding + ")");

      const parseTime = d3.timeParse("%b %e, %Y");

      const x = d3
        .scaleTime()
        .domain(
          d3.extent(this.displayedData, function (d) {
            return parseTime(d.date);
          })
        )
        .rangeRound([0, width - 2 * padding]);

      const y = d3
        .scaleLinear()
        .domain(
          d3.extent(this.displayedData, function (d) {
            return d.value;
          })
        )
        .rangeRound([height - 2 * padding, 0]);

      const line = d3
        .line()
        .x(function (d) {
          return x(parseTime(d.date));
        })
        .y(function (d) {
          return y(d.value);
        });

      g.append("g")
        .attr("transform", "translate(0," + (height - 2 * padding) + ")")
        .call(d3.axisBottom(x));

      g.append("g")
        .call(d3.axisLeft(y))
        .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6 - padding)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end");

      g.append("path")
        .datum(this.displayedData)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", line);
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
        this.displayedRange = [0,this.dataSize]
      } catch (error) {
        console.error("Error retrieving data from local storage:", error);
      }
    },
  },
};
</script>
