import { afterEach, describe, expect, it } from 'vitest'
import { getCookie, getCsrfToken } from './csrf'

function setCookies(raw: string) {
  document.cookie = raw
}

function clearAllCookies() {
  document.cookie.split(';').forEach((c) => {
    const name = c.split('=')[0].trim()
    if (name) document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT`
  })
}

describe('getCookie', () => {
  afterEach(() => {
    clearAllCookies()
  })

  it('reads a cookie by name among several', () => {
    setCookies('foo=bar')
    setCookies('csrftoken=abc123')
    expect(getCookie('csrftoken')).toBe('abc123')
  })

  it('returns null when the cookie is not present', () => {
    setCookies('foo=bar')
    expect(getCookie('missing')).toBeNull()
  })

  it('URL-decodes the value', () => {
    setCookies(`csrftoken=${encodeURIComponent('abc/123+xyz')}`)
    expect(getCookie('csrftoken')).toBe('abc/123+xyz')
  })
})

describe('getCsrfToken', () => {
  afterEach(() => {
    clearAllCookies()
  })

  it('returns the csrftoken cookie value when present', () => {
    setCookies('csrftoken=xyz789')
    expect(getCsrfToken()).toBe('xyz789')
  })

  it('throws a readable error when the cookie is missing', () => {
    expect(() => getCsrfToken()).toThrow(/CSRF cookie not found/)
  })
})
