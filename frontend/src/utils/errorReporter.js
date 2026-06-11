// Forwards browser-side errors to the backend log (/api/logs/frontend) so
// they are visible in one place. Rate-limited and fire-and-forget: reporting
// must never break the app or flood the backend.

const MAX_REPORTS_PER_MINUTE = 10
let reportTimestamps = []

function report(message, source, stack) {
  const now = Date.now()
  reportTimestamps = reportTimestamps.filter(t => now - t < 60_000)
  if (reportTimestamps.length >= MAX_REPORTS_PER_MINUTE) return
  reportTimestamps.push(now)

  try {
    fetch('/api/logs/frontend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: String(message || '').slice(0, 2000),
        source: String(source || '').slice(0, 500),
        stack: String(stack || '').slice(0, 4000)
      })
    }).catch(() => {})
  } catch {
    // never let error reporting throw
  }
}

export function installErrorReporter(app) {
  app.config.errorHandler = (err, instance, info) => {
    console.error('Vue error:', err, info)
    report(err?.message || err, `vue:${info}`, err?.stack)
  }

  window.addEventListener('error', (event) => {
    report(event.message, `${event.filename}:${event.lineno}`, event.error?.stack)
  })

  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason
    report(reason?.message || String(reason), 'unhandledrejection', reason?.stack)
  })
}

export { report as reportError }
