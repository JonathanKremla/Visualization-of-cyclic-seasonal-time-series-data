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
            category: month,
            time: year,
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
          if (entry[1].name === month) {
            if (!(month in aggregatedData)) {
              aggregatedData[month] = {
                name: month,
                count: 1,
                average: entry[1].values[0],
                values: [
                  {
                    category: month,
                    time: entry[1].time,
                    value: entry[1].values[0],
                  },
                ],
              };
            } else {
              aggregatedData[month].average += entry[1].values[0];
              aggregatedData[month].count += 1;
              aggregatedData[month].values.push({
                category: entry[1].name,
                time: entry[1].time,
                value: entry[1].values[0],
              });
            }
          }
        });
      });

      Object.values(aggregatedData).forEach((val) => {
        val.average = val.average / val.count;
      });

      return Object.values(aggregatedData);
    },
    groupData() {
      switch (this.granularity) {
        case "month-year":
          this.aggregatedData = this.calculateMonthYear();
          this.createCyclePlot();
          break;

        default:
          break;
      }
    },
    createCyclePlot() {
      d3.select(this.$refs.cyclePlot).selectAll("*").remove();
      console.log(this.aggregatedData);
      //radius of points
      const r = 3;
      const svg = d3
        .select(this.$refs.cyclePlot)
        .attr("width", this.width + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top + this.margin.bottom)
        .append("g")
        .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

      // Draw the y-axis
      const y = d3
        .scaleLinear()
        .range([this.height, 0])
        //TODO: Set domain dynamically
        .domain([
          Math.min(
            ...this.aggregatedData.flatMap((category) =>
              category.values.map((entry) => entry.value)
            )
          ),
          Math.max(
            ...this.aggregatedData.flatMap((category) =>
              category.values.map((entry) => entry.value)
            )
          ),
        ]);
      svg.append("g").call(d3.axisLeft(y));

      console.log();

      const xx = d3
        .scaleLinear()
        .range([r * 2, this.width / this.aggregatedData.length - r * 2])
        .domain([
          Math.min(
            ...this.aggregatedData.flatMap((category) =>
              category.values.map((entry) => entry.time)
            )
          ),
          Math.max(
            ...this.aggregatedData.flatMap((category) =>
              category.values.map((entry) => entry.time)
            )
          ),
        ]);

      // Draw the x-axis
      const x = d3
        .scaleBand()
        .range([0, this.width])
        .domain(this.aggregatedData.map((obj) => obj.name));
      svg
        .append("g")
        .attr("transform", "translate(0," + this.height + ")")
        .call(d3.axisBottom(x));

      // Draw lines
      var line = d3
        .line()
        .x(function (d) {
          return x(d.category) + xx(d.time);
        })
        .y(function (d) {
          return y(d.value);
        });
      svg
        .selectAll("myLines")
        .data(this.aggregatedData)
        .enter()
        .append("path")
        .attr("d", function (d) {
          return line(d.values);
        })
        .attr("stroke", "steelblue")
        .style("stroke-width", 2)
        .style("fill", "none");
      svg
        .selectAll(".month-lines")
        .data(this.aggregatedData)
        .enter()
        .append("line")
        .attr("class", "month-lines")
        .attr("x1", function (d) {
          return x(d.name) + x.bandwidth();
        })
        .attr("x2", function (d) {
          return x(d.name) + x.bandwidth();
        })
        .attr("y1", 0)
        .attr("y2", this.height)
        .attr("stroke", "lightgray")
        .attr("stroke-dasharray", "2");

      //draw dots
      svg
        .selectAll("myDots")
        .data(this.aggregatedData)
        .enter()
        .append("g")
        .style("fill", "black")
        .selectAll("myPoints")
        .data(function (d) {
          return d.values;
        })
        .enter()
        .append("circle")
        .attr("cx", function (d) {
          return x(d.category) + xx(d.time);
        })
        .attr("cy", function (d) {
          return y(d.value);
        })
        .attr("r", r)
        .attr("stroke", "white");
      // Draw horizontal lines at the average height for each month
      svg
        .selectAll(".average-lines")
        .data(this.aggregatedData)
        .enter()
        .append("line")
        .attr("class", "average-lines")
        .attr("x1", function (d) {
          return x(d.name);
        })
        .attr("x2", function (d) {
          return x(d.name) + x.bandwidth();
        })
        .attr("y1", function (d) {
          return y(d.average);
        })
        .attr("y2", function (d) {
          return y(d.average);
        })
        .attr("stroke", "red")
        .style("stroke-width", 2)
        .style("stroke-dasharray", "2");
    },
  },
};
</script>

<style scoped>
/* Add your component styles here if needed */
</style>
