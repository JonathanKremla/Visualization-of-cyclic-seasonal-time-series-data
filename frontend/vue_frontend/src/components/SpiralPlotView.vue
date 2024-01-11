
<template>
  <div>
    <svg ref="spiralPlot"></svg>
    <div id="legend"></div>
  </div>
</template>

<script >
import * as d3 from "d3";

export default {
  props: {
    displayedData: Object,
    segmentsPerCycle: Number,
  },
  data() {
    return {
      radians: 0.0174532925,
      cyclePadding: 1,
      cycles: undefined,
      data: null,
      radius: 400,
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
    displayedData: "prepareData",
    segmentsPerCycle: "prepareData",
    cycles: "prepareData",
  },
  methods: {
    prepareData() {
      this.innerRadius = this.radius * this.innerRatio;
      this.segmentAngle = 360 / this.segmentsPerCycle;
      this.cycles = Math.ceil(
        this.displayedData.length / this.segmentsPerCycle
      );
      this.segmentWidth =
        (this.radius * (1 - this.innerRatio)) / (this.cycles + 1);
      this.data = this.displayedData.map((entry) => {
        const { date, value } = entry;
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
      this.d;

      this.data.sort(function (a, b) {
        return a.year - b.year || a.month - b.month;
      });
      this.renderGraph();
    },

    renderGraph() {
      d3.select(this.$refs.spiralPlot).selectAll("*").remove();
      var color = d3.scaleSequential(d3.interpolateViridis);
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
          //start at vertice 1
          let start = "M " + d.x1 + " " + d.y1;
          //inner curve to vertice 2
          let side1 =
            " Q " +
            d.controlPoint1x +
            " " +
            d.controlPoint1y +
            " " +
            d.x2 +
            " " +
            d.y2;
          //straight line to vertice 3
          let side2 = "L " + d.x3 + " " + d.y3;
          //outer curve vertice 4
          let side3 =
            " Q " +
            d.controlPoint2x +
            " " +
            d.controlPoint2y +
            " " +
            d.x4 +
            " " +
            d.y4;
          //combine into string, with closure (Z) to vertice 1
          return start + " " + side1 + " " + side2 + " " + side3 + " Z";
        })
        .style("fill", function (d) {
          return color(d.value);
        });

    //create Legend
    var legendWidth = this.width;
    var legendHeight = 20;

    var legend = d3.select(this.$refs.spiralPlot)
        .append("g")
        .attr("class", "legend")
        .attr("width", legendWidth)
        .attr("height", legendHeight);

    // Create linear gradient
    legend.append("defs")
        .append("linearGradient")
        .attr("id", "colorGradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .selectAll("stop")
        .data(color.range())
        .enter().append("stop")
        .attr("offset", function(d, i) {
            return i / (color.range().length - 1);
        })
        .attr("stop-color", function(d) {
            return d;
        });

    // Create legend rectangle with gradient
    legend.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#colorGradient)");
    



    },
  },
};
</script>
