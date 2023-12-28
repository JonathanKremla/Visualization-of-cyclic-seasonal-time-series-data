<template>
  <div>
    <router-link to="/">
      <button>Home</button>
    </router-link>
    <svg></svg>
  </div>
</template>

<script >
import * as d3 from "d3";
export default {
  data() {
    return {
      data: null,
    };
  },
  mounted() {
    // Retrieve data from local storage when the component is mounted
    this.retrieveData();
    this.renderGraph();
  },
  methods: {
    renderGraph() {
      console.log(this.data)

      const width = 800;
      const height = 500;

      const svg = d3.select("svg").attr("width", width).attr("height", height);
      const g = svg.append("g");

      //2. Parse the dates
      const parseTime = d3.timeParse("%b %e, %Y");
      //const parseTime = d3.timeParse("%d-%b-%y");

      //3. Creating the Chart Axes
      const x = d3
        .scaleTime()
        .domain(
          d3.extent(this.data, function (d) {
            return parseTime(d.date);
          })
        )
        .rangeRound([0, width]);
      console.log(x)

      const y = d3
        .scaleLinear()
        .domain(
          d3.extent(this.data, function (d) {
            return d.value;
          })
        )
        .rangeRound([height, 0]);

      const line = d3
        .line()
        .x(function (d) {
          return x(parseTime(d.date));
        })
        .y(function (d) {
          return y(d.value);
        });

      g.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

      g.append("g")
        .call(d3.axisLeft(y))
        .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")

      g.append("path")
        .datum(this.data)
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
      } catch (error) {
        console.error("Error retrieving data from local storage:", error);
      }
    },
  },
};
</script>
