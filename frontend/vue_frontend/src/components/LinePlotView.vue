<template>
  <div>
    <svg ref="linePlot"></svg>
  </div>
</template>

<script >
import * as d3 from "d3";

export default {
  props: {
    displayedData: Object,
    updatedGranularity: String,
  },
  data() {
    return {
      data: null,
      selectedData: undefined,
      dataSize: 0,
      selectedGranularity: null,
    };
  },
  watch: {
    displayedData: "renderGraph",
    updatedGranularity: "updateGranularity",
    selectedData: "sendSelectedData",
  },
  mounted() {},
  methods: {
    sendSelectedData() {
      console.log(this.selectedData);
    },
    updateGranularity(newGranularity) {
      if (newGranularity == "Hours") {
        this.data = this.displayedData;
        this.renderGraph();
      }
      if (newGranularity == "Months") {
        const aggregatedData = [];
        this.displayedData.forEach((el) => {
          var month = new Date(el.date).toLocaleDateString("default", {
            month: "short",
            year: "numeric",
          });
          if (!aggregatedData[month]) {
            // If not, initialize it with the current value
            aggregatedData[month] = {
              date: el.date,
              value: el.value,
              count: 1,
            };
          } else {
            // If it exists, add the current value to the existing value
            aggregatedData[month].value += el.value;
            aggregatedData[month].count += 1;
          }
        });
        Object.values(aggregatedData).forEach((val) => {
          val.value = val.value / val.count;
        });
        this.data = Object.values(aggregatedData);
        this.renderGraph();
      }
      if (newGranularity == "Days") {
        const aggregatedData = [];
        this.displayedData.forEach((el) => {
          var day = new Date(el.date).toLocaleDateString("default", {
            day: "numeric",
            month: "short",
            year: "numeric",
          });
          if (!aggregatedData[day]) {
            // If not, initialize it with the current value
            aggregatedData[day] = {
              date: el.date,
              value: el.value,
              count: 1,
            };
          } else {
            // If it exists, add the current value to the existing value
            aggregatedData[day].value += el.value;
            aggregatedData[day].count += 1;
          }
        });
        Object.values(aggregatedData).forEach((val) => {
          val.value = val.value / val.count;
        });
        this.data = Object.values(aggregatedData);
        this.renderGraph();
      }
    },
    renderGraph() {
      d3.select(this.$refs.linePlot).selectAll("*").remove();
      const width = 800;
      const height = 500;
      const padding = 50;

      const graphData = this.data == undefined ? this.displayedData : this.data;

      const svg = d3
        .select(this.$refs.linePlot)
        .attr("width", width)
        .attr("height", height);
      const g = svg
        .append("g")
        .attr("transform", "translate(" + padding + "," + padding + ")");

      const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");

      const x = d3
        .scaleTime()
        .domain(
          d3.extent(graphData, function (d) {
            return parseTime(d.date);
          })
        )
        .rangeRound([0, width - 2 * padding]);

      const y = d3
        .scaleLinear()
        .domain(
          d3.extent(graphData, function (d) {
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
        .datum(graphData)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", line);

      const brush = d3.brushX().on("brush", brushed);

      g.append("g").attr("transform", "scale(0.9,0.8)").call(brush);

      function brushed({ selection }) {
        if (selection) {
          console.log(graphData.filter((el)=>x(parseTime(el.date)) in d3.range(selection[0], selection[1])));
        }
      }
    },
  },
};
</script>
