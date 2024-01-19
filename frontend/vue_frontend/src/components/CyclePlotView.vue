<template>
  <div>
    <svg ref="cyclePlot"></svg>
  </div>
</template>

<script>
import * as d3 from "d3";

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

export default {
  props: {
    displayedData: Object,
    granularity: String,
    selectedData: Object,
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
    granularity: "groupData",
  },
  methods: {
    calculateHourDay() {
      var groups = [
        "00:00",
        "01:00",
        "02:00",
        "03:00",
        "04:00",
        "05:00",
        "06:00",
        "07:00",
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
        "22:00",
        "23:00",
        "24:00",
      ]
      const groupedData = {};
      const aggregatedData = [];
      const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");
      this.displayedData.forEach((entry) => {
        const date = parseTime(entry.date);
        const month = date.getMonth();
        const year = date.getFullYear();
        const day = new Intl.DateTimeFormat("en-US", {day: "numeric"}).format(
          date
        );
        const hour = new Intl.DateTimeFormat("en-US", {hour: "numeric", minute:"numeric", hour12:false}).format(
          date
        );
        const key = `${hour}-${day}-${month}-${year}`;

        if (!groupedData[key]) {
          groupedData[key] = {
            name: new Intl.DateTimeFormat("en-US", { hour: "numeric", minute:"numeric", hour12:false }).format(
              date
            ),
            category: hour,
            time: date,
            values: [],
            count: 0,
            sum: 0,
            fullDate: date,
          };
        }

        groupedData[key].count += 1;
        groupedData[key].sum += entry.value;
      });

      Object.values(groupedData).forEach((data) => {
        const average = data.sum / data.count;
        data.values.push(average);
      });

      groups.forEach((element) => {
        Object.entries(groupedData).forEach((entry) => {
          if (entry[1].name === element) {
            if (!(element in aggregatedData)) {
              aggregatedData[element] = {
                name: element,
                count: 1,
                average: entry[1].values[0],
                values: [
                  {
                    category: element,
                    time: entry[1].time,
                    value: entry[1].values[0],
                    fullDate: entry[1].fullDate,
                  },
                ],
              };
            } else {
              aggregatedData[element].average += entry[1].values[0];
              aggregatedData[element].count += 1;
              aggregatedData[element].values.push({
                category: entry[1].name,
                time: entry[1].time,
                value: entry[1].values[0],
                fullDate: entry[1].fullDate,
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
    calculateDayMonth() {
      var groups = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
      ]
      const groupedData = {};
      const aggregatedData = [];
      const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");
      this.displayedData.forEach((entry) => {
        const date = parseTime(entry.date);
        const month = date.getMonth();
        const year = date.getFullYear();
        const day = 
            new Intl.DateTimeFormat("en-US", { day: "numeric" }).format(
              date
            );

        const key = `${day}-${month}-${year}`;

        if (!groupedData[key]) {
          groupedData[key] = {
            name:  day,
            category: day,
            time: date,
            values: [],
            count: 0,
            sum: 0,
            fullDate: date,
          };
        }

        groupedData[key].count += 1;
        groupedData[key].sum += entry.value;
      });


      Object.values(groupedData).forEach((data) => {
        const average = data.sum / data.count;
        data.values.push(average);
      });

      groups.forEach((element) => {
        Object.entries(groupedData).forEach((entry) => {
          if (entry[1].name === element) {
            if (!(element in aggregatedData)) {
              aggregatedData[element] = {
                name: element,
                count: 1,
                average: entry[1].values[0],
                values: [
                  {
                    category: element,
                    time: entry[1].time,
                    value: entry[1].values[0],
                    fullDate: entry[1].fullDate,
                  },
                ],
              };
            } else {
              aggregatedData[element].average += entry[1].values[0];
              aggregatedData[element].count += 1;
              aggregatedData[element].values.push({
                category: entry[1].name,
                time: entry[1].time,
                value: entry[1].values[0],
                fullDate: entry[1].fullDate,
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
    calculateWeekMonth() {
      var groups = [
        "1",
        "2",
        "3",
        "4",
        "5",
      ];
      const groupedData = {};
      const aggregatedData = [];
      const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");
      this.displayedData.forEach((entry) => {
        const date = parseTime(entry.date);
        const month = date.getMonth();
        const week = date.getWeek();
        const year = date.getFullYear();
        const key = `${week}-${year}`;
        const day = 
            new Intl.DateTimeFormat("en-US", { day: "numeric" }).format(
              date
        );

        if (!groupedData[key]) {
          groupedData[key] = {
            name: Math.floor(day/7)+1,            
            category: Math.floor(day/7)+1,
            time: date,
            values: [],
            count: 0,
            sum: 0,
            fullDate: date,
          };
        }

        groupedData[key].count += 1;
        groupedData[key].sum += entry.value;
      });

      Object.values(groupedData).forEach((data) => {
        const average = data.sum / data.count;
        data.values.push(average);
      });

      groups.forEach((element) => {
        Object.entries(groupedData).forEach((entry) => {
          if (entry[1].name == element) {
            if (!(element in aggregatedData)) {
              aggregatedData[element] = {
                name: element,
                count: 1,
                average: entry[1].values[0],
                values: [
                  {
                    category: element.toString(),
                    time: entry[1].time,
                    value: entry[1].values[0],
                    fullDate: entry[1].fullDate,
                  },
                ],
              };
            } else {
              aggregatedData[element].average += entry[1].values[0];
              aggregatedData[element].count += 1;
              aggregatedData[element].values.push({
                category: entry[1].name.toString(),
                time: entry[1].time,
                value: entry[1].values[0],
                fullDate: entry[1].fullDate,
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
    calculateWeekYear() {
      var groups = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
        "32",
        "33",
        "34",
        "35",
        "36",
        "37",
        "38",
        "39",
        "40",
        "41",
        "42",
        "43",
        "44",
        "45",
        "46",
        "47",
        "49",
        "50",
        "51",
        "52",
        "53",
      ];
      const groupedData = {};
      const aggregatedData = [];
      const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");
      this.displayedData.forEach((entry) => {
        const date = parseTime(entry.date);
        const month = date.getMonth();
        const week = date.getWeek();
        const year = date.getFullYear();
        const key = `${week}-${year}`;
        const day = 
            new Intl.DateTimeFormat("en-US", { day: "numeric" }).format(
              date
        );

        if (!groupedData[key]) {
          groupedData[key] = {
            name: week,            
            category: week,
            time: date,
            values: [],
            count: 0,
            sum: 0,
            fullDate: date,
          };
        }

        groupedData[key].count += 1;
        groupedData[key].sum += entry.value;
      });

      Object.values(groupedData).forEach((data) => {
        const average = data.sum / data.count;
        data.values.push(average);
      });

      groups.forEach((element) => {
        Object.entries(groupedData).forEach((entry) => {
          if (entry[1].name == element) {
            if (!(element in aggregatedData)) {
              aggregatedData[element] = {
                name: element,
                count: 1,
                average: entry[1].values[0],
                values: [
                  {
                    category: element.toString(),
                    time: entry[1].time,
                    value: entry[1].values[0],
                    fullDate: entry[1].fullDate,
                  },
                ],
              };
            } else {
              aggregatedData[element].average += entry[1].values[0];
              aggregatedData[element].count += 1;
              aggregatedData[element].values.push({
                category: entry[1].name.toString(),
                time: entry[1].time,
                value: entry[1].values[0],
                fullDate: entry[1].fullDate,
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
      const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");
      this.displayedData.forEach((entry) => {
        const date = parseTime(entry.date);
        const month = date.getMonth();
        const year = date.getFullYear();
        const key = `${month}-${year}`;

        if (!groupedData[key]) {
          groupedData[key] = {
            name: new Intl.DateTimeFormat("en-US", { month: "long" }).format(
              date
            ),
            category: month,
            time: year,
            values: [],
            count: 0,
            sum: 0,
            fullDate: date,
          };
        }

        groupedData[key].count += 1;
        groupedData[key].sum += entry.value;
      });

      Object.values(groupedData).forEach((data) => {
        const average = data.sum / data.count;
        data.values.push(average);
      });

      groups.forEach((element) => {
        Object.entries(groupedData).forEach((entry) => {
          if (entry[1].name === element) {
            if (!(element in aggregatedData)) {
              aggregatedData[element] = {
                name: element,
                count: 1,
                average: entry[1].values[0],
                values: [
                  {
                    category: element,
                    time: entry[1].time,
                    value: entry[1].values[0],
                    fullDate: entry[1].fullDate,
                  },
                ],
              };
            } else {
              aggregatedData[element].average += entry[1].values[0];
              aggregatedData[element].count += 1;
              aggregatedData[element].values.push({
                category: entry[1].name,
                time: entry[1].time,
                value: entry[1].values[0],
                fullDate: entry[1].fullDate,
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
    calculateDayWeek() {
      //group data by Day per Week
      var groups = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
      ];
      const groupedData = {};
      const aggregatedData = [];
      const parseTime = d3.timeParse("%b %e, %Y, %I:%M:%S %p");
      this.displayedData.forEach((entry) => {
        const date = parseTime(entry.date);
        const day = date.getDay();
        const week = date.getWeek();
        const year = date.getFullYear();
        const key = `${day}-${week}-${year}`;

        if (!groupedData[key]) {
          groupedData[key] = {
            name: day,
            category: groups[day],
            time: date,
            values: [],
            count: 0,
            sum: 0,
            fullDate: date,
          };
        }

        groupedData[key].count += 1;
        groupedData[key].sum += entry.value;
      });
      Object.values(groupedData).forEach((dayData) => {
        const average = dayData.sum / dayData.count;
        dayData.values.push(average);
      });
      groups.forEach((day) => {
        Object.entries(groupedData).forEach((entry) => {
          if (entry[1].category === day) {
            if (!(day in aggregatedData)) {
              aggregatedData[day] = {
                name: day,
                count: 1,
                average: entry[1].values[0],
                values: [
                  {
                    category: day,
                    time: entry[1].time,
                    value: entry[1].values[0],
                    fullDate: entry[1].fullDate,
                  },
                ],
              };
            } else {
              aggregatedData[day].average += entry[1].values[0];
              aggregatedData[day].count += 1;
              aggregatedData[day].values.push({
                category: day,
                time: entry[1].time,
                value: entry[1].values[0],
                fullDate: entry[1].fullDate,
              });
            }
          }
        });
        //sort values by weeks
        aggregatedData[day].values.sort((a, b) => {
          return a.time - b.time;
        });
      });

      Object.values(aggregatedData).forEach((val) => {
        val.average = val.average / val.count;
      });
      return Object.values(aggregatedData);
    },
    groupData() {
      switch (this.granularity) {
        case "Months-per-Year":
          this.aggregatedData = this.calculateMonthYear();
          this.createCyclePlot();
          break;
        case "Days-per-Week":
          this.aggregatedData = this.calculateDayWeek();
          this.createCyclePlot();
          break;
        case "Hours-per-Day":
          this.aggregatedData = this.calculateHourDay();
          this.createCyclePlot();
          break;
        case "Days-per-Month":
          this.aggregatedData = this.calculateDayMonth();
          this.createCyclePlot();
          break;
        case "Weeks-per-Month":
          this.aggregatedData = this.calculateWeekMonth();
          this.createCyclePlot();
          break;
        case "Weeks-per-Year":
          this.aggregatedData = this.calculateWeekYear();
          this.createCyclePlot();
          break;
        default:
          d3.select(this.$refs.cyclePlot).selectAll("*").remove()
          break;
      }
    },
    createCyclePlot() {
      d3.select(this.$refs.cyclePlot).selectAll("*").remove();
      //radius of points
      const r = 3;
      const svg = d3
        .select(this.$refs.cyclePlot)
        .attr("width", this.width + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top + this.margin.bottom)
        .append("g")
        .append("g")
        .attr("transform", `translate(${this.margin.left},${this.margin.top})`)
        .attr("class", "zoomContainer");
      
      

      // Draw the y-axis
      const y = d3
        .scaleLinear()
        .range([this.height, 0])
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
      var dynamicWidth =
        this.aggregatedData[0].values.length * this.aggregatedData.length * 3< this.width
          ? this.width
          : (this.aggregatedData[0].values.length) * (this.aggregatedData.length*3);
      while((dynamicWidth /this.aggregatedData.length -r *2) < 142 ) {
        dynamicWidth += 100;
      }
      const xx = d3
        .scaleLinear()
        .range([r * 2, dynamicWidth / this.aggregatedData.length - r * 2])
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
        .range([0, dynamicWidth])
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

      svg
        .selectAll(".segments")
        .data(this.aggregatedData)
        .enter()
        .append("rect")
        .attr("class", "segments")
        .attr("x", function (d) {
          return x(d.name);
        })
        .attr("y", 0)
        .attr("width", x.bandwidth())
        .attr("height", this.height)
        .attr("stroke", "black")
        .attr("fill", "transparent");

      d3.selectAll(".segments").on("click", (event) => {
        this.$emit("highlightedData", event.target.__data__);
      });

      const zoom = d3.zoom().scaleExtent([1, 1]).on("zoom", zoomed);

      const self = this;
      function zoomed({ transform }) {
        transform.y = self.margin.top;
        d3.select(".zoomContainer").attr("transform", transform);
      }
      svg.call(zoom);
    },
  },
};
</script>

<style scoped>
/* Add your component styles here if needed */
</style>
