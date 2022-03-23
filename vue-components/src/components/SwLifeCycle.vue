<template>
  <div>Life cycle {{ uiType }} - instance {{ count }}</div>
</template>
<script>
const COUNTS = {};

export default {
  name: 'swLifeCycle',
  props: {
    uiType: {
      type: String,
    },
  },
  data() {
    return {
      count: 0,
    };
  },
  created() {
    if (COUNTS[this.uiType]) {
      COUNTS[this.uiType]++;
    } else {
      COUNTS[this.uiType] = 1;
    }
    this.count = COUNTS[this.uiType];
  },
};
</script>
