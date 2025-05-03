<script setup>
import { ref } from 'vue'
import { supabase } from '../utils/supabase'

const caseName = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(false)

const emit = defineEmits(['case-created'])

const handleCreateCase = async () => {
  error.value = null
  success.value = false
  loading.value = true
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      throw new Error('User not authenticated')
    }

    const response = await fetch('/cases/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify({ name: caseName.value })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to create case')
    }

    const data = await response.json()
    success.value = true
    caseName.value = '' // Clear the form
    console.log('Case created successfully:', data)
    emit('case-created') // Emit event to notify parent
  } catch (err) {
    error.value = err.message
    console.error('Error creating case:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleCreateCase">
    <h3>Create New Case</h3>
    <div>
      <label for="caseName">Case Name:</label>
      <input type="text" id="caseName" v-model="caseName" required />
    </div>
    <button type="submit" :disabled="loading">
      {{ loading ? 'Creating...' : 'Create Case' }}
    </button>
    <p v-if="error" style="color: red;">{{ error }}</p>
    <p v-if="success" style="color: green;">Case created successfully!</p>
  </form>
</template>

<style scoped>
/* Add some basic styling */
form {
  display: flex;
  flex-direction: column;
  gap: 1em;
  max-width: 300px;
  margin: 1em auto;
  padding: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>
