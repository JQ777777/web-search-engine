// src/router.js
import { createRouter, createWebHistory } from 'vue-router';
import SearchPage from './components/SearchPage.vue';
import AuthPage from './components/AuthPage.vue';
import HtmlSnapshot from './components/HtmlSnapshot.vue';

const routes = [
  {
    path: '/',
    redirect: { name: 'Search', params: { index: 'nku_index' } } // 默认重定向到 articles 索引
  },
  {
    path: '/auth',
    name: 'Auth',
    component: AuthPage
  },
  {
    path: '/search/:index/:query?',
    name: 'Search',
    component: SearchPage,
    beforeEnter: (to, from, next) => {
      if (to.params.query) {
        next(); // 直接允许跳转
      } else {
        next();
      }
    }
  },
  {
    path: '/snapshot/:id', // 使用动态路由参数来传递快照ID或路径
    name: 'HtmlSnapshot',
    component: HtmlSnapshot,
    props: route => ({ htmlFilePath: route.params.id })
  },
  
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;