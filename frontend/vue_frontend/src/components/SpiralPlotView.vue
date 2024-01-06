
<template>
  <div>
    <svg ref="spiralPlot"></svg>
  </div>
</template>

<script >
import * as d3 from "d3";

export default {
  props: {
    displayedData: Object,
  },
  data() {
    return {
      data: null,
      dataSize: 0,
    };
  },
  watch: {
    displayedData: "renderGraph",
  },
  methods: {
    renderGraph(){

    }

  },
};

</script>
