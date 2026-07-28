import { describe, expect, it } from 'vitest'
import { forgotPasswordEmailSchema, forgotPasswordOtpSchema, forgotPasswordResetSchema } from './forgotPasswordSchema'

describe('forgotPasswordEmailSchema', () => {
  it('accepts a valid email via the shared emailSchema', () => {
    expect(forgotPasswordEmailSchema.safeParse({ email: 'jane@example.com' }).success).toBe(true)
  })

  it('rejects a malformed email', () => {
    expect(forgotPasswordEmailSchema.safeParse({ email: 'not-an-email' }).success).toBe(false)
  })
})

describe('forgotPasswordOtpSchema', () => {
  it('accepts a 6-digit code', () => {
    expect(forgotPasswordOtpSchema.safeParse({ otp: '123456' }).success).toBe(true)
  })

  it.each(['12345', '1234567', 'abcdef', '12345a'])('rejects a malformed code: %s', (otp) => {
    expect(forgotPasswordOtpSchema.safeParse({ otp }).success).toBe(false)
  })

  it('trims surrounding whitespace before validating', () => {
    expect(forgotPasswordOtpSchema.safeParse({ otp: ' 123456 ' }).success).toBe(true)
  })
})

describe('forgotPasswordResetSchema', () => {
  const VALID = { new_password: 'Strong-Pass1!', confirm_password: 'Strong-Pass1!' }

  it('accepts matching, strong passwords', () => {
    expect(forgotPasswordResetSchema.safeParse(VALID).success).toBe(true)
  })

  it('rejects mismatched passwords', () => {
    const result = forgotPasswordResetSchema.safeParse({ ...VALID, confirm_password: 'Different-Pass1!' })
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues.some((i) => i.path[0] === 'confirm_password')).toBe(true)
    }
  })

  it('rejects a weak new_password via the shared passwordStrengthSchema', () => {
    expect(forgotPasswordResetSchema.safeParse({ new_password: 'weak', confirm_password: 'weak' }).success).toBe(false)
  })
})
