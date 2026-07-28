import { z } from 'zod'

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

// Client-side checks are UX only — the real password rules (length,
// similarity to user attributes, common-password list, not-all-numeric, plus
// the uppercase/special-character/no-whitespace rules mirrored below) are
// enforced server-side via Django's AUTH_PASSWORD_VALIDATORS (including the
// custom core.password_validators trio) through
// core.serializers.ChangePasswordSerializer, same "Zod is UX only, never the
// trust boundary" convention used by every other form island in this app.
export const PASSWORD_REQUIREMENTS_HINT =
  'At least 8 characters, with one uppercase letter, one special character (e.g. ! @ # $ %), and no spaces.'

export const changePasswordSchema = z
  .object({
    old_password: z.string().min(1, 'Enter your current password.'),
    new_password: z
      .string()
      .min(8, 'Must be at least 8 characters.')
      .regex(/[A-Z]/, 'Must contain at least one uppercase letter.')
      .regex(/[^A-Za-z0-9\s]/, 'Must contain at least one special character.')
      .refine((v) => !/\s/.test(v), 'Must not contain spaces.'),
    confirm_password: z.string().min(1, 'Confirm your new password.'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Passwords do not match.',
    path: ['confirm_password'],
  })

export type ChangePasswordInput = z.infer<typeof changePasswordSchema>
export type ChangePasswordErrors = Partial<Record<keyof ChangePasswordInput, string>>
