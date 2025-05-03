<script setup>
import { ref, onMounted } from 'vue'
import { supabase } from '../utils/supabase'
import CreateCaseForm from '../components/CreateCaseForm.vue'

const cases = ref([])
const loading = ref(false)
const error = ref(null)

const fetchCases = async () => {
  error.value = null
  loading.value = true
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      throw new Error('User not authenticated')
    }

    const response = await fetch('/cases/', {
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to fetch cases')
    }

    const data = await response.json()
    cases.value = data
  } catch (err) {
    error.value = err.message
    console.error('Error fetching cases:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCases()
})

// Function to refresh the case list after a new case is created
const handleCaseCreated = () => {
  fetchCases()
}
</script>

<template>
  <div>
    <h2>Case List</h2>
    <p v-if="loading">Loading cases...</p>
    <p v-if="error" style="color: red;">Error loading cases: {{ error }}</p>
    <ul v-if="cases.length">
      <li v-for="caseItem in cases" :key="caseItem.id">
        <router-link :to="{ name: 'case-details', params: { caseId: caseItem.id } }">
          {{ caseItem.name }} (ID: {{ caseItem.id }})
        </router-link>
      </li>
    </ul>
    <p v-else-if="!loading && !error">No cases found.</p>

    <hr /> <!-- Separator -->

    <CreateCaseForm @case-created="handleCaseCreated" /> <!-- Include the CreateCaseForm and listen for the event -->
  </div>
</template>

<style scoped>
/* Add some basic styling */
ul {
  list-style: none;
  padding: 0;
}

li {
  border: 1px solid #ccc;
  margin-bottom: 0.5em;
  padding: 0.5em;
  border-radius: 4px;
}
</style>
