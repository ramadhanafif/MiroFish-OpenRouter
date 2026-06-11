import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './tailwind.css'
import './legacy-global.css'
import { installErrorReporter } from './utils/errorReporter'

const app = createApp(App)

installErrorReporter(app)
app.use(router)

app.mount('#app')
