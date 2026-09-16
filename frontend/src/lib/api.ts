type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface RequestOptions {
  method?: Method
  body?: unknown
  signal?: AbortSignal
}

export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown
  /** From the `Retry-After` header (in seconds), sent with `429 Too Many Requests`. */
  readonly retryAfterSeconds: number | null

  constructor(status: number, detail: unknown, retryAfterSeconds: number | null = null) {
    super(typeof detail === 'string' ? detail : `Request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
    this.retryAfterSeconds = retryAfterSeconds
  }
}

function readRetryAfter(response: Response): number | null {
  const seconds = Number(response.headers.get('Retry-After') ?? Number.NaN)
  return Number.isInteger(seconds) && seconds >= 0 ? seconds : null
}

async function readDetail(response: Response): Promise<unknown> {
  try {
    const payload = (await response.json()) as { detail?: unknown }
    return payload.detail
  } catch {
    return undefined
  }
}

/** Calls the backend through the same-origin `/api` prefix, sending and receiving JSON. */
export async function apiFetch<T>(
  path: string,
  { method = 'GET', body, signal }: RequestOptions = {},
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method,
    signal,
    credentials: 'same-origin',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await readDetail(response), readRetryAfter(response))
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}
