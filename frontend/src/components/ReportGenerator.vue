<script setup>
import { ref, defineProps } from 'vue'
import { supabase } from '../utils/supabase' // Supabase client is needed for auth header

const props = defineProps({
  caseId: {
    type: [String, Number],
    required: true
  }
})

const prompt = ref('')
const generatedReport = ref(null)
const loading = ref(false)
const error = ref(null)

const generateReport = async () => {
  if (!prompt.value.trim()) {
    error.value = 'Please enter a prompt to generate the report.'
    return
  }

  error.value = null
  generatedReport.value = null
  loading.value = true

  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      throw new Error('User not authenticated.')
    }

    // Send the prompt as a query parameter instead of in the body
    const response = await fetch(`/reports/generate/${props.caseId}?prompt=${encodeURIComponent(prompt.value)}`, {
      method: 'POST',
      headers: {
        // 'Content-Type': 'application/json', // Not needed for query parameters
        'Authorization': `Bearer ${session.access_token}`
      },
      // body: JSON.stringify({ prompt: prompt.value }) // Remove body
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Report generation failed.')
    }

    const result = await response.json()
    generatedReport.value = result.report_content // Assuming the backend returns an object with a 'report_content' key

  } catch (err) {
    error.value = err.message
    console.error('Error generating report:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h3>Generate Report</h3>
    <form @submit.prevent="generateReport">
      <div>
        <label for="reportPrompt">Prompt:</label>
        <textarea id="reportPrompt" v-model="prompt" rows="4" placeholder="Enter your prompt for the report..."></textarea>
      </div>
      <button type="submit" :disabled="loading || !prompt.trim()">
        {{ loading ? 'Generating...' : 'Generate Report' }}
      </button>
      <p v-if="error" style="color: red;">{{ error }}</p>
    </form>

    <div v-if="generatedReport">
      <h4>Generated Report:</h4>
      <div class="report-content">
        <p>{{ generatedReport }}</p>
        <!-- Render the generated report content -->
      </div>
    </div>
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

textarea {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* Include padding and border in the element's total width and height */
}

.report-content {
  margin-top: 1em;
  padding: 1em;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: #f9f9f9;
  white-space: pre-wrap; /* Preserve whitespace and line breaks */
}
</style>
