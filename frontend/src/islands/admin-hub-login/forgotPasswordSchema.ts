import { z } from 'zod'
import { emailSchema, passwordStrengthSchema, PASSWORD_REQUIREMENTS_HINT } from '../../lib/validators'

export { PASSWORD_REQUIREMENTS_HINT }

export const forgotPasswordEmailSchema = z.object({ email: emailSchema })
export type ForgotPasswordEmailInput = z.infer<typeof forgotPasswordEmailSchema>
export type ForgotPasswordEmailErrors = Partial<Record<keyof ForgotPasswordEmailInput, string>>

export const forgotPasswordOtpSchema = z.object({
  otp: z.string().trim().regex(/^\d{6}$/, 'Enter the 6-digit code.'),
})
export type ForgotPasswordOtpInput = z.infer<typeof forgotPasswordOtpSchema>
export type ForgotPasswordOtpErrors = Partial<Record<keyof ForgotPasswordOtpInput, string>>

// No reset_token field — that's carried in component state, not typed by the
// admin, so it has nothing to do with this form's own validation.
export const forgotPasswordResetSchema = z
  .object({
    new_password: passwordStrengthSchema,
    confirm_password: z.string().min(1, 'Confirm your new password.'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Passwords do not match.',
    path: ['confirm_password'],
  })
export type ForgotPasswordResetInput = z.infer<typeof forgotPasswordResetSchema>
export type ForgotPasswordResetErrors = Partial<Record<keyof ForgotPasswordResetInput, string>>
