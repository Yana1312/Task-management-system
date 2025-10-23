<template>
  <nav class="vertical-navbar">
    <div class="nav-top">
      <router-link to="/profile" aria-label="Профиль">
        <img class="nav-avatar-img" :src="avatarSrc" alt="Профиль" @error="onAvatarError" />
      </router-link>
    </div>

    <div class="nav-items">
      <router-link to="/main" class="nav-item" :class="{ active: isActivePath('/main') }" aria-label="Домой">
        <img class="nav-icon-img" src="/resources/menu_icon.svg" alt="Домой"/>
      </router-link>

      <router-link to="/main#tasks" class="nav-item" :class="{ active: isActiveHash('#tasks') }" aria-label="Задачи">
        <img class="nav-icon-img" src="/resources/zadachi_icon.svg" alt="Задачи"/>
      </router-link>

      <router-link to="/main#folders" class="nav-item" :class="{ active: isActiveHash('#folders') }" aria-label="Папки">
        <img class="nav-icon-img" src="/resources/folder_icon.svg" alt="Папки"/>
      </router-link>
    </div>

    <div class="nav-footer">
      <router-link to="/main#settings" class="nav-item" :class="{ active: isActiveHash('#settings') }" aria-label="Настройки">
        <img class="nav-icon-img" src="/resources/settings.svg" alt="Настройки"/>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { auth } from '../js/auth.js'

const route = useRoute()
const isActivePath = (path) => route.path === path
const isActiveHash = (hash) => route.path === '/main' && route.hash === hash

onMounted(() => {
  console.log('[navbar] mounted userId:', auth.userId.value, 'avatarUrl:', auth.avatarUrl.value)
  if (!auth.avatarUrl.value) {
    auth.fetchAvatar().then((url) => {
      console.log('[navbar] fetchAvatar resolved url:', url)
    }).catch((e) => console.warn('[navbar] fetchAvatar error:', e))
  }
})

const avatarSrc = computed(() => auth.avatarUrl.value || auth.PLACEHOLDER_AVATAR)

watch(() => auth.userId.value, (nv, ov) => {
  console.log('[navbar] userId changed:', ov, '->', nv)
})

watch(() => auth.avatarUrl.value, (nv, ov) => {
  console.log('[navbar] avatarUrl changed:', ov, '->', nv)
})

const onAvatarError = (e) => {
  console.warn('[navbar] img error, fallback to placeholder')
  e.target.src = auth.PLACEHOLDER_AVATAR
}
</script>