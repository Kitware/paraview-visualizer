import { floatToHex2, debounce } from '../../utils';

let COUNT = 1;

// Nested properties:
// => AmbientColor, ColorArrayName, DiffuseColor, LookupTable, UseSeparateColorMap
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
      const newValue = `__ColorEditor_${COUNT}__${this.uiTS()}`;
      if (this.tsKey !== newValue) {
        this.$nextTick(() => {
          this.tsKey = newValue;
        });
      }
    };
    this.simputChannel.$on('templateTS', this.onUpdateUI);
    this.flushSolidColorToServer = debounce(() => {
      // May have an issue for beeing 2 calls instead of just 1!
      this.dirtyMany('AmbientColor', 'DiffuseColor');
    }, 100);
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
      componentMode: '',
      componentOptions: ['Magnitude', 'X', 'Y', 'Z'],
    };
  },
  // watch: {
  //   colorMode() {
  //     // console.log(
  //     //   'DATA',
  //     //   JSON.stringify(this.data()?.properties?.ColorArrayName, null, 2)
  //     // );
  //     console.log(
  //       'DOMAIN',
  //       JSON.stringify(this.domains().ColorArrayName, null, 2)
  //     );
  //   },
  // },
  computed: {
    // fixme ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    hasComponents() {
      return this.colorMode === 'Velocity';
    },
    hasField() {
      return this.colorMode !== 'Solid Color';
    },
    hasFieldStyle() {
      return this.hasField ? {} : { opacity: 0.5 };
    },
    // fixme ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    arrayMap() {
      this.mtime; // force refresh
      const arrayMap = { 'Solid Color': ['', '', '', '0', ''] };
      const list = this.domains()?.ColorArrayName?.array_list?.available || [];
      for (let i = 0; i < list.length; i++) {
        const { text, value } = list[i];
        arrayMap[text] = value;
      }
      return arrayMap;
    },
    colorOptions() {
      this.mtime; // force refresh
      const list = this.domains()?.ColorArrayName?.array_list?.available || [];
      const names = list.map(({ text }) => text);
      return ['Solid Color', ...names];
    },
    colorMode: {
      get() {
        this.mtime; // force refresh
        const fieldName = this.properties().ColorArrayName[4];
        if (fieldName.length) {
          return fieldName;
        }
        return 'Solid Color';
      },
      set(name) {
        this.properties().ColorArrayName = this.arrayMap[name];
        this.dirty('ColorArrayName');
      },
    },
    solidColor: {
      get() {
        // AmbientColor, DiffuseColor
        const value = this.properties() && this.properties().AmbientColor;
        if (!value) {
          return '#FFFFFF';
        }
        return `#${floatToHex2(value[0])}${floatToHex2(value[1])}${floatToHex2(
          value[2]
        )}`;
      },
      set(hexStr) {
        const colorFloat = [
          parseInt(hexStr.substr(1, 2), 16) / 255,
          parseInt(hexStr.substr(3, 2), 16) / 255,
          parseInt(hexStr.substr(5, 2), 16) / 255,
        ];
        this.properties().AmbientColor = colorFloat;
        this.properties().DiffuseColor = colorFloat;
        this.flushSolidColorToServer();
      },
    },
  },
  inject: [
    'data',
    'properties',
    'domains',
    'dirty',
    'dirtyMany',
    'getSimput',
    'uiTS',
    'simputChannel',
  ],
};
