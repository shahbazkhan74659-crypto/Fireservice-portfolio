/**
 * Parses a DRF-style validation error response body (e.g.
 * `{ "field": ["message"] }`) and returns the first field's first message,
 * or null if the shape doesn't match what's expected.
 */
export function extractFirstErrorMessage(data: unknown): string | null {
  if (!data || typeof data !== 'object') return null
  const first = Object.values(data as Record<string, unknown>)[0]
  if (Array.isArray(first) && typeof first[0] === 'string') return first[0]
  return null
}

const DEFAULT_ERROR_MESSAGE = 'Something went wrong. Please try again or call us directly.'

/**
 * Shared fallback message shown when a `fetch()` call itself throws (offline,
 * DNS failure, etc.) rather than the server responding with an error body.
 */
export const NETWORK_ERROR_MESSAGE = 'Network error. Check your connection and try again.'

/**
 * Reads an error message out of a failed fetch Response's JSON body,
 * falling back to a generic message if the body can't be parsed or doesn't
 * contain a usable field error.
 */
export async function readErrorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json()
    const message = extractFirstErrorMessage(data)
    if (message) return message
  } catch {
    // keep default message
  }
  return DEFAULT_ERROR_MESSAGE
}
