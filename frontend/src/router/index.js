import { createRouter, createWebHistory } from 'vue-router'
import { supabase } from '../utils/supabase' // Import supabase client
import LoginForm from '../components/LoginForm.vue'
import RegistrationForm from '../components/RegistrationForm.vue'
import DashboardLayout from '../views/DashboardLayout.vue' // Import the new layout
import CaseList from '../views/CaseList.vue' // Import CaseList

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login' // Redirect root to login
    },
    {
      path: '/login',
      name: 'login',
      component: LoginForm
    },
    {
      path: '/register',
      name: 'register',
      component: RegistrationForm
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardLayout,
      meta: { requiresAuth: true }, // Mark this route and its children as requiring authentication
      children: [
        {
          path: 'cases', // Nested path
          name: 'case-list',
          component: CaseList // Use CaseList component
        },
        {
          path: 'cases/:caseId', // Route for Case Details with a dynamic parameter
          name: 'case-details',
          component: () => import('../views/CaseDetails.vue') // Lazy load CaseDetails component
        }
      ]
    }
  ]
})

// Navigation guard to check for authentication
router.beforeEach(async (to, from, next) => {
  const { data: { session } } = await supabase.auth.getSession()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !session) {
    // If route requires auth and user is not logged in, redirect to login
    next('/login')
  } else {
    // Otherwise, allow navigation
    next()
  }
})

export default router
