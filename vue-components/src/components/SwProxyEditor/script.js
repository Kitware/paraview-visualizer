export default {
  name: 'swProxyEditor',
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
    hints: {
      type: String,
    },
  },
  data() {
    return {
      collapsed: true,
    };
  },
  computed: {
    decorator() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.domains()[this.name]?.decorator?.available || { show: true };
    },
    collapseIcon() {
      return this.collapsed ? 'mdi-chevron-right' : 'mdi-chevron-down';
    },
    parentId() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.data().id;
    },
    itemId() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.properties()[this.name];
    },
    togglePropertyName() {
      if (this.hints) {
        console.log(atob(this.hints));
        const list = JSON.parse(atob(this.hints)).children;
        const toggleProp = list.find(
          ({ elem_name }) => elem_name === 'ProxyEditorPropertyWidget'
        );
        if (toggleProp) {
          return toggleProp.property;
        }
      }
      return false;
    },
  },
  methods: {
    toggleCollapse() {
      this.collapsed = !this.collapsed;
    },
  },
  inject: ['data', 'domains', 'properties'],
};
