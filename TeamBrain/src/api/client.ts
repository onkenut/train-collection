const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

interface RequestOptions {
  method?: string
  body?: any
  headers?: Record<string, string>
  params?: Record<string, string | number | boolean | null | undefined>
}

class ApiError extends Error {
  status: number
  data: any

  constructor(message: string, status: number, data?: any) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

function buildURL(path: string, params?: Record<string, string | number | boolean | null | undefined>): string {
  const url = new URL(`${BASE_URL}${path}`, window.location.origin)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        url.searchParams.set(key, String(value))
      }
    })
  }
  return url.toString()
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, params } = options

  const url = buildURL(path, params)
  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  }

  if (body && method !== 'GET') {
    config.body = JSON.stringify(body)
  }

  const response = await fetch(url, config)

  if (!response.ok) {
    let errorData: any
    try {
      errorData = await response.json()
    } catch {
      errorData = { message: response.statusText }
    }
    throw new ApiError(
      errorData.message || errorData.detail || `Request failed with status ${response.status}`,
      response.status,
      errorData
    )
  }

  if (response.status === 204) return undefined as T

  return response.json()
}

export const api = {
  get: <T>(path: string, params?: Record<string, string | number | boolean | null | undefined>) =>
    request<T>(path, { method: 'GET', params }),

  post: <T>(path: string, body?: any) =>
    request<T>(path, { method: 'POST', body }),

  put: <T>(path: string, body?: any) =>
    request<T>(path, { method: 'PUT', body }),

  delete: <T>(path: string) =>
    request<T>(path, { method: 'DELETE' }),

  upload: async <T>(path: string, formData: FormData): Promise<T> => {
    const url = buildURL(path)
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      let errorData: any
      try { errorData = await response.json() } catch { errorData = { message: response.statusText } }
      throw new ApiError(errorData.message || `Upload failed with status ${response.status}`, response.status, errorData)
    }
    return response.json()
  },
}

export { ApiError, BASE_URL }
export default api
