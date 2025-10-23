<template>
  <div :class="['app-shell', { 'with-navbar': !isAuthRoute }]">
    <Navbar v-if="!isAuthRoute" />
    <div class="app-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

const route = useRoute()
const isAuthRoute = computed(() => route.path === '/' || route.path === '/register')
</script>

<style>
</style>
