import { useMutation } from '@tanstack/react-query'
import { apiFetch } from '@/lib/api'

export interface FeedbackIn {
  message: string
  /** The screen the person was on before opening their account, e.g. `/entrenar`. */
  page: string | null
}

export function useSendFeedback() {
  return useMutation({
    mutationFn: (feedback: FeedbackIn) => apiFetch<void>('/feedback', { method: 'POST', body: feedback }),
  })
}
