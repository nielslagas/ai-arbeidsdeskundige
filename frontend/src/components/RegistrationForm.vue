<script setup>
import { ref } from 'vue'
import { supabase } from '../utils/supabase'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(false)

const handleRegistration = async () => {
  error.value = null
  success.value = false
  loading.value = true
  const { error: authError } = await supabase.auth.signUp({
    email: email.value,
    password: password.value,
  })
  if (authError) {
    error.value = authError.message
  } else {
    success.value = true
    // Optionally clear form or redirect
    email.value = ''
    password.value = ''
    console.log('User registered successfully! Check email for confirmation.')
  }
  loading.value = false
}
</script>

<template>
  <form @submit.prevent="handleRegistration">
    <h2>Register</h2>
    <div>
      <label for="email">Email:</label>
      <input type="email" id="email" v-model="email" required />
    </div>
    <div>
      <label for="password">Password:</label>
      <input type="password" id="password" v-model="password" required />
    </div>
    <button type="submit" :disabled="loading">
      {{ loading ? 'Loading...' : 'Register' }}
    </button>
    <p v-if="error" style="color: red;">{{ error }}</p>
    <p v-if="success" style="color: green;">Registration successful! Please check your email to confirm your account.</p>
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
