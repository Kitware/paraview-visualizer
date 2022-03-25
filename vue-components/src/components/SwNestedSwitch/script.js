export default {
  name: 'swNestedSwitch',
  props: {
    name: {
      type: String,
    },
    mtime: {
      type: Number,
    },
  },
  computed: {
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        return this.properties() && this.properties()[this.name] || false;
      },
      set(v) {
        this.properties()[this.name] = v ? 1 : 0;
      },
    },
  },
  methods: {
    validate() {
      this.dirty(this.name);
    },
  },
  inject: ['data', 'properties', 'dirty'],
};
