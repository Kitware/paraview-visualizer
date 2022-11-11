import { shouldShowDecorator } from '../../utils';

export default {
  name: 'swDisplayRepresentationSelector',
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
    initial: {},
  },
  created() {
    this.onUpdateUI = () => {
      const newValue = `__${this.name}__${this.uiTS()}`;
      if (this.tsKey !== newValue) {
        this.$nextTick(() => {
          this.tsKey = newValue;
        });
      }
    };
    this.simputChannel.$on('templateTS', this.onUpdateUI);
    this.onUpdateUI();
    this.onQuery = (query) => {
      this.query = query;
    };
    this.simputChannel.$on('query', this.onQuery);
  },
  beforeDestroy() {
    this.simputChannel.$off('templateTS', this.onUpdateUI);
    this.simputChannel.$off('query', this.onQuery);
  },
  data() {
    return {
      showHelp: false,
      tsKey: '__default__',
      query: '',
    };
  },
  computed: {
    shouldShowDecorator,
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        return this.properties() && this.properties()[this.name];
      },
      set(v) {
        this.properties()[this.name] = v;
      },
    },
    decorator() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return (
        this.domains()[this.name]?.decorator?.available || {
          show: true,
          enable: true,
          query: true,
        }
      );
    },
    computedItems() {
      // Dynamic domain evaluation
      const availableOptions = this.domains()[this.name] || {};

      return (
        availableOptions?.List?.available || availableOptions?.list?.available
      );
    },
    selectedItem() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.computedItems.find(({ value }) => value === this.model);
    },
  },
  methods: {
    validate() {
      this.dirty(this.name);
      this.trame.trigger('pv_reaction_representation_type', [this.model]);
    },
  },
  inject: [
    'data',
    'properties',
    'domains',
    'dirty',
    'uiTS',
    'simputChannel',
    'trame',
  ],
};
