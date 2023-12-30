<template>
  <div>
    <svg></svg>
  </div>
</template>

<script >
//TODO make slider double
import * as d3 from "d3";

export default {
  props: {
    displayedData: Object
  },
  data() {
    return {
      data: null,
      dataSize: 0,
    };
  },
  watch: {
    displayedData: "renderGraph",
  },
  methods: {
    renderGraph() {
      d3.select("svg").selectAll("*").remove();
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
  },
};
</script>
