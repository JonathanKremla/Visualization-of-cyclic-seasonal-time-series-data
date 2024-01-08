<template>
    <v-range-slider
      v-if="this.max"
      v-model="this.displayedRange"
      step= "30"
      show-ticks="always"
      :ticks="this.ticks"
      :max="this.max"
      min="1"
    ></v-range-slider>
</template>
<script>

export default {
  props: {
    data: Object,
    max: Number,
  },
  data() {
    return {
      displayedRange: [0,0],
      ticks: {},
    }
  },
  mounted() {
    this.displayedRange = [1, this.max]
  },
  watch: {
   displayedRange:  "sendUpdatedRange"
  },
  
  methods: {
    sendUpdatedRange() {
      this.$emit('updatedRange', this.displayedRange);
    },
    //TODO: Calculate ticks for finer granularity
    calculateTicks() {
      const uniqueMonths = [
        ...new Set(this.data.map((item) => new Date(item.date).getMonth())),
      ];
      const uniqueYears = [
        ...new Set(this.data.map((item) => new Date(item.date).getFullYear())),
      ];
      var counter = 0;
      for (let index = 0; index < uniqueYears.length; index++) {
        uniqueMonths.forEach((val) => {
          if (val === 0) {
            this.ticks[counter * 30] = uniqueYears[index];
          } else {
            this.ticks[counter * 30] = "";
          }
          counter += 1;
        });
      }
    },
  }
}
</script>
