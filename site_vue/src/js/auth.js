import { ref } from 'vue'
import { supabase } from '../lib/supabase.js'

const __DEV__ = typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.DEV;
function log(...args) {
  if (__DEV__) console.log('[auth]', ...args);
}

const userId = ref(null)
const avatarUrl = ref(null)
const isDemo = ref(false)

const PLACEHOLDER_AVATAR = '/resources/user_zaglushka.svg'

export const auth = {
  userId: /** @type {import('vue').Ref<string|null>} */ (/** @type {any} */(ref(null))),
  avatarUrl: /** @type {import('vue').Ref<string|null>} */ (/** @type {any} */(ref(null))),
  isDemo: /** @type {import('vue').Ref<boolean>} */ (/** @type {any} */(ref(false))),
  PLACEHOLDER_AVATAR: '/resources/user_zaglushka.svg',

  setUser(id) {
    log('setUser called with id:', id);
    auth.userId.value = id
    this.userId.value = id || null;
    try {
      if (id) {
        localStorage.setItem('user_id', id);
        log('localStorage user_id set:', id);
      } else {
        localStorage.removeItem('user_id');
        log('localStorage user_id removed');
      }
    } catch (e) {
      log('localStorage error:', e);
    }
  },

  initFromStorage() {
    try {
      const stored = localStorage.getItem('user_id');
      this.userId.value = stored || null;
      log('initFromStorage loaded user_id:', stored);
      const avatarStored = localStorage.getItem('avatar_url');
      this.avatarUrl.value = avatarStored || null;
      log('initFromStorage loaded avatar_url:', avatarStored);
      const demoStored = localStorage.getItem('demo_mode');
      this.isDemo.value = demoStored === '1';
      log('initFromStorage loaded demo_mode:', demoStored);
      if (this.avatarUrl.value && (/^\s*<!doctype/i.test(this.avatarUrl.value) || /<html/i.test(this.avatarUrl.value))) {
        log('initFromStorage invalid avatar_url (HTML), clearing');
        this.avatarUrl.value = null;
        try { localStorage.removeItem('avatar_url'); } catch {}
      }
    } catch (e) {
      log('initFromStorage error:', e);
    }
  },

  initDemoFromEnv() {
    try {
      const flag = String(import.meta?.env?.VITE_DEMO_MODE || '').toLowerCase() === 'true';
      if (flag || localStorage.getItem('demo_mode') === '1') {
        this.enableDemo();
      }
    } catch (e) { log('initDemoFromEnv error:', e); }
  },

  enableDemo() {
    log('enableDemo');
    this.isDemo.value = true;
    try { localStorage.setItem('demo_mode', '1'); } catch {}
    const existingId = localStorage.getItem('user_id');
    this.userId.value = existingId || 'demo-user-id';
    try { if (!existingId) localStorage.setItem('user_id', this.userId.value); } catch {}
    const demoAvatar = localStorage.getItem('demo_avatar');
    this.avatarUrl.value = demoAvatar || this.PLACEHOLDER_AVATAR;
    log('enableDemo set userId:', this.userId.value, 'avatarUrl:', this.avatarUrl.value);
  },

  disableDemo() {
    log('disableDemo');
    this.isDemo.value = false;
    try { localStorage.removeItem('demo_mode'); } catch {}
  },

  normalizeAvatarUrl(raw) {
    log('normalizeAvatarUrl input:', raw);
    if (!raw) return null;
    let s = String(raw);
    s = s.replace(/^["']|["']$/g, '');
    s = s.replace(/\\/g, '/');
    const idx = s.toLowerCase().indexOf('resources/');
    if (idx > -1) s = s.slice(idx);
    s = s.replace(/\/+/g, '/');
    if (!/^https?:\/\//i.test(s)) {
      if (!s.startsWith('/')) s = '/' + s;
    }
    log('normalizeAvatarUrl output:', s);
    return s;
  },

  async fetchAvatarFromSupabaseProfile() {
    try {
      const { data, error } = await supabase.auth.getUser();
      if (error) { log('fetchAvatarFromSupabaseProfile getUser error:', error); return null; }
      const uid = this.userId.value || data?.user?.id || null;
      const email = data?.user?.email || null;

      if (!uid && !email) { log('fetchAvatarFromSupabaseProfile: no uid/email'); return null; }

      let row = null, qErr = null;

      if (uid) {
        const res = await supabase.from('users').select('avatar_url').eq('id', uid).maybeSingle();
        row = res.data; qErr = res.error;
        log('fetchAvatarFromSupabaseProfile by uuid:', uid, 'row:', row, 'error:', qErr);
      }

      if ((!row || !row?.avatar_url) && email) {
        const res2 = await supabase.from('users').select('avatar_url').eq('email', email).maybeSingle();
        if (res2.error) log('fetchAvatarFromSupabaseProfile email fallback error:', res2.error);
        row = res2.data || row;
        log('fetchAvatarFromSupabaseProfile email fallback row:', row);
      }

      const candidate = row?.avatar_url || null;
      const url = this.normalizeAvatarUrl(candidate);
      log('fetchAvatarFromSupabaseProfile candidate:', candidate, 'normalized:', url);
      return url;
    } catch (e) {
      log('fetchAvatarFromSupabaseProfile exception:', e);
      return null;
    }
  },

  async fetchAvatar() {
    if (this.isDemo.value) {
      log('fetchAvatar in DEMO mode');
      const demoAvatar = localStorage.getItem('demo_avatar');
      this.avatarUrl.value = demoAvatar || this.PLACEHOLDER_AVATAR;
      try { localStorage.setItem('avatar_url', this.avatarUrl.value); } catch {}
      return this.avatarUrl.value;
    }

    const uid = this.userId.value;
    log('fetchAvatar start (Supabase). userId:', uid);
    if (!uid) {
      log('fetchAvatar aborted: no userId');
      this.avatarUrl.value = this.PLACEHOLDER_AVATAR;
      return this.avatarUrl.value;
    }
    try {
      let url = await this.fetchAvatarFromSupabaseProfile();

      if (!url) {
        log('fetchAvatar no avatar in Supabase, fallback to placeholder');
        url = this.PLACEHOLDER_AVATAR;
      }

      this.avatarUrl.value = url;
      try {
        localStorage.setItem('avatar_url', url);
        log('fetchAvatar stored avatar_url in localStorage:', url);
      } catch (e) {
        log('fetchAvatar localStorage error:', e);
      }
      log('fetchAvatar done. avatarUrl:', this.avatarUrl.value);
      return this.avatarUrl.value;
    } catch (e) {
      log('fetchAvatar supabase error:', e);
      this.avatarUrl.value = this.PLACEHOLDER_AVATAR;
      return this.avatarUrl.value;
    }
  },

  saveDemoAvatar(dataUrl) {
    if (!dataUrl) return;
    try {
      localStorage.setItem('demo_avatar', dataUrl);
      localStorage.setItem('avatar_url', dataUrl);
    } catch {}
    this.avatarUrl.value = dataUrl;
  },
};