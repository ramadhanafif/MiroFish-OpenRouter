<template>
  <div class="min-h-screen bg-white font-sans text-black">
    <!-- Top Navigation Bar -->
    <nav class="flex h-[60px] items-center justify-between bg-black px-10 text-white max-md:px-5">
      <div class="font-mono text-[1.2rem] font-extrabold tracking-[1px]">MIROFISH OFFLINE</div>
      <div class="flex items-center gap-7">
        <router-link to="/settings" class="flex items-center gap-2 font-mono text-[0.9rem] font-medium text-white no-underline transition-opacity hover:opacity-80">
          Settings <span>⚙</span>
        </router-link>
        <a href="https://github.com/nikmcfly/MiroFish-Offline" target="_blank" class="flex items-center gap-2 font-mono text-[0.9rem] font-medium text-white no-underline transition-opacity hover:opacity-80">
          Visit our Github <span>↗</span>
        </a>
      </div>
    </nav>

    <div class="mx-auto max-w-[1400px] px-10 py-[60px] max-md:px-5 max-md:py-8">
      <!-- Hero Section -->
      <section class="relative mb-20 flex justify-between max-lg:flex-col max-md:mb-12">
        <div class="flex-1 pr-[60px] max-lg:mb-10 max-lg:pr-0">
          <div class="mb-6 flex items-center gap-[15px] font-mono text-[0.8rem]">
            <span class="bg-accent px-2.5 py-1 text-[0.75rem] font-bold tracking-[1px] text-white">Offline Multi-Agent Simulation Engine</span>
            <span class="font-medium tracking-[0.5px] text-[#999]">/ v0.1-preview</span>
          </div>

          <h1 class="m-0 mb-10 text-[4.5rem] font-medium leading-[1.2] tracking-[-2px] text-black max-md:mb-7 max-md:text-[2.5rem] max-md:tracking-[-1px]">
            Upload Any Document<br>
            <span class="gradient-text">Predict What Happens Next</span>
          </h1>

          <div class="mb-[50px] max-w-[640px] text-justify text-[1.05rem] font-normal leading-[1.8] text-[#666] max-md:mb-8 max-md:text-[0.95rem]">
            <p class="mb-6">
              From a single document, <span class="font-bold text-black">MiroFish Offline</span> extracts reality seeds and builds a parallel world of <span class="font-mono font-bold text-accent">autonomous AI agents</span> that runs entirely on your machine. Inject variables, observe emergent behavior, and find <span class="rounded-[2px] bg-black/5 px-1.5 py-0.5 font-mono text-[0.9em] font-semibold text-black">"local optima"</span> in complex social dynamics.
            </p>
            <p class="mt-5 border-l-[3px] border-accent pl-4 text-[1.2rem] font-[520] tracking-[1px] text-black">
              Your data never leaves your machine. The future is simulated locally<span class="blinking-cursor font-bold text-accent">_</span>
            </p>
          </div>

          <div class="h-4 w-4 bg-accent"></div>
        </div>

        <div class="flex flex-[0.8] flex-col items-end justify-between max-md:items-start">
          <div class="flex w-full justify-end pr-10 max-md:justify-start max-md:pr-0">
            <img src="../assets/logo/MiroFish_logo_left.jpeg" alt="MiroFish Logo" class="w-full max-w-[500px] max-lg:mb-5 max-lg:max-w-[200px]" />
          </div>
          <button class="flex h-10 w-10 cursor-pointer items-center justify-center border border-[#E5E5E5] bg-transparent text-[1.2rem] text-accent transition-all hover:border-accent max-md:h-11 max-md:w-11" @click="scrollToBottom">↓</button>
        </div>
      </section>

      <!-- Dashboard: Two-Column Layout -->
      <section class="flex items-start gap-[60px] border-t border-[#E5E5E5] pt-[60px] max-lg:flex-col max-md:gap-10 max-md:pt-10">
        <!-- Left Column: Status & Steps -->
        <div class="flex flex-[0.8] flex-col">
          <div class="mb-5 flex items-center gap-2 font-mono text-[0.8rem] text-[#999]">
            <span class="text-[0.8rem] text-accent">■</span> System Status
          </div>

          <h2 class="m-0 mb-4 text-[2rem] font-[520]">Ready</h2>
          <p class="mb-6 leading-[1.6] text-[#666]">
            Local prediction engine on standby. Upload unstructured data to initialize a simulation.
          </p>

          <div class="mb-4 flex gap-5 max-md:flex-wrap">
            <div class="min-w-[150px] border border-[#E5E5E5] px-[30px] py-5 max-md:min-w-0 max-md:flex-[1_1_calc(50%-10px)] max-md:px-5 max-md:py-4">
              <div class="mb-1 font-mono text-[1.8rem] font-[520]">Free</div>
              <div class="text-[0.85rem] text-[#999]">Runs on your hardware</div>
            </div>
            <div class="min-w-[150px] border border-[#E5E5E5] px-[30px] py-5 max-md:min-w-0 max-md:flex-[1_1_calc(50%-10px)] max-md:px-5 max-md:py-4">
              <div class="mb-1 font-mono text-[1.8rem] font-[520]">Private</div>
              <div class="text-[0.85rem] text-[#999]">100% offline, no cloud</div>
            </div>
          </div>

          <div class="relative border border-[#E5E5E5] p-[30px] max-md:p-5">
            <div class="mb-6 flex items-center gap-2 font-mono text-[0.8rem] text-[#999]">
              <span class="text-[1.2rem] leading-none">◇</span> Workflow Sequence
            </div>
            <div class="flex flex-col gap-5">
              <div v-for="(step, i) in steps" :key="i" class="flex items-start gap-5">
                <span class="font-mono font-bold text-black opacity-30">{{ step.num }}</span>
                <div class="flex-1">
                  <div class="mb-1 text-base font-[520]">{{ step.title }}</div>
                  <div class="text-[0.85rem] text-[#666]">{{ step.desc }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Interactive Console -->
        <div class="flex flex-[1.2] flex-col max-lg:w-full">
          <div class="border border-[#CCC] p-2">
            <div class="p-5 max-md:p-3.5">
              <div class="mb-4 flex justify-between font-mono text-[0.75rem] text-[#666]">
                <span>01 / Reality Seeds</span>
                <span>Supported: PDF, MD, TXT</span>
              </div>
              <div
                class="flex h-[200px] cursor-pointer items-center justify-center overflow-y-auto border border-dashed bg-[#FAFAFA] transition-all duration-300 hover:border-[#999] hover:bg-[#F0F0F0]"
                :class="isDragOver ? 'border-accent bg-[#F0F0F0]' : 'border-[#CCC]'"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input ref="fileInput" type="file" multiple accept=".pdf,.md,.txt" @change="handleFileSelect" style="display: none" :disabled="loading" />
                <div v-if="files.length === 0" class="text-center">
                  <div class="mx-auto mb-4 flex h-10 w-10 items-center justify-center border border-[#DDD] text-[#999]">↑</div>
                  <div class="mb-1 text-[0.9rem] font-medium">Drag & drop files here</div>
                  <div class="font-mono text-[0.75rem] text-[#999]">or click to browse</div>
                </div>
                <div v-else class="flex w-full flex-col gap-2.5 self-start p-4">
                  <div v-for="(file, index) in files" :key="index" class="flex items-center border border-[#EEE] bg-white px-3 py-2 font-mono text-[0.85rem]">
                    <span>📄</span>
                    <span class="mx-2.5 flex-1">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="cursor-pointer border-none bg-transparent text-[1.2rem] text-[#999]">×</button>
                  </div>
                </div>
              </div>
            </div>

            <div class="my-2.5 flex items-center border-t border-[#EEE]"><span class="px-4 font-mono text-[0.7rem] tracking-[1px] text-[#BBB]">Parameters</span></div>

            <div class="p-5 max-md:p-3.5">
              <div class="mb-4 flex justify-between font-mono text-[0.75rem] text-[#666]">
                <span>>_ 02 / Simulation Prompt</span>
              </div>
              <div class="relative border border-[#DDD] bg-[#FAFAFA]">
                <textarea v-model="formData.simulationRequirement" class="min-h-[150px] w-full resize-y border-none bg-transparent p-5 font-mono text-[0.9rem] leading-[1.6] outline-none max-md:p-3.5" placeholder="// Describe your simulation or prediction goal in natural language" rows="6" :disabled="loading"></textarea>
                <div class="absolute bottom-2.5 right-4 font-mono text-[0.7rem] text-[#AAA]">Engine: OpenRouter + Neo4j</div>
              </div>
            </div>

            <div class="px-5 pb-5">
              <button class="start-engine-btn flex w-full items-center justify-between p-5 font-mono text-[1.1rem] font-bold tracking-[1px] text-white max-md:p-4 max-md:text-base" @click="startSimulation" :disabled="!canSubmit || loading">
                <span v-if="!loading">Start Engine</span>
                <span v-else>Initializing...</span>
                <span>→</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'

const steps = [
  { num: '01', title: 'Graph Build', desc: 'Extract reality seeds from your document, build knowledge graph with Neo4j + GraphRAG' },
  { num: '02', title: 'Env Setup', desc: 'Generate agent personas, configure simulation parameters via LLM' },
  { num: '03', title: 'Simulation', desc: 'Run multi-agent simulation locally with dynamic memory updates and emergent behavior' },
  { num: '04', title: 'Report', desc: 'ReportAgent analyzes the simulation results and generates a detailed prediction report' },
  { num: '05', title: 'Interaction', desc: 'Chat with any agent from the simulated world or discuss findings with ReportAgent' },
]

const router = useRouter()

const formData = ref({ simulationRequirement: '' })
const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const fileInput = ref(null)

const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

const triggerFileInput = () => { if (!loading.value) fileInput.value?.click() }
const handleFileSelect = (event) => { addFiles(Array.from(event.target.files)) }
const handleDragOver = () => { isDragOver.value = true }
const handleDragLeave = () => { isDragOver.value = false }
const handleDrop = (e) => { isDragOver.value = false; addFiles(Array.from(e.dataTransfer.files)) }

const addFiles = (newFiles) => {
  const allowed = ['.pdf', '.md', '.txt']
  const valid = newFiles.filter(f => allowed.some(ext => f.name.toLowerCase().endsWith(ext)))
  files.value = [...files.value, ...valid]
}

const removeFile = (index) => { files.value.splice(index, 1) }

const scrollToBottom = () => { window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }) }

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
}
</script>

<style scoped>
/* Only what utilities cannot express: animations, gradient text clipping,
   and the multi-state engine button. Everything else is Tailwind classes. */
.gradient-text {
  background: linear-gradient(90deg, #000 0%, #444 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.blinking-cursor {
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.start-engine-btn:not(:disabled) {
  background: #000;
  border: 1px solid #000;
  cursor: pointer;
  animation: pulse-border 2s infinite;
  transition: all 0.2s;
}

.start-engine-btn:hover:not(:disabled) {
  background: #FF4500;
  border-color: #FF4500;
  transform: translateY(-2px);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #E5E5E5;
  color: #999;
  cursor: not-allowed;
  border: 1px solid #E5E5E5;
}

@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); }
  70% { box-shadow: 0 0 0 6px rgba(0, 0, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
}
</style>
