import { createApp, ref } from './vue.esm-browser.js'

const app = createApp({
    setup() {
        const message = ref('Hello vue!')
        return {
            message
        }
    }
}).mount('#app')
