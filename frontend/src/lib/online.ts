import { useSyncExternalStore } from 'react'

function subscribe(onChange: () => void) {
  window.addEventListener('online', onChange)
  window.addEventListener('offline', onChange)
  return () => {
    window.removeEventListener('online', onChange)
    window.removeEventListener('offline', onChange)
  }
}

/** Whether the device reports a connection. A `true` only means a request is worth trying. */
export function isOnline(): boolean {
  return window.navigator.onLine
}

/** Re-renders on the browser's `online` and `offline` events. */
export function useOnline(): boolean {
  return useSyncExternalStore(subscribe, isOnline, () => true)
}
