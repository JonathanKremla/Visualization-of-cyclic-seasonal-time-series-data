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
      console.log(this.displayedData);
      //group data by months per year
      var groups = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
      ];
      const groupedData = {};
      const aggregatedData = [];
      this.displayedData.forEach((entry) => {
        const date = new Date(entry.date);
        const month = date.getMonth();
        const year = date.getFullYear();
        const monthYearKey = `${month}-${year}`;

        if (!groupedData[monthYearKey]) {
          groupedData[monthYearKey] = {
            name: new Intl.DateTimeFormat("en-US", { month: "long" }).format(
              date
            ),
            values: [],
            count: 0,
            sum: 0,
          };
        }

        groupedData[monthYearKey].count += 1;
        groupedData[monthYearKey].sum += entry.value;
      });

      // Calculate averages and store in the values array
      Object.values(groupedData).forEach((monthData) => {
        const average = monthData.sum / monthData.count;
        monthData.values.push(average);
      });

      groups.forEach((month) => {
        Object.entries(groupedData).forEach((entry) => {
          console.log(entry)
          if(entry[1].name === month) {
            if(!(month in aggregatedData)){
              aggregatedData[month] = {
                name: month,
                values: entry[1].values
              }
            } else {
              aggregatedData[month].values.push(entry[1].values[0])
            }
          }
        })
      })
      return Object.values(aggregatedData);
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

      //TODO: For each month, group the values ignore the year -> January: 20,21... and so on.

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
