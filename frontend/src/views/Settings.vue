<template>
  <div class="settings-container">
    <!-- Top Navigation Bar -->
    <nav :style="s.navbar">
      <div :style="s.navBrand">MIROFISH OFFLINE</div>
      <div :style="s.navLinks">
        <router-link to="/" :style="s.navLink">&larr; Back to Home</router-link>
      </div>
    </nav>

    <div :style="s.mainContent">
      <div :style="s.tagRow">
        <span :style="s.orangeTag">Configuration</span>
        <span :style="s.versionText">/ stored in .env at the project root</span>
      </div>
      <h1 :style="s.pageTitle">Settings</h1>
      <p :style="s.pageDesc">
        These values are written to the .env file the backend loads at startup.
        Secret fields show a masked preview as the placeholder: leave them blank to keep the current value, or type a new one to replace it.
      </p>

      <div v-if="restartKeys.length" :style="s.restartBanner">
        Backend restart required for the following keys to take effect: {{ restartKeys.join(', ') }}
      </div>

      <div v-if="loadError" :style="s.errorBox">{{ loadError }}</div>

      <div v-for="group in groups" :key="group.id" :style="s.groupBox">
        <div :style="s.groupHeader">
          <span :style="s.diamondIcon">&#9671;</span> {{ group.label }}
        </div>
        <p v-if="group.description" :style="s.groupDesc">{{ group.description }}</p>

        <div v-for="item in group.keys" :key="item.key" :style="s.fieldRow">
          <label :style="s.fieldLabel" :for="item.key">
            <span>{{ item.label }}</span>
            <span :style="s.fieldKey">{{ item.key }}</span>
            <span v-if="item.restart_required" :style="s.restartTag">restart required</span>
          </label>
          <input
            v-if="item.secret"
            :id="item.key"
            v-model="form[item.key]"
            type="password"
            autocomplete="new-password"
            :placeholder="item.set ? item.value : 'not set'"
            :style="s.input"
          />
          <input
            v-else
            :id="item.key"
            v-model="form[item.key]"
            type="text"
            :style="s.input"
          />
          <div v-if="item.description" :style="s.fieldDesc">{{ item.description }}</div>
        </div>
      </div>

      <div v-if="groups.length" :style="s.saveRow">
        <button :style="s.saveBtn" :disabled="saving" @click="save">
          <span>{{ saving ? 'Saving...' : 'Save Changes' }}</span>
          <span>&rarr;</span>
        </button>
        <div v-if="status" :style="statusOk ? s.statusOk : s.statusError">{{ status }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import service from '../api/index.js'

const mono = 'JetBrains Mono, monospace'

const s = reactive({
  navbar: { height: '60px', background: '#000', color: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 40px' },
  navBrand: { fontFamily: mono, fontWeight: '800', letterSpacing: '1px', fontSize: '1.2rem' },
  navLinks: { display: 'flex', alignItems: 'center', gap: '24px' },
  navLink: { color: '#fff', textDecoration: 'none', fontFamily: mono, fontSize: '0.9rem', fontWeight: '500' },
  mainContent: { maxWidth: '900px', margin: '0 auto', padding: '60px 40px' },
  tagRow: { display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '25px', fontFamily: mono, fontSize: '0.8rem' },
  orangeTag: { background: '#FF4500', color: '#fff', padding: '4px 10px', fontWeight: '700', letterSpacing: '1px', fontSize: '0.75rem' },
  versionText: { color: '#999', fontWeight: '500', letterSpacing: '0.5px' },
  pageTitle: { fontSize: '3rem', lineHeight: '1.2', fontWeight: '500', margin: '0 0 20px 0', letterSpacing: '-1px', color: '#000' },
  pageDesc: { fontSize: '1rem', lineHeight: '1.7', color: '#666', marginBottom: '40px', maxWidth: '700px' },
  restartBanner: { border: '1px solid #FF4500', background: 'rgba(255,69,0,0.06)', color: '#C73800', padding: '15px 20px', fontFamily: mono, fontSize: '0.85rem', marginBottom: '30px', lineHeight: '1.6' },
  errorBox: { border: '1px solid #D33', background: 'rgba(221,51,51,0.06)', color: '#B22', padding: '15px 20px', fontFamily: mono, fontSize: '0.85rem', marginBottom: '30px' },
  groupBox: { border: '1px solid #E5E5E5', padding: '30px', marginBottom: '30px' },
  groupHeader: { fontFamily: mono, fontSize: '0.95rem', fontWeight: '700', color: '#000', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', letterSpacing: '0.5px' },
  diamondIcon: { color: '#FF4500', fontSize: '1.1rem', lineHeight: '1' },
  groupDesc: { fontSize: '0.85rem', color: '#999', margin: '0 0 25px 0', lineHeight: '1.6' },
  fieldRow: { marginBottom: '22px' },
  fieldLabel: { display: 'flex', alignItems: 'center', gap: '10px', fontWeight: '520', fontSize: '0.95rem', marginBottom: '8px', color: '#000' },
  fieldKey: { fontFamily: mono, fontSize: '0.7rem', color: '#BBB', letterSpacing: '0.5px' },
  restartTag: { fontFamily: mono, fontSize: '0.65rem', color: '#FF4500', border: '1px solid #FF4500', padding: '1px 6px', letterSpacing: '0.5px' },
  input: { width: '100%', border: '1px solid #DDD', background: '#FAFAFA', padding: '12px 15px', fontFamily: mono, fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box', color: '#000' },
  fieldDesc: { fontSize: '0.8rem', color: '#999', marginTop: '6px', lineHeight: '1.5' },
  saveRow: { display: 'flex', alignItems: 'center', gap: '25px', marginTop: '10px' },
  saveBtn: { background: '#000', color: '#fff', border: 'none', padding: '16px 30px', fontFamily: mono, fontWeight: '700', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '15px', cursor: 'pointer', letterSpacing: '1px' },
  statusOk: { fontFamily: mono, fontSize: '0.85rem', color: '#1A7F37' },
  statusError: { fontFamily: mono, fontSize: '0.85rem', color: '#B22' },
})

const groups = ref([])
const form = reactive({})
const originals = reactive({})
const saving = ref(false)
const status = ref('')
const statusOk = ref(true)
const restartKeys = ref([])
const loadError = ref('')

const load = async () => {
  loadError.value = ''
  try {
    const res = await service.get('/api/settings')
    groups.value = res.data.groups
    for (const group of res.data.groups) {
      for (const item of group.keys) {
        // Secrets start blank: the masked value lives in the placeholder
        form[item.key] = item.secret ? '' : item.value
        originals[item.key] = item.secret ? '' : item.value
      }
    }
  } catch (e) {
    loadError.value = 'Failed to load settings: ' + (e.message || 'unknown error')
  }
}

const save = async () => {
  const payload = {}
  for (const group of groups.value) {
    for (const item of group.keys) {
      const value = form[item.key]
      if (item.secret) {
        // Only send secrets the user actually typed
        if (value && value.trim() !== '') payload[item.key] = value.trim()
      } else if (value !== originals[item.key]) {
        payload[item.key] = value
      }
    }
  }

  if (Object.keys(payload).length === 0) {
    status.value = 'No changes to save.'
    statusOk.value = true
    return
  }

  saving.value = true
  status.value = ''
  try {
    const res = await service.post('/api/settings', payload)
    const applied = res.data.applied || []
    restartKeys.value = res.data.restart_required || []
    status.value = applied.length
      ? `Saved: ${applied.join(', ')}`
      : 'Nothing changed.'
    statusOk.value = true
    await load()
  } catch (e) {
    status.value = 'Save failed: ' + (e.message || 'unknown error')
    statusOk.value = false
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
