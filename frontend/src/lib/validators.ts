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

/** Shared phone validation used by the contact and consultation forms. */
export const phoneSchema = z.string().trim()
  .min(1, 'Phone number is required.')
  .max(20, 'Phone number is too long.')
  .refine((v) => v.replace(/\D/g, '').length >= 7, 'Please enter a valid phone number.')

/** Shared entity-name validation used by every Admin Hub Add/Edit form. */
export const entityNameField = z.string().trim()
  .min(2, 'Name is required.')
  .max(120, 'Name is too long (max 120 characters).')

/**
 * Client-side checks are UX only — the real password rules (length,
 * similarity to user attributes, common-password list, not-all-numeric, plus
 * the uppercase/special-character/no-whitespace rules mirrored below) are
 * enforced server-side via Django's AUTH_PASSWORD_VALIDATORS (including the
 * custom core.password_validators trio), same "Zod is UX only, never the
 * trust boundary" convention used by every form island in this app. Shared
 * by the Account Settings change-password form and the Forgot Password
 * flow's reset step, which both need the exact same rules.
 */
export const PASSWORD_REQUIREMENTS_HINT =
  'At least 8 characters, with one uppercase letter, one special character (e.g. ! @ # $ %), and no spaces.'

export const passwordStrengthSchema = z.string()
  .min(8, 'Must be at least 8 characters.')
  .regex(/[A-Z]/, 'Must contain at least one uppercase letter.')
  .regex(/[^A-Za-z0-9\s]/, 'Must contain at least one special character.')
  .refine((v) => !/\s/.test(v), 'Must not contain spaces.')

/**
 * Factory for an image-upload Zod schema, parametrized by the caller's own
 * size cap / accepted MIME types / messages so each Admin Hub island can
 * keep its exact existing validation behavior (e.g. certifications rejects
 * SVG, everything else accepts it) while sharing the refinement logic.
 */
export function imageFileSchema(
  maxBytes: number,
  acceptedTypes: string[],
  typeErrorMessage: string,
  requiredMessage = 'Please choose an image file.',
) {
  function checkImageFile(file: File, ctx: z.RefinementCtx) {
    if (file.size > maxBytes) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Image is too large (max ${maxBytes / (1024 * 1024)}MB).`,
      })
    }
    if (!acceptedTypes.includes(file.type)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: typeErrorMessage })
    }
  }
  return z.instanceof(File, { message: requiredMessage }).superRefine(checkImageFile)
}
