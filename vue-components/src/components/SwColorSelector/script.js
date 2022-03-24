import { floatToHex2, debounce, areEquals } from '../../utils';

export default {
  name: 'swColorSelector',
  props: {
    name: {
      type: String,
    },
    size: {
      type: Number,
      default: 1,
    },
    label: {
      type: String,
    },
    help: {
      type: String,
    },
    mtime: {
      type: Number,
    },
    type: {
      type: String,
    },
    initial: {},
  },
  data() {
    return {
      color: '#ffffff',
      showHelp: false,
    };
  },
  created() {
    this.flushToServer = debounce(() => {
      const value = (this.properties() && this.properties()[this.name]) || [];
      if (!areEquals(this.initial, value)) {
        this.dirty(this.name);
      }
    }, 100);
  },
  computed: {
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        const value = this.properties() && this.properties()[this.name];
        if (!value) {
          return '#FFFFFF';
        }
        return `#${floatToHex2(value[0])}${floatToHex2(value[1])}${floatToHex2(
          value[2]
        )}`;
      },
      set(hexStr) {
        this.properties()[this.name] = [
          parseInt(hexStr.substr(1, 2), 16) / 255,
          parseInt(hexStr.substr(3, 2), 16) / 255,
          parseInt(hexStr.substr(5, 2), 16) / 255,
        ];
        this.flushToServer();
      },
    },
    decorator() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return (
        this.domains()[this.name]?.decorator?.available || {
          show: true,
          enable: true,
        }
      );
    },
    hints() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.domains()?.[this.name]?.hints || [];
    },
  },
  inject: ['data', 'properties', 'domains', 'dirty', 'getSimput'],
};
