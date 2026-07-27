import { describe, expect, it } from 'vitest'
import { contactMessageSchema, SERVICE_OPTIONS } from './schema'

const VALID = {
  name: 'Jane Doe',
  phone: '9876543210',
  email: 'jane@example.com',
  service: SERVICE_OPTIONS[0].value,
  message: 'Looking for a quote.',
}

describe('contactMessageSchema', () => {
  it('accepts a fully valid payload', () => {
    expect(contactMessageSchema.safeParse(VALID).success).toBe(true)
  })

  it('accepts every declared service option', () => {
    for (const option of SERVICE_OPTIONS) {
      const result = contactMessageSchema.safeParse({ ...VALID, service: option.value })
      expect(result.success).toBe(true)
    }
  })

  it('rejects a service value not in SERVICE_OPTIONS', () => {
    const result = contactMessageSchema.safeParse({ ...VALID, service: 'not_a_real_service' })
    expect(result.success).toBe(false)
  })

  it('message is optional', () => {
    const { message, ...rest } = VALID
    expect(contactMessageSchema.safeParse(rest).success).toBe(true)
  })

  it('rejects a message over 2000 characters', () => {
    const result = contactMessageSchema.safeParse({ ...VALID, message: 'a'.repeat(2001) })
    expect(result.success).toBe(false)
  })

  it('rejects an invalid phone number via the shared phoneSchema', () => {
    expect(contactMessageSchema.safeParse({ ...VALID, phone: '123' }).success).toBe(false)
  })

  it('rejects an invalid email via the shared emailSchema', () => {
    expect(contactMessageSchema.safeParse({ ...VALID, email: 'not-an-email' }).success).toBe(false)
  })
})
