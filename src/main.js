// src/main.js
import {createApp} from 'vue';
import App from './App.vue';
import router from './router';  // 引入路由
import store from './store';

const app = createApp(App);

// 使用路由和 Vuex store
app.use(router).use(store);

// 挂载应用
app.mount('#app');
