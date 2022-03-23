import components from './components';
import icons from './icons';

export default {
  install(Vue) {
    Object.keys(components).forEach((name) => {
      Vue.component(name, components[name]);
    });

    // SVG icons
    Object.keys(icons).forEach((name) => {
      console.log('register vue widget', name);
      Vue.component(name, icons[name]);
    });
  },
};
