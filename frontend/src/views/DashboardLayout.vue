<script setup>
import { useRouter } from 'vue-router'
import { supabase } from '../utils/supabase'

const router = useRouter()

const handleLogout = async () => {
  await supabase.auth.signOut()
  router.push('/login')
}
</script>

<template>
  <div>
    <header>
      <h1>AD-Rapport Generator AI</h1>
      <nav>
        <router-link to="/dashboard/cases">Cases</router-link>
        <!-- Other navigation links will go here later -->
        <button @click="handleLogout">Logout</button>
      </nav>
    </header>
    <main>
      <router-view></router-view> <!-- Content of nested routes will be displayed here -->
    </main>
  </div>
</template>

<style scoped>
/* Basic styling for the layout */
header {
  background-color: #f0f0f0;
  padding: 1em;
  text-align: center;
}

nav a {
  margin: 0 1em;
}

main {
  padding: 1em;
}
</style>
