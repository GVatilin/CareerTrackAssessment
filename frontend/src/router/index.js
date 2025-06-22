import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login Page',
    component: () => import('../pages/login/index.vue'),
    meta: { isLogin: true }
  },
  {
    path: '/registration',
    name: 'Registration',
    component: () => import('../pages/login/index.vue'),
    meta: { isLogin: false }
  },
  {
    path: '/profile',
    name: 'Profile Page',
    component: () => import('../pages/profile/index.vue')
  },
  {
    path: '/settings',
    name: 'Settings Page',
    component: () => import('../pages/settings/index.vue')
  },
  {
    path: '/debug',
    name: 'Debug',
    component: () => import('../pages/debug/index.vue')
  },
  {
    path: '/',
    name: 'Textbook',
    component: () => import('../pages/textbook/index.vue')
  },
  {
    path: '/textbook',
    name: 'Textbook',
    component: () => import('../pages/textbook/index.vue')
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: () => import('../pages/quiz/index.vue')
  },
  {
    path: '/activity',
    name: 'Activity',
    component: () => import('../pages/activity/index.vue')
  },
  {
    path: '/auth/google/callback',
    name: 'Google Auth',
    component: () => import('../pages/google_redirect/index.vue')
  },
  {
    path: '/404',
    name: '404',
    component: () => import('../pages/error404/index.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router