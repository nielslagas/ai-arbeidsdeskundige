<script setup>
import { ref, defineProps } from 'vue'
import { supabase } from '../utils/supabase' // Supabase client is needed for auth header

const props = defineProps({
  caseId: {
    type: [String, Number],
    required: true
  }
})

const searchQuery = ref('')
const searchResults = ref([])
const loading = ref(false)
const error = ref(null)

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    error.value = 'Please enter a search query.'
    searchResults.value = [] // Clear previous results
    return
  }

  error.value = null
  searchResults.value = []
  loading.value = true

  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      throw new Error('User not authenticated.')
    }

    const response = await fetch(`/search/${props.caseId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify({ query: searchQuery.value })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Document search failed.')
    }

    const result = await response.json()
    searchResults.value = result // Assuming the backend returns an array of search results (chunks)

  } catch (err) {
    error.value = err.message
    console.error('Error performing search:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h3>Search Documents</h3>
    <form @submit.prevent="performSearch">
      <div>
        <label for="searchQuery">Search Query:</label>
        <input type="text" id="searchQuery" v-model="searchQuery" placeholder="Enter your search query..." />
      </div>
      <button type="submit" :disabled="loading || !searchQuery.trim()">
        {{ loading ? 'Searching...' : 'Search' }}
      </button>
      <p v-if="error" style="color: red;">{{ error }}</p>
    </form>

    <div v-if="searchResults.length">
      <h4>Search Results:</h4>
      <ul>
        <li v-for="result in searchResults" :key="result.id">
          <!-- Assuming each result object has 'id', 'content', and potentially 'document_id' -->
          <p><strong>Chunk ID:</strong> {{ result.id }}</p>
          <p><strong>Content:</strong> {{ result.content }}</p>
          <!-- Display other relevant info like document name if available -->
          <hr />
        </li>
      </ul>
    </div>
    <p v-else-if="!loading && !error && searchQuery.trim()">No results found for "{{ searchQuery }}".</p>
  </div>
</template>

<style scoped>
/* Add some basic styling */
form {
  display: flex;
  flex-direction: column;
  gap: 1em;
  max-width: 600px;
  margin: 1em auto;
  padding: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
}

input[type="text"] {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  border: 1px solid #eee;
  margin-bottom: 1em;
  padding: 1em;
  border-radius: 4px;
  background-color: #f9f9f9;
}
</style>
