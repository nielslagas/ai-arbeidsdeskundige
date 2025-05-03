<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { supabase } from '../utils/supabase' // Supabase client is needed for auth header

const props = defineProps({
  caseId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['document-uploaded'])

const selectedFiles = ref([])
const loading = ref(false)
const error = ref(null)
const success = ref(false)

const handleFileSelect = (event) => {
  selectedFiles.value = Array.from(event.target.files).filter(file =>
    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || // .docx
    file.type === 'text/plain' // .txt
  )
  error.value = null // Clear previous errors on new selection
  success.value = false // Clear previous success on new selection
}

const handleUpload = async () => {
  if (selectedFiles.value.length === 0) {
    error.value = 'Please select at least one .docx or .txt file.'
    return
  }

  error.value = null
  success.value = false
  loading.value = true

  const formData = new FormData()
  // The backend expects a single file under the name 'file' for this endpoint
  // If uploading multiple files, a loop is still needed, but the backend needs to handle multiple 'file' fields or a different structure.
  // For the MVP, we'll assume single file upload or backend handles multiple 'file' fields.
  // Based on the backend signature `file: UploadFile = File(...)`, it expects a single file.
  // Let's send only the first selected file for now to match the backend signature.
  if (selectedFiles.value.length > 0) {
    formData.append('file', selectedFiles.value[0]) // 'file' should match the backend endpoint parameter name
  }

  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      throw new Error('User not authenticated.')
    }

    const response = await fetch(`/documents/${props.caseId}/upload_mvp`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      },
      body: formData
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'File upload failed.')
    }

    // const result = await response.json() // Backend might return a success message or list of uploaded docs
    success.value = true
    selectedFiles.value = [] // Clear selected files after successful upload
    console.log('Files uploaded successfully.')
    emit('document-uploaded') // Notify parent component

  } catch (err) {
    error.value = err.message
    console.error('Error uploading files:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleUpload">
    <h3>Upload Documents (.docx, .txt)</h3>
    <div>
      <label for="documentUpload">Select Files:</label>
      <input type="file" id="documentUpload" multiple @change="handleFileSelect" accept=".docx,.txt" />
    </div>
    <div v-if="selectedFiles.length">
      <h4>Selected Files:</h4>
      <ul>
        <li v-for="file in selectedFiles" :key="file.name">
          {{ file.name }} ({{ (file.size / 1024).toFixed(2) }} KB)
        </li>
      </ul>
    </div>
    <button type="submit" :disabled="loading || selectedFiles.length === 0">
      {{ loading ? 'Uploading...' : 'Upload Selected Files' }}
    </button>
    <p v-if="error" style="color: red;">{{ error }}</p>
    <p v-if="success" style="color: green;">Upload successful!</p>
  </form>
</template>

<style scoped>
/* Add some basic styling */
form {
  display: flex;
  flex-direction: column;
  gap: 1em;
  max-width: 400px;
  margin: 1em auto;
  padding: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
}

ul {
  list-style: disc;
  padding-left: 1.5em;
}
</style>
