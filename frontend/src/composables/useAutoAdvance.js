import { ref, onUnmounted } from 'vue'

/**
 * Countdown that fires `action` after `seconds` unless cancelled.
 * Used to auto-advance workflow steps so a full run (ontology to report)
 * needs no human interaction, while still giving the user a window to
 * cancel and stay on the current step.
 *
 * Returns:
 *   countdown - ref, remaining seconds or null when inactive
 *   start()   - begin the countdown (no-op if already running)
 *   cancel()  - stop the countdown and clear the display
 */
export function useAutoAdvance(action, seconds = 10) {
  const countdown = ref(null)
  let timer = null

  const cancel = () => {
    if (timer) clearInterval(timer)
    timer = null
    countdown.value = null
  }

  const start = () => {
    if (timer) return
    countdown.value = seconds
    timer = setInterval(() => {
      countdown.value -= 1
      if (countdown.value <= 0) {
        cancel()
        action()
      }
    }, 1000)
  }

  onUnmounted(cancel)

  return { countdown, start, cancel }
}
