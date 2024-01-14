<template>
  <div>
    <h3>Options:</h3>
    <div class="text-caption">Segments per Cycle</div>
    <v-container>
      <v-slider
        aria-label="Segments per Cycle"
        step="1"
        v-model="this.segmentsPerCycle"
        :max="this.displayedData.length"
        :disabled="this.recommendedSeg"
        min="1"
        thumb-label="always"
      >
        <template v-slot:append>
          <v-text-field
            v-model="this.segmentsPerCycle"
            hide-details
            single-line
            density="compact"
            type="number"
            style="width: 100px"
          ></v-text-field>
        </template>
      </v-slider>
      <v-checkbox
        label="Use recommended segments per cycle"
        v-model="this.recommendedSeg"
      ></v-checkbox>
    </v-container>
    <div>
      <v-card flat>
        <v-card-text>
          <v-container fluid>
            <v-row>
              <v-col cols="12" sm="4" md="4">
                <v-switch
                  label="Highlight start of each year"
                  v-model="this.options.yearHighlight"
                  color="primary"
                ></v-switch>
                <v-switch
                  label="Display text for year"
                  v-model="this.options.yearText"
                  color="primary"
                ></v-switch>
              </v-col>
              <v-col>
                <v-select
                  label="Select color scheme"
                  :items="['Cividis', 'Viridis', 'Inferno', 'Magma', 'Plasma']"
                  v-model="this.options.colorScheme"
                ></v-select>
                <v-select
                  label="Select granularity"
                  item-text="text"
                  item-disabled="disable"
                  :items="this.options.granularityItems"
                  v-model="this.options.granularity"
                ></v-select>
              </v-col>
              <v-col> </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </div>
    <svg ref="spiralPlot"></svg>
    <div id="legend"></div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  props: {
    displayedData: Object,
    baseGranularity: String,
  },
  data() {
    return {
      options: {
        yearHighlight: false,
        granularity: undefined,
        yearText: true,
        granularityItems: ["Hours", "Days", "Months"],
        colorScheme: "Cividis",
      },
      defaults: {
        hours: 168,
        days: 365,
        months: 12,
      },
      recommendedSeg: true,
      segmentsPerCycle: undefined,
      radians: 0.0174532925,
      cyclePadding: 1,
      cycles: undefined,
      data: null,
      radius: 500,
      innerRatio: 0.3,
      width: 1000,
      height: 1000,
      dataSize: 0,
      //set radius for empty space
      margin: { top: 50, right: 50, bottom: 50, left: 50 },
      segmentAngle: undefined,
      innerRadius: undefined,
      segmentWidth: undefined,
    };
  },
  watch: {
    options: {
      handler: "handleOptions",
      deep: true,
    },
    displayedData: "prepareData",
    segmentsPerCycle: "prepareData",
    cycles: "prepareData",
    recommendedSeg: "setDefaultSegmentsPerCycle",
  },
  mounted() {
    this.setGranularities();
    this.setDefaultSegmentsPerCycle();
  },
  methods: {
    setGranularities() {
      switch (this.baseGranularity) {
        case "Hours":
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
      return this.displayedData;
    },

    prepareData() {
      const aggregatedData = this.aggregateData();
      console.log(this.segmentsPerCycle);
      console.log(this.defaults.days);
      console.log(this.granularity);
      if (
        (this.segmentsPerCycle == this.defaults.hour &&
          this.options.granularity == "Hours") ||
        (this.segmentsPerCycle == this.defaults.days &&
          this.options.granularity == "Days") ||
        (this.segmentsPerCycle == this.defaults.month &&
          this.options.granularity == "Months")
      ) {
        this.recommendedSeg = true;
      } else {
        this.recommendedSeg = false;
      }
      this.innerRadius = this.radius * this.innerRatio;
      this.segmentAngle = 360 / this.segmentsPerCycle;
      this.cycles = Math.ceil(aggregatedData.length / this.segmentsPerCycle);
      this.segmentWidth =
        (this.radius * (1 - this.innerRatio)) / (this.cycles + 1);
      this.data = aggregatedData.map((entry) => {
        const { date, value, count } = entry;
        const parsedDate = new Date(date);
        const year = parsedDate.getFullYear();
        const month = parsedDate.getMonth() + 1; // Months are zero-based, so we add 1
        const day = parsedDate.getDate();

        return {
          year: year,
          month: month,
          day: day,
          value: value,
        };
      });
      this.data.sort(function (a, b) {
        return a.year - b.year || a.month - b.month;
      });
      this.renderGraph();
    },

    renderGraph() {
      d3.select(this.$refs.spiralPlot).selectAll("*").remove();
      var c = `d3.interpolate${this.options.colorScheme}`;
      var color = d3.scaleSequential(eval(c));
      var radians = this.radians;
      const svg = d3
        .select(this.$refs.spiralPlot)
        .attr("width", this.width + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top + this.margin.bottom);

      const g = svg
        .append("g")
        .attr(
          "transform",
          "translate(" +
            (this.margin.left + this.radius) +
            "," +
            (this.margin.top + this.radius) +
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

      this.data.forEach((d, i) => {
        var segment = Math.floor(i / this.segmentsPerCycle);
        var position = i - segment * this.segmentsPerCycle;
        //console.log("position: " + position)

        var startAngle = position * this.segmentAngle;
        var endAngle = (position + 1) * this.segmentAngle;
        //console.log("angles: " + startAngle +", " + endAngle)

        var startInnerRadius =
          this.cyclePadding +
          this.innerRadius +
          (i / this.segmentsPerCycle) * this.segmentWidth;
        var startOuterRadius =
          this.innerRadius +
          (i / this.segmentsPerCycle) * this.segmentWidth +
          this.segmentWidth;
        var endInnerRadius =
          this.cyclePadding +
          this.innerRadius +
          ((i + 1) / this.segmentsPerCycle) * this.segmentWidth;
        var endOuterRadius =
          this.innerRadius +
          ((i + 1) / this.segmentsPerCycle) * this.segmentWidth +
          this.segmentWidth;

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

        let midAngle = startAngle + this.segmentAngle / 2;
        let midInnerRadius =
          this.innerRadius +
          this.cyclePadding +
          ((i + 0.5) / this.segmentsPerCycle) * this.segmentWidth;
        let midOuterRadius =
          this.innerRadius +
          ((i + 0.5) / this.segmentsPerCycle) * this.segmentWidth +
          this.segmentWidth;

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
        });

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
          });
      }

      //create Legend
      var legendWidth = this.width / 2;
      var legendHeight = 20;

      var legend = d3
        .select(this.$refs.spiralPlot)
        .append("g")
        .attr("class", "legend")
        .attr("width", legendWidth)
        .attr("height", legendHeight);

      var colorRange = [];
      for (let index = dataExtent[0]; index < dataExtent[1]; index++) {
        colorRange.push(color(index));
      }

      // Create linear gradient
      legend
        .append("defs")
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
      legend
        .append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#colorGradient)");

      var tickValues = d3.range(dataExtent[0], dataExtent[1] + 1, 10);
      var tickScale = d3
        .scaleLinear()
        .domain(dataExtent)
        .range([0, legendWidth]);

      legend
        .selectAll(".tick")
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
      legend
        .selectAll(".tick-label")
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
    },
  },
};
</script>
