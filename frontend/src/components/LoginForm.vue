<script setup>
import { ref } from 'vue'
import { supabase } from '../utils/supabase'
import { useRouter } from 'vue-router' // Import useRouter

const router = useRouter() // Get the router instance

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const handleLogin = async () => {
  error.value = null
  loading.value = true
  const { error: authError } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value,
  })
  if (authError) {
    error.value = authError.message
  } else {
    console.log('User logged in successfully!')
    router.push('/dashboard/cases') // Redirect to dashboard on successful login
  }
  loading.value = false
}
</script>

<template>
  <form @submit.prevent="handleLogin">
    <h2>Login</h2>
    <div>
      <label for="email">Email:</label>
      <input type="email" id="email" v-model="email" required />
    </div>
    <div>
      <label for="password">Password:</label>
      <input type="password" id="password" v-model="password" required />
    </div>
    <button type="submit" :disabled="loading">
      {{ loading ? 'Loading...' : 'Login' }}
    </button>
    <p v-if="error" style="color: red;">{{ error }}</p>
  </form>
</template>

<style scoped>
/* Add some basic styling */
form {
  display: flex;
  flex-direction: column;
  gap: 1em;
  max-width: 300px;
  margin: 0 auto;
  padding: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>
