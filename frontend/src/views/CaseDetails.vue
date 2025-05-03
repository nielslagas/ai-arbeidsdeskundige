<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { supabase } from '../utils/supabase'
import DocumentUploadForm from '../components/DocumentUploadForm.vue'
import ReportGenerator from '../components/ReportGenerator.vue'
import DocumentSearch from '../components/DocumentSearch.vue'

const route = useRoute()
const caseId = ref(null)
const caseDetails = ref(null)
const loading = ref(false)
const error = ref(null)
const documents = ref([])
let pollingInterval = null

const fetchCaseDetails = async (id) => {
  error.value = null
  // Only show loading indicator on initial fetch or manual refresh, not during polling
  if (!pollingInterval) {
     loading.value = true
  }
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      throw new Error('User not authenticated')
    }

    // Fetch case details from backend
    const caseResponse = await fetch(`/cases/${id}`, {
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })

    if (!caseResponse.ok) {
      const errorData = await caseResponse.json()
      throw new Error(errorData.detail || 'Failed to fetch case details')
    }

    const caseData = await caseResponse.json()
    caseDetails.value = caseData

    // Fetch documents for this case from backend
    const documentsResponse = await fetch(`/documents/case/${id}`, {
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })

    if (!documentsResponse.ok) {
      const errorData = await documentsResponse.json()
      throw new Error(errorData.detail || 'Failed to fetch documents')
    }

    const documentsData = await documentsResponse.json()
    documents.value = documentsData

    // Check if all documents are processed and stop polling if so
    const allProcessed = documentsData.every(doc => doc.status === 'processed' || doc.status === 'failed')
    if (allProcessed && pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
      console.log('All documents processed, stopping polling.')
    }

  } catch (err) {
    error.value = err.message
    console.error('Error fetching case details:', err)
    // Stop polling on error
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  } finally {
    // Only hide loading indicator on initial fetch or manual refresh
    if (!pollingInterval) {
      loading.value = false
    }
  }
}

const startPolling = (id) => {
  // Clear any existing interval before starting a new one
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }
  // Poll every 5 seconds (adjust as needed)
  pollingInterval = setInterval(() => {
    console.log('Polling for document status...')
    fetchCaseDetails(id)
  }, 5000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
    console.log('Polling stopped.')
  }
}


// Watch for changes in the route parameter (caseId)
watch(() => route.params.caseId, (newCaseId) => {
  if (newCaseId) {
    caseId.value = newCaseId
    fetchCaseDetails(newCaseId)
    // startPolling(newCaseId) // Start polling when caseId changes - Commented out to reduce backend log noise
  } else {
    stopPolling() // Stop polling if caseId becomes null (e.g., navigating away)
  }
}, { immediate: true }) // Fetch details immediately on component mount if caseId is in route

// Stop polling when the component is unmounted
onUnmounted(() => {
  stopPolling()
})

// Function to refresh documents after upload
const handleDocumentUploaded = () => {
  fetchCaseDetails(caseId.value) // Re-fetch case details and documents immediately
  startPolling(caseId.value) // Ensure polling is active after upload
}
</script>

<template>
  <div>
    <div v-if="loading">Loading case details...</div>
    <div v-if="error" style="color: red;">Error: {{ error }}</div>

    <div v-if="caseDetails">
      <h2>Case: {{ caseDetails.name }} (ID: {{ caseDetails.id }})</h2>

      <h3>Documents</h3>
      <p v-if="documents.length === 0">No documents uploaded yet.</p>
      <ul v-else>
        <li v-for="doc in documents" :key="doc.id">
          {{ doc.filename }} (Status: {{ doc.status }})
          <!-- Add links to view document details or generated reports later -->
        </li>
      </ul>

      <hr /> <!-- Separator -->

      <DocumentUploadForm :case-id="caseId" @document-uploaded="handleDocumentUploaded" /> <!-- Include the upload form -->

      <hr /> <!-- Separator -->

      <ReportGenerator :case-id="caseId" /> <!-- Include the report generator -->

      <hr /> <!-- Separator -->

      <DocumentSearch :case-id="caseId" /> <!-- Include the document search component -->
    </div>
  </div>
</template>

<style scoped>
/* Add some basic styling */
ul {
  list-style: disc;
  padding-left: 1.5em;
}

li {
  margin-bottom: 0.5em;
}
</style>
