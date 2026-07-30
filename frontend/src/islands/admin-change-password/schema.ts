import { z } from 'zod'
import { emailSchema, passwordStrengthSchema, PASSWORD_REQUIREMENTS_HINT } from '../../lib/validators'

export { PASSWORD_REQUIREMENTS_HINT }

// Mirrors this project's own (deliberately space-permitting) username rules
// loosely — real enforcement happens server-side via
// core.serializers.ChangeUsernameSerializer, same UX-only convention below.
// confirm_username exists purely to catch a mistyped new username before it
// gets saved — since it changes the login credential itself, a silent typo
// here (unlike most form fields) can lock the account out with no easy way
// to recover the intended value, since it's never hashed/unrecoverable the
// way a password is anyway, but there's no "forgot username" flow either.
export const changeUsernameSchema = z
  .object({
    new_username: z.string().min(1, 'Enter a username.').max(150, 'Too long (max 150 characters).'),
    confirm_username: z.string().min(1, 'Confirm your new username.'),
  })
  .refine((data) => data.new_username === data.confirm_username, {
    message: 'Usernames do not match.',
    path: ['confirm_username'],
  })

export type ChangeUsernameInput = z.infer<typeof changeUsernameSchema>
export type ChangeUsernameErrors = Partial<Record<keyof ChangeUsernameInput, string>>

export const changePasswordSchema = z
  .object({
    old_password: z.string().min(1, 'Enter your current password.'),
    new_password: passwordStrengthSchema,
    confirm_password: z.string().min(1, 'Confirm your new password.'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Passwords do not match.',
    path: ['confirm_password'],
  })

export type ChangePasswordInput = z.infer<typeof changePasswordSchema>
export type ChangePasswordErrors = Partial<Record<keyof ChangePasswordInput, string>>

export const changeEmailRequestSchema = z.object({
  new_email: emailSchema,
})
export type ChangeEmailRequestInput = z.infer<typeof changeEmailRequestSchema>
export type ChangeEmailRequestErrors = Partial<Record<keyof ChangeEmailRequestInput, string>>

export const changeEmailOtpSchema = z.object({
  otp: z.string().trim().regex(/^\d{6}$/, 'Enter the 6-digit code.'),
})
export type ChangeEmailOtpInput = z.infer<typeof changeEmailOtpSchema>
export type ChangeEmailOtpErrors = Partial<Record<keyof ChangeEmailOtpInput, string>>
