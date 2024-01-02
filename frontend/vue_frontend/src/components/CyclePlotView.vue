<template>
  <div>
    <h2>Cycle Plot Example</h2>
    <svg ref="cyclePlot"></svg>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  props: {
    displayedData: Object,
    granularity: String,
  },
  data() {
    return {
      data: null,
      aggregatedData: null,
      dataSize: 0,
      margin: { top: 50, right: 50, bottom: 50, left: 50 },
      width: 1000,
      height: 500,
    };
  },
  watch: {
    displayedData: "groupData",
  },
  methods: {
    calculateMonthYear() {
      const groupedData = {};
      const aggregatedData = {};

      this.displayedData.forEach((entry) => {
        const date = new Date(entry.date);
        const monthYear = `${date.getMonth() + 1}-${date.getFullYear()}`;
        if (!groupedData[monthYear]) {
          groupedData[monthYear] = {
            entries: [],
            sum: 0,
            count: 0,
          };
        }

        groupedData[monthYear].entries.push(entry);
        groupedData[monthYear].sum += entry.value;
        groupedData[monthYear].count += 1;
      });
      for (var [monthYear, data] of Object.entries(groupedData)) {
        aggregatedData[monthYear] = data.sum / data.count;
      }

      var tmp = Object.entries(aggregatedData).map(function ([time, value]) {
        return { time: time, value: value };
      });
      return tmp.sort((a, b) => {
        const [aMonth, aYear] = a.time.split("-");
        const [bMonth, bYear] = b.time.split("-");
        return aMonth - bMonth || aYear - bYear;
      });
    },
    groupData() {
      console.log(this.granularity);
      switch (this.granularity) {
        case "month-year":
          this.aggregatedData = this.calculateMonthYear();
          console.log(this.aggregatedData);
          this.createCyclePlot();
          break;

        default:
          break;
      }
    },
    createCyclePlot() {
      const svg = d3
        .select(this.$refs.cyclePlot)
        .attr("width", this.width + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top + this.margin.bottom)
        .append("g")
        .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

      const x = d3
        .scaleBand()
        .range([0, this.width])
        .domain(this.aggregatedData.map((obj) => obj.time));
      console.log(x("February"));

      const y = d3
        .scaleLinear()
        .range([this.height, 0])
        .domain([0, d3.max(this.aggregatedData, (d) => d.value)]);

      // Draw the x-axis
      svg
        .append("g")
        .attr("transform", "translate(0," + this.height + ")")
        .call(d3.axisBottom(x));
      //

      // Draw the y-axis
      svg.append("g").call(d3.axisLeft(y));

      svg
        .append("path")
        .datum(this.aggregatedData)
        .attr("fill", "none")
        .attr("stroke", "#69b3a2")
        .attr("stroke-width", 1.5)
        .attr(
          "d",
          d3
            .line()
            .x((d) => x(d.time)) // Adjust for the center of the band
            .y((d) => y(d.value))
        );

      svg
        .append("g")
        .selectAll("dot")
        .data(this.aggregatedData)
        .enter()
        .append("circle")
        .attr("cx", function (d) {
          return x(d.time);
        })
        .attr("cy", function (d) {
          return y(d.value);
        })
        .attr("r", 1.5)
        .style("fill", "#69b3a2");
    },
  },
};
</script>

<style scoped>
/* Add your component styles here if needed */
</style>
