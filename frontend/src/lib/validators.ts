import { z } from 'zod'

/** Shared full-name validation used by both the survey and contact forms. */
export const nameSchema = z.string().trim()
  .min(2, 'Please enter your full name.')
  .max(120, 'Name is too long (max 120 characters).')

/** Shared email validation used by both the survey and contact forms. */
export const emailSchema = z.string().trim()
  .min(1, 'Email is required.')
  .email('Enter a valid email address.')
  .max(254, 'Email is too long.')
