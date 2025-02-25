<template>
    <form @submit.prevent="handleSubmit" class="mb-8">
      <div class="flex flex-col space-y-4">
        <input
          type="file"
          @change="handleFileSelect"
          class="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          accept=".pdf,.docx"
        />
        <button
          type="submit"
          :disabled="loading"
          class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {{ loading ? 'Processing...' : 'Analyze Resume' }}
        </button>
      </div>
    </form>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  
  const emit = defineEmits(['upload-success'])
  const loading = ref(false)
  const selectedFile = ref(null)
  
  const handleFileSelect = (event) => {
    selectedFile.value = event.target.files[0]
  }
  
  const handleSubmit = async () => {
    if (!selectedFile.value) return
    
    loading.value = true
    const formData = new FormData()
    formData.append('file', selectedFile.value)
  
    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      emit('upload-success', response.data.skills)
    } catch (error) {
      alert(error.response?.data?.error || 'An error occurred')
    } finally {
      loading.value = false
    }
  }
  </script>