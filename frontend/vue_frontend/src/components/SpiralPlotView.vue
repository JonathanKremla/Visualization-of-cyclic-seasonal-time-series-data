<template>
  <div>
    <svg ref="legend"></svg>
    <svg ref="spiralPlot"></svg>
    <h3>Options:</h3>
    <div class="text-caption">Segments per Cycle</div>
    <v-container>
      <v-slider aria-label="Segments per Cycle" step="1" v-model="this.segmentsPerCycle" :max="this.displayedData.length"
        :disabled="this.recommendedSeg" min="1" thumb-label="always">
        <template v-slot:append>
          <v-text-field v-model="this.segmentsPerCycle" hide-details single-line density="compact" type="number"
            style="width: 100px"></v-text-field>
        </template>
      </v-slider>
      <v-checkbox label="Use recommended segments per cycle" v-model="this.recommendedSeg"></v-checkbox>
    </v-container>
    <div>
      <v-card flat>
        <v-card-text>
          <v-container fluid>
            <v-row>
              <v-col>
                <v-switch label="Highlight start of each year" v-model="this.options.yearHighlight" :disabled="this.options.granularity == 'Hours' ||
                  this.baseGranularity == 'Hours'
                  " color="primary"></v-switch>
                <v-switch label="Display text for year" v-model="this.options.yearText" :disabled="this.options.granularity == 'Hours' ||
                  this.baseGranularity == 'Hours'
                  " color="primary"></v-switch>
              </v-col>
              <v-col>
                <v-switch label="Highlight start of each month" v-model="this.options.monthHighlight"
                  :disabled="this.options.granularity == 'Months'" color="primary"></v-switch>
                <v-switch label="Display text for month" v-model="this.options.monthText"
                  :disabled="this.options.granularity == 'Months'" color="primary"></v-switch>
              </v-col>
              <v-col>
                <v-switch label="Highlight start of each day" v-model="this.options.dayHighlight"
                  :disabled="this.options.granularity != 'Hours'" color="primary"></v-switch>
                <v-switch label="Enable brushing / Disable zoom" v-model="this.zoomBrushToggle"
                  color="primary"></v-switch>
              </v-col>
              <v-col>
                <v-select label="Select color scheme" :items="['Cividis', 'Viridis', 'Inferno', 'Magma', 'Plasma']"
                  v-model="this.options.colorScheme"></v-select>
                <v-select label="Select granularity" :items="this.options.granularityItems"
                  v-model="this.options.granularity">
                </v-select>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";
import { toRaw } from "vue";

export default {
  props: {
    displayedData: Object,
    baseGranularity: String,
    selectedGranularity: String,
    highlightData: Object,
  },
  data() {
    return {
      //User defined options
      options: {
        yearHighlight: false,
        yearText: true,
        monthHighlight: false,
        monthText: true,
        dayHighlight: false,
        granularity: undefined,
        yearText: true,
        granularityItems: ["Hours", "Days", "Weeks", "Months"],
        colorScheme: "Cividis",
      },

      //Default segment per cycle count for each granularity
      defaults: {
        hours: 168,
        days: 365,
        months: 12,
        weeks: 53,
      },
      //Constants for spiral Plot
      spiralPlotConstants: {
        radians: 0.0174532925,
        cyclePadding: 1,
        radius: 400,
        innerRatio: 0.3,
        width: 800,
        height: 800,
        segmentAngle: undefined,
        innerRadius: undefined,
        segmentWidth: undefined,
      },
      margin: { top: 50, right: 50, bottom: 50, left: 50 },

      zoomBrushToggle: true,
      selectedData: [],
      recommendedSeg: true,
      segmentsPerCycle: undefined,
      data: null,
      dataSize: 0,
    };
  },
  watch: {
    options: {
      handler: "handleOptions",
      deep: true,
    },
    displayedData: "prepareData",
    segmentsPerCycle: {
      handler(newVal, oldVal) {
        if (oldVal !== undefined) {
          this.debounceOnSegmentChange();
        }
      },
    },
    zoomBrushToggle: "renderGraph",
    recommendedSeg: "setDefaultSegmentsPerCycle",
    selectedGranularity: "updateSelectedGranularity",
    highlightData: "updateHighlightedData",
    selectedData: "emitSelectedData",
  },
  mounted() {
    this.setGranularities();
    this.setDefaultSegmentsPerCycle();
  },
  methods: {
    emitSelectedData() {
      this.$emit("highlightedData", this.selectedData);
    },
    updateHighlightedData() {
      this.renderGraph();
      if (this.highlightData == undefined) {
        return;
      }
      var data = this.highlightData.values.map((item) => item.time.getTime());
      var arcs = d3.selectAll(".arc");
      var dataPoints = arcs
        .filter(function (d) {
          var date = new Date(`${d.month} ${d.day}, ${d.year} ${d.hour}:00:00`);
          return data.includes(date.getTime());
        })
        .raise();
      dataPoints
        .append("path")
        .attr("d", function (d) {
          let start = "M " + d.x1 + " " + d.y1;
          let side1 =
            " Q " +
            d.controlPoint1x +
            " " +
            d.controlPoint1y +
            " " +
            d.x2 +
            " " +
            d.y2;
          let side2 = "L " + d.x3 + " " + d.y3;
          let side3 =
            " Q " +
            d.controlPoint2x +
            " " +
            d.controlPoint2y +
            " " +
            d.x4 +
            " " +
            d.y4;
          return start + " " + side1 + " " + side2 + " " + side3 + " Z";
        })
        .style(
          "stroke",
          this.options.colorScheme == "Cividis" ||
            this.options.colorScheme == "Viridis"
            ? "red"
            : "green"
        )
        .style("fill", "none")
        .style("stroke-width", 2);
    },
    updateSelectedGranularity(newGranularity) {
      this.options.granularity = newGranularity;
    },
    sendUpdatdGranularity() {
      this.$emit("updateGranularity", this.options.granularity);
    },
    debounceOnSegmentChange() {
      clearTimeout(this.watcherTimeout);
      // Set a new timeout to debounce the watcher function after 300 milliseconds of inactivity
      this.watcherTimeout = setTimeout(() => {
        this.prepareData();
      }, 10);
    },
    setGranularities() {
      switch (this.baseGranularity) {
        case "Hours":
          this.options.granularityItems.pop();
          break;
        case "Days":
          this.options.granularityItems.shift();
          break;

        default:
          break;
      }
      this.options.granularity = this.baseGranularity;
    },
    handleOptions() {
      this.setDefaultSegmentsPerCycle();
      this.prepareData();
      this.sendUpdatdGranularity();
    },
    setDefaultSegmentsPerCycle() {
      switch (this.options.granularity) {
        case "Hours":
          this.segmentsPerCycle = this.defaults.hours;
          break;
        case "Days":
          this.segmentsPerCycle = this.defaults.days;
          break;
        case "Months":
          this.segmentsPerCycle = this.defaults.months;
          break;
        case "Weeks":
          this.segmentsPerCycle = this.defaults.weeks;
          break;
        default:
          break;
      }
    },
    aggregateData() {
      if (this.options.granularity == this.baseGranularity) {
        return this.displayedData;
      }
      if (this.options.granularity == "Months") {
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
        return Object.values(aggregatedData);
      }
      if (this.options.granularity == "Days") {
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
        return Object.values(aggregatedData);
      }
      if (this.options.granularity == "Weeks") {
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
        return Object.values(aggregatedData).sort((a, b) => {
          return new Date(a.date) - new Date(b.date);
        });
      }
    },

    prepareData() {
      const aggregatedData = this.aggregateData();
      if (
        (this.segmentsPerCycle == this.defaults.hour &&
          this.options.granularity == "Hours") ||
        (this.segmentsPerCycle == this.defaults.days &&
          this.options.granularity == "Days") ||
        (this.segmentsPerCycle == this.defaults.months &&
          this.options.granularity == "Months") ||
        (this.segmentsPerCycle == this.defaults.weeks &&
          this.options.granularity == "Weeks")
      ) {
        this.recommendedSeg = true;
      } else {
        this.recommendedSeg = false;
      }
      this.spiralPlotConstants.innerRadius =
        this.spiralPlotConstants.radius * this.spiralPlotConstants.innerRatio;
      this.spiralPlotConstants.segmentAngle = 360 / this.segmentsPerCycle;
      var cycles = Math.ceil(aggregatedData.length / this.segmentsPerCycle);
      this.spiralPlotConstants.segmentWidth =
        (this.spiralPlotConstants.radius *
          (1 - this.spiralPlotConstants.innerRatio)) /
        (cycles + 1);
      this.data = aggregatedData.map((entry) => {
        const { date, value, count } = entry;
        const parsedDate = new Date(date);
        const year = parsedDate.getFullYear();
        const month = parsedDate.getMonth() + 1; // Months are zero-based, so we add 1
        const day = parsedDate.getDate();
        const hour = parsedDate.getHours();

        return {
          year: year,
          month: month,
          day: day,
          hour: hour,
          value: value,
        };
      });
      this.data.sort(function (a, b) {
        return a.year - b.year || a.month - b.month;
      });
      this.renderGraph();
    },

    renderYearHighlights() {
      var arcs = d3.selectAll(".arc");

      var yearStarts = arcs
        .filter(function (d) {
          return d.month == 1 && d.day == 1;
        })
        .raise();
      if (this.options.yearHighlight) {
        yearStarts
          .append("path")
          .attr("d", function (d) {
            let start = "M " + d.x1 + " " + d.y1;
            let side1 =
              " Q " +
              d.controlPoint1x +
              " " +
              d.controlPoint1y +
              " " +
              d.x2 +
              " " +
              d.y2;
            let side2 = "L " + d.x3 + " " + d.y3;
            let side3 =
              " Q " +
              d.controlPoint2x +
              " " +
              d.controlPoint2y +
              " " +
              d.x4 +
              " " +
              d.y4;
            return start + " " + side1 + " " + side2 + " " + side3 + " Z";
          })
          .style(
            "stroke",
            this.options.colorScheme == "Cividis" ||
              this.options.colorScheme == "Viridis"
              ? "red"
              : "green"
          )
          .style("fill", "none")
          .style("stroke-width", 2);
      }

      if (this.options.yearText) {
        yearStarts
          .append("text")
          .attr("x", function (d) {
            return d.x1;
          })
          .attr("y", function (d) {
            return d.y1;
          })
          .text(function (d) {
            return d.year;
          })
          .style("font-size", "20px")
          .style(
            "fill",
            this.options.colorScheme == "Cividis" ||
              this.options.colorScheme == "Viridis"
              ? "red"
              : "green"
          );
      }
    },

    renderMonthHighlights() {
      var arcs = d3.selectAll(".arc");

      var baseGranularity = this.baseGranularity;
      var monthStarts = arcs
        .filter(function (d) {
          if (baseGranularity == "Hours") {
            return d.day == 1 && d.hour == 0;
          }
          return d.day == 1;
        })
        .raise();
      if (this.options.monthHighlight) {
        monthStarts
          .append("path")
          .attr("d", function (d) {
            let start = "M " + d.x1 + " " + d.y1;
            let side1 =
              " Q " +
              d.controlPoint1x +
              " " +
              d.controlPoint1y +
              " " +
              d.x2 +
              " " +
              d.y2;
            let side2 = "L " + d.x3 + " " + d.y3;
            let side3 =
              " Q " +
              d.controlPoint2x +
              " " +
              d.controlPoint2y +
              " " +
              d.x4 +
              " " +
              d.y4;
            return start + " " + side1 + " " + side2 + " " + side3 + " Z";
          })
          .style(
            "stroke",
            this.options.colorScheme == "Cividis" ||
              this.options.colorScheme == "Viridis"
              ? "red"
              : "green"
          )
          .style("fill", "none")
          .style("stroke-width", 2);
      }

      if (this.options.monthText) {
        var yearTextDisplayed = this.options.yearText;
        monthStarts
          .append("text")
          .attr("x", function (d) {
            return d.x1;
          })
          .attr("y", function (d) {
            return d.y1;
          })
          .text(function (d) {
            if (!(d.month == 1 && yearTextDisplayed)) {
              return months[d.month - 1];
            }
          })
          .style("font-size", "15px")
          .style(
            "fill",
            this.options.colorScheme == "Cividis" ||
              this.options.colorScheme == "Viridis"
              ? "red"
              : "green"
          );
      }
    },

    renderDayHighlights() {
      var arcs = d3.selectAll(".arc");

      var dayStarts = arcs
        .filter(function (d) {
          return d.hour == 0;
        })
        .raise();

      if (this.options.dayHighlight) {
        dayStarts
          .append("path")
          .attr("d", function (d) {
            let start = "M " + d.x1 + " " + d.y1;
            let side1 =
              " Q " +
              d.controlPoint1x +
              " " +
              d.controlPoint1y +
              " " +
              d.x2 +
              " " +
              d.y2;
            let side2 = "L " + d.x3 + " " + d.y3;
            let side3 =
              " Q " +
              d.controlPoint2x +
              " " +
              d.controlPoint2y +
              " " +
              d.x4 +
              " " +
              d.y4;
            return start + " " + side1 + " " + side2 + " " + side3 + " Z";
          })
          .style(
            "stroke",
            this.options.colorScheme == "Cividis" ||
              this.options.colorScheme == "Viridis"
              ? "red"
              : "green"
          )
          .style("fill", "none")
          .style("stroke-width", 2);
      }
    },

    renderGraph() {
      this.selectedData = null;
      d3.select(this.$refs.spiralPlot).selectAll("*").remove();
      var c = `d3.interpolate${this.options.colorScheme}`;
      var color = d3.scaleSequential(eval(c));
      var radians = this.spiralPlotConstants.radians;
      const svg = d3
        .select(this.$refs.spiralPlot)
        .attr(
          "width",
          this.spiralPlotConstants.width + this.margin.left + this.margin.right
        )
        .attr(
          "height",
          this.spiralPlotConstants.height + this.margin.top + this.margin.bottom
        );

      const g = svg
        .append("g")
        .attr(
          "transform",
          "translate(" +
          (this.margin.left + this.spiralPlotConstants.radius) +
          "," +
          (this.margin.top + this.spiralPlotConstants.radius) +
          ")"
        );

      const x = function (angle, radius) {
        //change to clockwise
        let a = 360 - angle;
        //start from 12 o'clock
        a = a + 180;
        return radius * Math.sin(a * radians);
      };

      const y = function (angle, radius) {
        //change to clockwise
        let a = 360 - angle;
        //start from 12 o'clock
        a = a + 180;
        return radius * Math.cos(a * radians);
      };

      var dataExtent = d3.extent(this.data, function (d) {
        return d.value;
      });
      color.domain(dataExtent);

      var infoBox = d3
        .select("body")
        .append("div")
        .attr("class", "infoBox")
        .style("opacity", 0);

      this.data.forEach((d, i) => {
        var segment = Math.floor(i / this.segmentsPerCycle);
        var position = i - segment * this.segmentsPerCycle;
        //console.log("position: " + position)

        var startAngle = position * this.spiralPlotConstants.segmentAngle;
        var endAngle = (position + 1) * this.spiralPlotConstants.segmentAngle;
        //console.log("angles: " + startAngle +", " + endAngle)

        var startInnerRadius =
          this.spiralPlotConstants.cyclePadding +
          this.spiralPlotConstants.innerRadius +
          (i / this.segmentsPerCycle) * this.spiralPlotConstants.segmentWidth;
        var startOuterRadius =
          this.spiralPlotConstants.innerRadius +
          (i / this.segmentsPerCycle) * this.spiralPlotConstants.segmentWidth +
          this.spiralPlotConstants.segmentWidth;
        var endInnerRadius =
          this.spiralPlotConstants.cyclePadding +
          this.spiralPlotConstants.innerRadius +
          ((i + 1) / this.segmentsPerCycle) *
          this.spiralPlotConstants.segmentWidth;
        var endOuterRadius =
          this.spiralPlotConstants.innerRadius +
          ((i + 1) / this.segmentsPerCycle) *
          this.spiralPlotConstants.segmentWidth +
          this.spiralPlotConstants.segmentWidth;

        //console.log("Radi: " + startInnerRadius + ", " + startOuterRadius + ", " + endInnerRadius + ", " + endOuterRadius)
        //set vertices
        d.x1 = x(startAngle, startInnerRadius);
        d.y1 = y(startAngle, startInnerRadius);

        d.x2 = x(endAngle, endInnerRadius);
        d.y2 = y(endAngle, endInnerRadius);

        d.x3 = x(endAngle, endOuterRadius);
        d.y3 = y(endAngle, endOuterRadius);

        d.x4 = x(startAngle, startOuterRadius);
        d.y4 = y(startAngle, startOuterRadius);

        let midAngle = startAngle + this.spiralPlotConstants.segmentAngle / 2;
        let midInnerRadius =
          this.spiralPlotConstants.innerRadius +
          this.spiralPlotConstants.cyclePadding +
          ((i + 0.5) / this.segmentsPerCycle) *
          this.spiralPlotConstants.segmentWidth;
        let midOuterRadius =
          this.spiralPlotConstants.innerRadius +
          ((i + 0.5) / this.segmentsPerCycle) *
          this.spiralPlotConstants.segmentWidth +
          this.spiralPlotConstants.segmentWidth;

        d.mid1x = x(midAngle, midInnerRadius);
        d.mid1y = y(midAngle, midInnerRadius);

        d.mid2x = x(midAngle, midOuterRadius);
        d.mid2y = y(midAngle, midOuterRadius);

        //quadratic Bézier formula
        d.controlPoint1x = (d.mid1x - 0.25 * d.x1 - 0.25 * d.x2) / 0.5;
        d.controlPoint1y = (d.mid1y - 0.25 * d.y1 - 0.25 * d.y2) / 0.5;

        d.controlPoint2x = (d.mid2x - 0.25 * d.x3 - 0.25 * d.x4) / 0.5;
        d.controlPoint2y = (d.mid2y - 0.25 * d.y3 - 0.25 * d.y4) / 0.5;
      });
      var arcs = g
        .selectAll(".arc")
        .data(this.data)
        .enter()
        .append("g")
        .attr("class", "arc");

      arcs
        .append("path")
        .attr("d", function (d) {
          let start = "M " + d.x1 + " " + d.y1;
          let side1 =
            " Q " +
            d.controlPoint1x +
            " " +
            d.controlPoint1y +
            " " +
            d.x2 +
            " " +
            d.y2;
          let side2 = "L " + d.x3 + " " + d.y3;
          let side3 =
            " Q " +
            d.controlPoint2x +
            " " +
            d.controlPoint2y +
            " " +
            d.x4 +
            " " +
            d.y4;
          return start + " " + side1 + " " + side2 + " " + side3 + " Z";
        })
        .style("fill", function (d) {
          return color(d.value);
        })
        .on("mouseover", function (d, i) {
          d3.select(this).transition().duration("50").attr("opacity", ".5");
        })
        .on("mouseout", function (d, i) {
          infoBox.html("").style("opacity", 0);
          d3.select(this).transition().duration("50").attr("opacity", "1");
        })
        .on("click", function (event) {
          var data = event.originalTarget.__data__;
          infoBox.transition().duration(50).style("opacity", 1);
          infoBox
            .html(
              `value: ${Math.round(data.value * 100) / 100} <br> date: ${data.day
              }.${data.month}.${data.year}`
            )
            .style("left", event.pageX + 10 + "px")
            .style("top", event.pageY - 15 + "px")
            .style("color", "black");

          var currEl = d3.select(this)._groups[0].map((d) => {
            var date = new Date(
              d.__data__.year,
              d.__data__.month - 1,
              d.__data__.day,
              d.__data__.hour,
              0,
              0
            );
            return {
              fullDate: date,
              value: d.__data__.value,
            };
          });
          var isInSelection = self.selectedData.some(
            (el) => el.fullDate.getTime() == currEl[0].fullDate.getTime()
          );
          if (isInSelection) {
            if (event.metaKey || event.ctrlKey) {
              var timeDiff = (Math.abs(self.selectedData[self.selectedData.length - 1].fullDate.getTime() - self.selectedData[self.selectedData.length - 2].fullDate.getTime()))
              var temp = []
              var found = false
              for (let index = 0; index < self.selectedData.length - 1; index++) {
                temp.push(self.selectedData[index])
                if(index == self.selectedData.length-2) {
                  temp.push(self.selectedData[index+1])
                }
                if (self.selectedData[index].fullDate.getTime() == currEl[0].fullDate.getTime()) {
                  found = true;
                }
                if (Math.abs(self.selectedData[index].fullDate.getTime() - self.selectedData[index + 1].fullDate.getTime()) > timeDiff) {
                  if (found) {
                    break;
                  }
                  temp = []
                }
              }


              var temp = temp.map((d) => d.fullDate.getTime());
              var t = arcs
                .filter(function (d) {
                  var date = new Date(`${d.month} ${d.day}, ${d.year} ${d.hour}:00:00`);
                  return temp.includes(date.getTime());
                })
              t.attr("opacity","1")
              var updated = self.selectedData.filter((d) => {
                return !temp.includes(d.fullDate.getTime())
              })
              self.selectedData = updated;
            } else {
              d3.select(this.parentNode).attr("opacity", "1")
              const updated = self.selectedData.filter(
                (el) => el.fullDate.getTime() != currEl[0].fullDate.getTime()
              );
              self.selectedData = updated;
            }
          }
          if (!isInSelection) {
            //deep copy to trigger watcher
            const updated = [];
            self.selectedData.forEach((el) => {
              updated.push(el);
            });
            updated.push(currEl[0]);
            self.selectedData = updated;
            d3.select(this.parentNode).attr("opacity", "0.5")
          }
        });

      this.renderYearHighlights();
      this.renderMonthHighlights();
      this.renderDayHighlights();

      //create Legend
      var legendWidth = this.spiralPlotConstants.width / 2;
      var legendHeight = 30;

      d3.select(this.$refs.legend).selectAll("*").remove();
      var legend = d3
        .select(this.$refs.legend)
        .attr("class", "legend")
        .attr("width", legendWidth)
        .attr("height", legendHeight * 2);

      var lg = legend.append("g");

      var colorRange = [];
      for (let index = dataExtent[0]; index < dataExtent[1]; index++) {
        colorRange.push(color(index));
      }

      const colorScale = d3
        .scaleLinear()
        .domain(
          d3.extent(this.data, function (d) {
            return d.value;
          })
        )
        .range([0, legendWidth]);

      // Create linear gradient
      lg.append("defs")
        .append("linearGradient")
        .attr("id", "colorGradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .selectAll("stop")
        .data(colorRange)
        .enter()
        .append("stop")
        .attr("offset", function (d, i) {
          return i / (colorRange.length - 1);
        })
        .attr("stop-color", function (d) {
          return d;
        });

      // Create legend rectangle with gradient
      lg.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#colorGradient)");

      var tickValues = d3.range(dataExtent[0], dataExtent[1] + 1, 10);
      var tickScale = d3
        .scaleLinear()
        .domain(dataExtent)
        .range([0, legendWidth]);

      lg.selectAll(".tick")
        .data(tickValues)
        .enter()
        .append("line")
        .attr("class", "tick")
        .attr("x1", function (d) {
          return tickScale(d);
        })
        .attr("x2", function (d) {
          return tickScale(d);
        })
        .attr("y1", 0)
        .attr("y2", legendHeight + 5);

      // Add tick labels
      lg.selectAll(".tick-label")
        .data(tickValues)
        .enter()
        .append("text")
        .attr("class", "tick-label")
        .attr("x", function (d) {
          return tickScale(d);
        })
        .attr("y", legendHeight + 15)
        .text(function (d) {
          return Math.round(d); // Display tick values as labels
        });

      // Add brush for legend
      const brush = d3.brushX().on("brush", brushed);
      lg.append("g").attr("transform", "scale(1, 0.5)").call(brush);
      const self = this;

      function brushed({ selection }) {
        clearTimeout(this.watcherTimeout);
        this.watcherTimeout = setTimeout(() => {
          //remove previous paths
          d3.select(self.$refs.spiralPlot).selectAll("path").remove();
          arcs
            .append("path")
            .attr("d", function (d) {
              let start = "M " + d.x1 + " " + d.y1;
              let side1 =
                " Q " +
                d.controlPoint1x +
                " " +
                d.controlPoint1y +
                " " +
                d.x2 +
                " " +
                d.y2;
              let side2 = "L " + d.x3 + " " + d.y3;
              let side3 =
                " Q " +
                d.controlPoint2x +
                " " +
                d.controlPoint2y +
                " " +
                d.x4 +
                " " +
                d.y4;
              return start + " " + side1 + " " + side2 + " " + side3 + " Z";
            })
            .style("fill", function (d) {
              if (
                d.value < colorScale.invert(selection[0]) ||
                d.value > colorScale.invert(selection[1])
              ) {
                return "white";
              }
              return color(d.value);
            })
            .on("mouseover", function (d, i) {
              d3.select(this).transition().duration("50").attr("opacity", ".5");
            })
            .on("mouseout", function (d, i) {
              d3.select(this).transition().duration("50").attr("opacity", "1");
              infoBox.html("").style("opacity", 0);
            })
            .on("click", function (event) {
              var data = event.originalTarget.__data__;
              infoBox.transition().duration(50).style("opacity", 1);
              infoBox
                .html(
                  `value: ${Math.round(data.value * 100) / 100} <br> date: ${data.day
                  }.${data.month}.${data.year}`
                )
                .style("left", event.pageX + 10 + "px")
                .style("top", event.pageY - 15 + "px")
                .style("color", "black");
              d3.select(this).attr("opacity", "1");
            });
        }, 300);
      }

      function updateSelected(action) {
        arcs.attr("opacity", "1");
        var offset = self.margin.top + self.spiralPlotConstants.radius;
        draggedPoints.push([offset, offset]);
        var hullPoints = d3.polygonHull(draggedPoints);
        var selectedData = arcs.filter(function (d) {
          return d3.polygonContains(hullPoints, [
            offset + d.mid1x,
            offset + d.mid1y,
          ]);
        });
        selectedData.attr("opacity", "0.5");
        var transformed = selectedData._groups[0].map((d) => {
          var date = new Date(
            d.__data__.year,
            d.__data__.month - 1,
            d.__data__.day,
            d.__data__.hour,
            0,
            0
          );
          return {
            fullDate: date,
            value: d.__data__.value,
          };
        });
        self.selectedData = transformed;
      }

      var yOffset = -70;
      var draggedPoints = [[450, 450]];
      var selectionLine1 = svg.append('line')
        .style("stroke", "black")
        .style("stroke-width", 1)
        .attr("x1", 450)
        .attr("y1", 450)
        .attr("x2", 450)
        .attr("y2", 450)
        .on("mouseover", function (d) {
          d3.select(this).transition().duration("50").attr("opacity", "0.5");
          d3.select(this).style("stroke-width", 5);
        })
        .on("mouseout", function (d) {
          d3.select(this).transition().duration("50").attr("opacity", "1");
          d3.select(this).style("stroke-width", 1);
        }).call(addLineDrag1());


      function addLineDrag1() {
        function dragstart(event) {
        }
        function dragged(event) {
          var offset = self.margin.top + self.spiralPlotConstants.radius;
          var hullPoints = d3.polygonHull(draggedPoints);
          d3.select(this).attr("x2", event.x).attr("y2", event.y).on("mouseover", null)
          var contains = d3.polygonContains(hullPoints, [
            event.x,
            event.y,
          ]);
          //we are decreasing the selected area
          if (contains) {
            const angleA = Math.atan2(selectionLine2.attr("y2") - 450, selectionLine2.attr("x2") - 450);
            const angleB = Math.atan2(selectionLine1.attr("y2") - 450, selectionLine1.attr("x2") - 450);
            const angleMid = (angleA + angleB) / 2;

            // Calculate the midpoint coordinates using polar to Cartesian conversion
            const midX = 450 + 1000 * Math.cos(angleMid);
            const midY = 450 + 1000 * Math.sin(angleMid);
            var hp = d3.polygonHull([[450, 450], [selectionLine2.attr("x2"), selectionLine2.attr("y2")], [midX, midY], [event.x, event.y]])
            draggedPoints = draggedPoints.filter(el => {
              return d3.polygonContains(hp, el)
            })
          }
          //we are increasing the selected area
          if (!contains) {
            draggedPoints.push([event.x, event.y])
          }
          updateSelected();

        }
        function dragended(event) {
          draggedPoints.push([event.x, event.y])
          updateSelected();
          selectionLine1.attr("x2", 450).attr("y2", 450)
          selectionLine1 = svg.append('line')
            .style("stroke", "black")
            .style("stroke-width", 1)
            .attr("x1", 450)
            .attr("y1", 450)
            .attr("x2", event.x)
            .attr("y2", event.y)
            .attr("class", "selectionLine1")
            .on("mouseover", function (d) {
              d3.select(this).transition().duration("50").attr("opacity", "0.5");
              d3.select(this).style("stroke-width", 5);
            })
            .on("mouseout", function (d) {
              d3.select(this).transition().duration("50").attr("opacity", "1");
              d3.select(this).style("stroke-width", 1);
            }).call(addLineDrag1());
        }
        return d3
          .drag()
          .on("start", dragstart)
          .on("drag", dragged)
          .on("end", dragended);
      }

      var selectionLine2 = svg.append('line')
        .style("stroke", "black")
        .style("stroke-width", 1)
        .attr("x1", 450)
        .attr("y1", 450)
        .attr("x2", 450)
        .attr("y2", 450)
        .attr("class", "selectionLine2");


      function addLineDrag2() {
        function dragstart(event) {
        }
        function dragged(event) {
          var offset = self.margin.top + self.spiralPlotConstants.radius;
          var hullPoints = d3.polygonHull(draggedPoints);
          d3.select(this).attr("x2", event.x).attr("y2", event.y).on("mouseover", null)
          var contains = d3.polygonContains(hullPoints, [
            event.x,
            event.y,
          ]);
          //we are decreasing the selected area
          if (contains) {
            const angleA = Math.atan2(selectionLine2.attr("y2") - 450, selectionLine2.attr("x2") - 450);
            const angleB = Math.atan2(selectionLine1.attr("y2") - 450, selectionLine1.attr("x2") - 450);
            const angleMid = (angleA + angleB) / 2;

            //create a point which is "infinitely far" away
            const midX = 450 + 10000 * Math.cos(angleMid);
            const midY = 450 + 10000 * Math.sin(angleMid);
            var hp = d3.polygonHull([[450, 450], [selectionLine1.attr("x2"), selectionLine1.attr("y2")], [midX, midY], [event.x, event.y]])
            draggedPoints = draggedPoints.filter(el => {
              return d3.polygonContains(hp, el)
            })
          }
          //we are increasing the selected area
          if (!contains) {
            draggedPoints.push([event.x, event.y])
          }
          updateSelected();

        }
        function dragended(event) {
          draggedPoints.push([event.x, event.y])
          updateSelected();
          selectionLine2.attr("x2", 450).attr("y2", 450)
          selectionLine2 = svg.append('line')
            .style("stroke", "black")
            .style("stroke-width", 1)
            .attr("x1", 450)
            .attr("y1", 450)
            .attr("x2", event.x)
            .attr("y2", event.y)
            .attr("class", "selectionLine2")
            .on("mouseover", function (d) {
              d3.select(this).transition().duration("50").attr("opacity", "0.5");
              d3.select(this).style("stroke-width", 5);
            })
            .on("mouseout", function (d) {
              d3.select(this).transition().duration("50").attr("opacity", "1");
              d3.select(this).style("stroke-width", 1);
            }).call(addLineDrag2());

        }
        return d3
          .drag()
          .on("start", dragstart)
          .on("drag", dragged)
          .on("end", dragended);
      }
      function addDrag() {
        function dragstart(event) {
          if (event.sourceEvent.shiftKey) {
            selectionLine1.attr("x2", event.x).attr("y2", event.y + yOffset)
            selectionLine2.attr("x2", 450).attr("y2", 450)
            draggedPoints = [[450, 450]];
            draggedPoints.push([event.x, event.y + yOffset]);
            draw("start");
          }
        }
        function dragged(event) {
          if (event.sourceEvent.shiftKey) {
            draggedPoints.push([event.x, event.y + yOffset]);
            draw("");
          }
        }
        function dragended(event) {
          if (event.sourceEvent.shiftKey) {
            draggedPoints.push([event.x, event.y + yOffset]);
            selectionLine2.attr("x2", 450).attr("y2", 450)
            selectionLine2 = svg.append('line')
              .style("stroke", "black")
              .style("stroke-width", 1)
              .attr("x1", 450)
              .attr("y1", 450)
              .attr("x2", event.x)
              .attr("y2", event.y + yOffset)
              .attr("class", "selectionLine2")
              .on("mouseover", function (d) {
                d3.select(this).transition().duration("50").attr("opacity", "0.5");
                d3.select(this).style("stroke-width", "5");
              })
              .on("mouseout", function (d) {
                d3.select(this).transition().duration("50").attr("opacity", "1");
                d3.select(this).style("stroke-width", "1");
              }).call(addLineDrag2());

            updateSelected();
          }
        }

        function draw(status) {
          if (status == "start") {
            selectionLine2 = svg.append('line')
              .style("stroke", "black")
              .style("stroke-width", 1)
              .attr("x1", 450)
              .attr("y1", 450)
              .attr("x2", draggedPoints[draggedPoints.length - 1][0])
              .attr("y2", draggedPoints[draggedPoints.length - 1][1]);
          } else {
            selectionLine2
              .attr("x2", draggedPoints[draggedPoints.length - 1][0])
              .attr("y2", draggedPoints[draggedPoints.length - 1][1])

          }
        }
        return d3
          .drag()
          .on("start", dragstart)
          .on("drag", dragged)
          .on("end", dragended);
      }

      const zoom = d3.zoom().scaleExtent([1, 5]).on("zoom", zoomed);
      function zoomed({ transform }) {
        g.attr("transform", transform);
      }
      if (!this.zoomBrushToggle) {
        svg.on("mousedown.drag", null);
        svg.call(zoom);
      } else {
        svg.on("mousedown.zoom", null);
        svg.call(addDrag());
      }
    },
  },
};
const months = [
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
</script>
<style>
div.infoBox {
  position: absolute;
  text-align: center;
  padding: 0.5rem;
  background: #ffffff;
  color: #313639;
  border: 1px solid #313639;
  border-radius: 8px;
  pointer-events: none;
  font-size: 1rem;
}
</style>
