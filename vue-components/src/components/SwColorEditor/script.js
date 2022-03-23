// <input name="AmbientColor" />
// <input name="ColorArrayName" />
// <input name="DiffuseColor" />

let COUNT = 1;

export default {
  name: 'swColorEditor',
  props: {
    label: {
      type: String,
      default: 'Coloring',
    },
    mtime: {
      type: Number,
    },
  },
  created() {
    this.onUpdateUI = () => {
      console.log('update UI');
      const newValue = `__ColorEditor_${COUNT}__${this.uiTS()}`;
      if (this.tsKey !== newValue) {
        this.$nextTick(() => {
          this.tsKey = newValue;
        });
      }
    };
    this.simputChannel.$on('templateTS', this.onUpdateUI);
  },
  mounted() {
    COUNT++;
    this.onUpdateUI();
  },
  beforeDestroy() {
    this.simputChannel.$off('templateTS', this.onUpdateUI);
  },
  data() {
    return {
      tsKey: '__default__',
      colorMode: 'Solid Color',
      colorOptions: ['Solid Color', 'RTData', 'Pressure', 'Velocity'],
      componentMode: '',
      componentOptions: ['Magnitude', 'X', 'Y', 'Z'],
    };
  },
  computed: {
    hasComponents() {
      return this.colorMode === 'Velocity';
    },
    hasField() {
      return this.colorMode !== 'Solid Color';
    },
    hasFieldStyle() {
      return this.hasField ? {} : { opacity: 0.5 };
    },
  },
  inject: [
    'data',
    'properties',
    'domains',
    'dirty',
    'getSimput',
    'uiTS',
    'simputChannel',
  ],
};
