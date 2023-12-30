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
    granularity: String
  },
  data() {
    return {
      data: null,
      groupedData: null,
      dataSize: 0,
      margin: { top: 50, right: 50, bottom: 50, left: 50 },
      width: 800,
      height: 500,
    };
  },
  watch: {
    displayedData: "groupData",
  },
  methods: {
    calculateMonthYear() {
      const monthlyTotals = {};
      const monthlyCounts = {};

      this.displayedData.forEach(entry => {
        const month = new Date(entry.date).getMonth();
        monthlyTotals[month] = (monthlyTotals[month] || 0) + entry.value;
        monthlyCounts[month] = (monthlyCounts[month] || 0) + 1;
      });

      // Calculate the average for each month
      const monthlyAverages = Object.keys(monthlyTotals).reduce((result, month) => {
        result[month] = monthlyTotals[month] / monthlyCounts[month];
        return result;
      }, {});

      // Log the monthly averages (you can do anything else with the result)
      console.log(monthlyAverages);
      return monthlyAverages;

    },
    groupData() {
      console.log(this.granularity)
      switch (this.granularity) {
        case 'month-year':
            this.groupedData=this.calculateMonthYear()
          break;
      
        default:
          break;
      }

    },
    createCyclePlot() {
      console.log(this.displayedData)
    },
  },
};
</script>

<style scoped>
/* Add your component styles here if needed */
</style>
