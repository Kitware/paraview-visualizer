export default {
  name: 'CustomWidget',
  props: {
    attribute_name: {
      type: String,
    },
    js_attr_name: {
      type: String,
    },
  },
  methods: {
    triggerClick() {
      this.$emit('click');
    },
    triggerChange() {
      this.$emit('change');
    },
  },
};
