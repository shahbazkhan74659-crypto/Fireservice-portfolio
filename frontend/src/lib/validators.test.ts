import { describe, expect, it } from 'vitest'
import { emailSchema, entityNameField, imageFileSchema, nameSchema, passwordStrengthSchema, phoneSchema } from './validators'

describe('nameSchema', () => {
  it('trims and accepts a valid name', () => {
    expect(nameSchema.parse('  Jane Doe  ')).toBe('Jane Doe')
  })

  it('rejects a single character', () => {
    expect(nameSchema.safeParse('J').success).toBe(false)
  })

  it('rejects a name over 120 characters', () => {
    expect(nameSchema.safeParse('a'.repeat(121)).success).toBe(false)
  })
})

describe('emailSchema', () => {
  it('accepts a valid email', () => {
    expect(emailSchema.parse('jane@example.com')).toBe('jane@example.com')
  })

  it('rejects an empty string', () => {
    expect(emailSchema.safeParse('').success).toBe(false)
  })

  it('rejects a malformed email', () => {
    expect(emailSchema.safeParse('not-an-email').success).toBe(false)
  })
})

describe('phoneSchema', () => {
  it.each(['9876543210', '+91 98765 43210', '(987) 654-3210'])(
    'accepts a phone number with at least 7 digits: %s',
    (value) => {
      expect(phoneSchema.safeParse(value).success).toBe(true)
    },
  )

  it.each(['12345', 'abcdef', '123-456'])(
    'rejects a phone number with fewer than 7 digits: %s',
    (value) => {
      expect(phoneSchema.safeParse(value).success).toBe(false)
    },
  )

  it('rejects an empty string', () => {
    expect(phoneSchema.safeParse('').success).toBe(false)
  })
})

describe('entityNameField', () => {
  it('trims and accepts a valid name', () => {
    expect(entityNameField.parse('  Acme Corp  ')).toBe('Acme Corp')
  })

  it('rejects a single character', () => {
    expect(entityNameField.safeParse('A').success).toBe(false)
  })
})

describe('passwordStrengthSchema', () => {
  it('accepts a password meeting every rule', () => {
    expect(passwordStrengthSchema.safeParse('Strong-Pass1!').success).toBe(true)
  })

  it('rejects a password under 8 characters', () => {
    expect(passwordStrengthSchema.safeParse('Sh0rt!').success).toBe(false)
  })

  it('rejects a password with no uppercase letter', () => {
    expect(passwordStrengthSchema.safeParse('lowercase-pass1!').success).toBe(false)
  })

  it('rejects a password with no special character', () => {
    expect(passwordStrengthSchema.safeParse('NoSpecialChar123').success).toBe(false)
  })

  it('rejects a password containing whitespace', () => {
    expect(passwordStrengthSchema.safeParse('Has A Space1!').success).toBe(false)
  })
})

describe('imageFileSchema', () => {
  const schema = imageFileSchema(1024, ['image/png', 'image/jpeg'], 'Unsupported file type.')

  it('accepts a file within the size cap and an accepted type', () => {
    const file = new File(['a'.repeat(100)], 'test.png', { type: 'image/png' })
    expect(schema.safeParse(file).success).toBe(true)
  })

  it('rejects a file over the size cap', () => {
    const file = new File(['a'.repeat(2000)], 'test.png', { type: 'image/png' })
    const result = schema.safeParse(file)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues.some((i) => i.message.includes('too large'))).toBe(true)
    }
  })

  it('rejects an unaccepted file type with the caller-supplied message', () => {
    const file = new File(['a'], 'test.svg', { type: 'image/svg+xml' })
    const result = schema.safeParse(file)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues.some((i) => i.message === 'Unsupported file type.')).toBe(true)
    }
  })

  it('rejects a non-File value', () => {
    expect(schema.safeParse('not a file').success).toBe(false)
  })
})
