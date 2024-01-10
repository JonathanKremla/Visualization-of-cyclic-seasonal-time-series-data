<template>
  <v-range-slider
    v-if="this.max"
    v-model="this.displayedRange"
    :step=this.steps
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
    granularity: String,
  },
  data() {
    return {
      displayedRange: [0, 0],
      ticks: {},
      steps: 1,
    };
  },
  mounted() {
    this.displayedRange = [1, this.max];
    this.calculateTicks();
  },
  watch: {
    displayedRange: "sendUpdatedRange",
  },

  methods: {
    sendUpdatedRange() {
      this.$emit("updatedRange", this.displayedRange);
    },
    //TODO: Calculate ticks for finer granularity
    calculateTicks() {
      if (this.granularity === "day") {
        this.steps=30;
        const uniqueMonths = [
          ...new Set(this.data.map((item) => new Date(item.date).getMonth())),
        ];
        console.log(uniqueMonths);
        const uniqueYears = [
          ...new Set(
            this.data.map((item) => new Date(item.date).getFullYear())
          ),
        ];
        for (let index = 0; index < uniqueYears.length; index++) {
          uniqueMonths.forEach((val) => {
            if (val === 0) {
              this.ticks[index * 30] = uniqueYears[index];
            } else {
              this.ticks[index * 30] = "";
            }
          });
        }
      }
      console.log(this.data);
      if (this.granularity === "hour") {
        this.steps = 24
        const uniqueMonths = [
          ...new Set(
            this.data.map((item) =>
              new Date(item.date).toLocaleString("default", { month: "long" })
            )
          ),
        ];
        uniqueMonths.forEach((val, index) => {
          this.ticks[index * 30 * 24] = uniqueMonths[index];
        });
      }
    },
  },
};
</script>
