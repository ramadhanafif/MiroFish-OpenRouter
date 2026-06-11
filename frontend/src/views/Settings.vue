<template>
  <div class="min-h-screen bg-white font-sans text-black">
    <!-- Top Navigation Bar -->
    <nav class="flex h-[60px] items-center justify-between bg-black px-10 text-white max-md:px-5">
      <div class="font-mono text-[1.2rem] font-extrabold tracking-[1px]">MIROFISH OFFLINE</div>
      <div class="flex items-center gap-6">
        <router-link to="/" class="font-mono text-[0.9rem] font-medium text-white no-underline hover:opacity-80">&larr; Back to Home</router-link>
      </div>
    </nav>

    <div class="mx-auto max-w-[900px] px-10 py-[60px] max-md:px-5 max-md:py-8">
      <div class="mb-6 flex items-center gap-[15px] font-mono text-[0.8rem]">
        <span class="bg-accent px-2.5 py-1 text-[0.75rem] font-bold tracking-[1px] text-white">Configuration</span>
        <span class="font-medium tracking-[0.5px] text-[#999]">/ stored in .env at the project root</span>
      </div>
      <h1 class="m-0 mb-5 text-[3rem] font-medium leading-[1.2] tracking-[-1px] text-black max-md:text-[2rem]">Settings</h1>
      <p class="mb-10 max-w-[700px] text-base leading-[1.7] text-[#666]">
        These values are written to the .env file the backend loads at startup.
        Secret fields show a masked preview as the placeholder: leave them blank to keep the current value, or type a new one to replace it.
      </p>

      <div v-if="restartKeys.length" class="mb-[30px] border border-accent bg-accent/5 px-5 py-4 font-mono text-[0.85rem] leading-[1.6] text-[#C73800]">
        Backend restart required for the following keys to take effect: {{ restartKeys.join(', ') }}
      </div>

      <div v-if="loadError" class="mb-[30px] border border-[#D33] bg-[#D33]/5 px-5 py-4 font-mono text-[0.85rem] text-[#B22]">{{ loadError }}</div>

      <div v-for="group in groups" :key="group.id" class="mb-[30px] border border-[#E5E5E5] p-[30px] max-md:p-5">
        <div class="mb-2 flex items-center gap-2 font-mono text-[0.95rem] font-bold tracking-[0.5px] text-black">
          <span class="text-[1.1rem] leading-none text-accent">&#9671;</span> {{ group.label }}
        </div>
        <p v-if="group.description" class="m-0 mb-6 text-[0.85rem] leading-[1.6] text-[#999]">{{ group.description }}</p>

        <div v-for="item in group.keys" :key="item.key" class="mb-[22px]">
          <label class="mb-2 flex items-center gap-2.5 text-[0.95rem] font-[520] text-black max-md:flex-wrap" :for="item.key">
            <span>{{ item.label }}</span>
            <span class="font-mono text-[0.7rem] tracking-[0.5px] text-[#BBB]">{{ item.key }}</span>
            <span v-if="item.restart_required" class="border border-accent px-1.5 py-px font-mono text-[0.65rem] tracking-[0.5px] text-accent">restart required</span>
          </label>
          <input
            v-if="item.secret"
            :id="item.key"
            v-model="form[item.key]"
            type="password"
            autocomplete="new-password"
            :placeholder="item.set ? item.value : 'not set'"
            class="box-border w-full border border-[#DDD] bg-[#FAFAFA] px-4 py-3 font-mono text-[0.9rem] text-black outline-none focus:border-accent"
          />
          <input
            v-else
            :id="item.key"
            v-model="form[item.key]"
            type="text"
            class="box-border w-full border border-[#DDD] bg-[#FAFAFA] px-4 py-3 font-mono text-[0.9rem] text-black outline-none focus:border-accent"
          />
          <div v-if="item.description" class="mt-1.5 text-[0.8rem] leading-[1.5] text-[#999]">{{ item.description }}</div>
        </div>
      </div>

      <div v-if="groups.length" class="mt-2.5 flex items-center gap-6 max-md:flex-col max-md:items-stretch">
        <button
          class="flex cursor-pointer items-center justify-between gap-4 border-none bg-black px-[30px] py-4 font-mono text-base font-bold tracking-[1px] text-white transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="saving"
          @click="save"
        >
          <span>{{ saving ? 'Saving...' : 'Save Changes' }}</span>
          <span>&rarr;</span>
        </button>
        <div v-if="status" class="font-mono text-[0.85rem]" :class="statusOk ? 'text-[#1A7F37]' : 'text-[#B22]'">{{ status }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import service from '../api/index.js'

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
