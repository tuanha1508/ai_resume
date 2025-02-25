<template>
    <div class="min-h-screen bg-gray-100 py-8 px-4">
      <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">AI Resume Skill Extractor</h1>
        
        <FileUpload @upload-success="handleUploadSuccess"/>
        
        <div v-if="skills.length" class="mt-8">
          <h2 class="text-xl font-semibold mb-4">Extracted Skills:</h2>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="(skill, index) in skills" 
              :key="index"
              class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
            >
              {{ skill }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import FileUpload from './components/FileUpload.vue'
  
  const skills = ref([])
  
  const handleUploadSuccess = (extractedSkills) => {
    skills.value = extractedSkills
  }
  </script>