// <input name="AmbientColor" />
// <input name="ColorArrayName" />
// <input name="DiffuseColor" />

export default {
  name: 'swColorEditor',
  props: {
    label: {
      type: String,
      default: 'Coloring',
    },
  },
  data() {
    return {
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
};
