const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
    ...options,
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const data = await response.json()
      message = data.detail ?? message
    } catch {
      // Keep the generic message.
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return null
  }
  return response.json()
}

export function fetchHealth() {
  return request('/health')
}

export function fetchMetricsSummary() {
  return request('/metrics/summary')
}

export function recommendPois(payload) {
  return request('/recommendations/pois', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function planTrip(payload) {
  return request('/trips/plan', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function runPipeline(payload) {
  return request('/pipeline/plan', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function runEvaluation(payload) {
  return request('/evaluations/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
