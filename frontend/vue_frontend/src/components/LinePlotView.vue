<template>
  <div>
    <svg ref="linePlot"></svg>
  </div>
</template>

<script>
// Source: https://weeknumber.com/how-to/javascript

// Returns the ISO week of the date.
Date.prototype.getWeek = function () {
  var date = new Date(this.getTime());
  date.setHours(0, 0, 0, 0);
  // Thursday in current week decides the year.
  date.setDate(date.getDate() + 3 - ((date.getDay() + 6) % 7));
  // January 4 is always in week 1.
  var week1 = new Date(date.getFullYear(), 0, 4);
  // Adjust to Thursday in week 1 and count number of weeks from date to week1.
  return (
    1 +
    Math.round(
      ((date.getTime() - week1.getTime()) / 86400000 -
        3 +
        ((week1.getDay() + 6) % 7)) /
        7
    )
  );
};
import * as d3 from "d3";

export default {
  props: {
    displayedData: Object,
    updatedGranularity: String,
    highlightedData: Object,
  },
  data() {
    return {
      data: null,
      dataSize: 0,
      currentGranularity: null,
    };
  },
  watch: {
    displayedData: "updateData",
    highlightedData: "renderGraph",
    updatedGranularity: "updateGranularity",
  },
  mounted() { },
  methods: {
    updateData() {
      //aggregate new data according to selected granularity
      if(this.currentGranularity) {
        this.updateGranularity(this.currentGranularity);
      } else {
        this.renderGraph();
      }

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
        console.log(this.data)
        this.renderGraph();
      }
      if(newGranularity == "Weeks") {
        const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");
        const aggregatedData = [];
        this.displayedData.forEach((el) => {
          var year = new Date(el.date).toLocaleDateString("default", {
            year: "numeric",
          });
          var week = parseTime(el.date).getWeek() + year;
          if (!aggregatedData[week]) {
            // If not, initialize it with the current value
            aggregatedData[week] = {
              date: el.date,
              value: el.value,
              count: 1,
            };
          } else {
            // If it exists, add the current value to the existing value
            aggregatedData[week].value += el.value;
            aggregatedData[week].count += 1;
          }
        });
        Object.values(aggregatedData).forEach((val) => {
          val.value = val.value / val.count;
        });
        this.data = Object.values(aggregatedData);
        this.data.sort((a, b) => {
          return new Date(a.date) - new Date(b.date);
        });
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
        this.currentGranularity = newGranularity;
    },
    renderGraph() {
      d3.select(this.$refs.linePlot).selectAll("*").remove();
      const width = 1000;
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


      //draw highlighted points
      if (this.highlightedData) {
        g
          .selectAll("points")
          .data(this.highlightedData.values)
          .enter()
          .append("circle")
          .attr("cx", function (d) {
            return x(d.fullDate);
          })
          .attr("cy", function (d) {
            return y(d.value);
          })
          .attr("r", 3)
          .attr("fill", "red")
          .attr("stroke", "white");
      }

      const brush = d3.brushX().on("brush", brushed);

      g.append("g").attr("transform", "scale(0.9,0.8)").call(brush);

      const self = this;
      function brushed({ selection }) {
        clearTimeout(this.watcherTimeout);
        // Set a new timeout to debounce the watcher function after 300 milliseconds of inactivity
        this.watcherTimeout = setTimeout(() => {
        if (selection) {
          self.$emit(
            "selectedData",
            graphData.filter(
              (el) =>
                (x(parseTime(el.date)) >= selection[0] && x(parseTime(el.date)) <= selection[1])
            )
          );
        }
        }, 150);
      }
    },
  },
};
</script>
