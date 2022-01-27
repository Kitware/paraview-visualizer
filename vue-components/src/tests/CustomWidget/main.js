import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/dist/vuetify.min.css';
import 'typeface-roboto';

import Vue from 'vue';
import Vuetify from 'vuetify';

import App from './App';

Vue.config.productionTip = false;
Vue.use(Vuetify);

new Vue({
  vuetify: new Vuetify(),
  render: (h) => h(App),
}).$mount('#app');
