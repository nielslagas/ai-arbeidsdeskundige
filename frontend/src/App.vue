<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { supabase } from './utils/supabase'

const router = useRouter()
const session = ref(null)

// Function to handle logout
const handleLogout = async () => {
  const { error } = await supabase.auth.signOut()
  if (error) {
    console.error('Error logging out:', error.message)
  } else {
    session.value = null // Clear local session state
    router.push('/login') // Redirect to login after logout
    console.log('User logged out')
  }
}

// Check session on mount and listen for auth changes
onMounted(() => {
  supabase.auth.getSession().then(({ data }) => {
    session.value = data.session
  })

  supabase.auth.onAuthStateChange((event, _session) => {
    session.value = _session
    // Optional: Redirect on login/logout if needed, handled by router guard mostly
    // if (event === 'SIGNED_IN' && router.currentRoute.value.path === '/login') {
    //   router.push('/dashboard/cases');
    // } else if (event === 'SIGNED_OUT') {
    //   router.push('/login');
    // }
  })
})
</script>

<template>
  <header>
    <nav>
      <!-- Show Login/Register if not logged in -->
      <template v-if="!session">
        <RouterLink to="/login">Login</RouterLink>
        <RouterLink to="/register">Register</RouterLink>
      </template>
      <!-- Show Dashboard link and Logout button if logged in -->
      <template v-else>
        <RouterLink to="/dashboard/cases">Dashboard</RouterLink>
        <button @click="handleLogout">Logout</button>
      </template>
    </nav>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a, nav button {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  background: none; /* Style button like links */
  border: none;
  cursor: pointer;
  font-size: 12px; /* Match link font size */
  font-family: inherit; /* Match link font family */
  color: var(--color-text); /* Match link color */
  text-decoration: none; /* Remove underline */
}

nav a.router-link-exact-active {
  color: var(--color-primary); /* Highlight active link */
}

nav button:hover, nav a:hover {
  background-color: transparent; /* Consistent hover */
  text-decoration: underline;
}


nav a:first-of-type, nav button:first-of-type {
  border: 0;
}
</style>
