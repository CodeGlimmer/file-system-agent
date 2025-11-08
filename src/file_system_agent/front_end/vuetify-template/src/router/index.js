import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayOut from '@/layout/MainLayOut.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: MainLayOut,
    },
  ],
})

export default router
