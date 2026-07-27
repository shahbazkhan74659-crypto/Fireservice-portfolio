import { describe, expect, it, vi } from 'vitest'
import { extractFirstErrorMessage, NETWORK_ERROR_MESSAGE, readErrorMessage } from './api'

describe('extractFirstErrorMessage', () => {
  it('returns the first message of the first field in a DRF-style error body', () => {
    expect(extractFirstErrorMessage({ phone: ['Please enter a valid phone number.'] }))
      .toBe('Please enter a valid phone number.')
  })

  it('returns null for null', () => {
    expect(extractFirstErrorMessage(null)).toBeNull()
  })

  it('returns null for a non-object', () => {
    expect(extractFirstErrorMessage('just a string')).toBeNull()
  })

  it('returns null for an empty object', () => {
    expect(extractFirstErrorMessage({})).toBeNull()
  })

  it('returns null when the first field value is not an array of strings', () => {
    expect(extractFirstErrorMessage({ detail: 'not an array' })).toBeNull()
    expect(extractFirstErrorMessage({ detail: [] })).toBeNull()
    expect(extractFirstErrorMessage({ detail: [42] })).toBeNull()
  })

  it('reads the AdminHubLoginAPIView-style {"detail": [...]} shape too', () => {
    expect(extractFirstErrorMessage({ detail: ['Invalid username or password.'] }))
      .toBe('Invalid username or password.')
  })
})

describe('readErrorMessage', () => {
  it('extracts the field message from a well-formed error response', async () => {
    const res = new Response(JSON.stringify({ email: ['Enter a valid email address.'] }), { status: 400 })
    expect(await readErrorMessage(res)).toBe('Enter a valid email address.')
  })

  it('falls back to the default message when the body has no usable field error', async () => {
    const res = new Response(JSON.stringify({}), { status: 500 })
    expect(await readErrorMessage(res)).toBe('Something went wrong. Please try again or call us directly.')
  })

  it('falls back to the default message when the body is not valid JSON', async () => {
    const res = new Response('not json', { status: 500 })
    expect(await readErrorMessage(res)).toBe('Something went wrong. Please try again or call us directly.')
  })

  it('falls back to the default message when res.json() itself throws', async () => {
    const res = { json: vi.fn().mockRejectedValue(new Error('boom')) } as unknown as Response
    expect(await readErrorMessage(res)).toBe('Something went wrong. Please try again or call us directly.')
  })
})

describe('NETWORK_ERROR_MESSAGE', () => {
  it('is a non-empty, human-readable string', () => {
    expect(NETWORK_ERROR_MESSAGE.length).toBeGreaterThan(0)
  })
})
