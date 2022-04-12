export default {
  name: 'swScalarRange',
  props: {
    name: {
      type: String,
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
    size: {
      type: Number,
    },
    hints: {
      type: String,
    },
  },
  data() {
    return {
      spreadCount: 10,
      minValue: 0,
      maxValue: 0,
      showValueGenerator: false,
    };
  },
  computed: {
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        const value = this.properties() && this.properties()[this.name];
        if (!value) {
          return [];
        }
        if (Array.isArray(value)) {
          return value;
        }
        return [value];
      },
      set(array) {
        this.properties()[this.name] = array; // array.map(Number);
      },
    },
    decorator() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return (
        this.domains()[this.name]?.decorator?.available || {
          show: true,
          query: true,
        }
      );
    },
    availableScalarRange() {
      const dataRange = this.domains()[this.name]?.scalar_range?.available;
      if (dataRange) {
        this.minValue = dataRange[0];
        this.maxValue = dataRange[1];
      }
      return dataRange;
    },
  },
  methods: {
    toggleRange() {
      this.showValueGenerator = !this.showValueGenerator;
    },
    addEntry() {
      let nextValue = 0;
      if (this.model.length > 1) {
        const [a, b] = this.model.slice(-2);
        console.log(a, b);
        const delta = b - a;
        nextValue = b + delta;
      }
      this.model = [].concat(this.model, nextValue);
      this.dirty(this.name);
    },
    removeEntry(index = -1) {
      if (index === -1) {
        this.model = this.model.slice(0, -1);
      } else {
        this.model = this.model.filter((v, i) => i !== index);
      }

      this.dirty(this.name);
    },
    clearEntries() {
      this.model = [];
      this.dirty(this.name);
    },
    resetToDefault() {
      if (this.availableScalarRange) {
        this.model = [
          0.5 * (this.availableScalarRange[0] + this.availableScalarRange[1]),
        ];
        this.dirty(this.name);
        this.resetRange();
      }
    },
    spreadValues() {
      const min = Number(this.minValue);
      const max = Number(this.maxValue);
      const count = Number(this.spreadCount);
      const delta = (max - min) / (count - 1);
      const values = [];
      let currentValue = min;
      while (values.length < count) {
        values.push(currentValue);
        currentValue += delta;
      }
      this.model = values;
      this.dirty(this.name);
    },
    validate() {
      this.model = this.model.map(Number);
      this.dirty(this.name);
    },
    resetRange() {
      const dataRange = this.availableScalarRange || [0, 1];
      this.minValue = dataRange[0];
      this.maxValue = dataRange[1];
    },
  },
  inject: ['data', 'domains', 'properties', 'dirty'],
};
