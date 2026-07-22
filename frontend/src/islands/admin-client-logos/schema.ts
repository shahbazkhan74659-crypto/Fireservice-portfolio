import { z } from 'zod'

const MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']

const nameField = z.string().trim()
  .min(2, 'Name is required.')
  .max(120, 'Name is too long (max 120 characters).')

function checkImageFile(file: File, ctx: z.RefinementCtx) {
  if (file.size > MAX_LOGO_SIZE_BYTES) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Image is too large (max 5MB).' })
  }
  if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Unsupported image type. Use PNG, JPEG, WebP or SVG.' })
  }
}

export const addClientLogoSchema = z.object({
  name: nameField,
  image: z.instanceof(File, { message: 'Please choose an image file.' }).superRefine(checkImageFile),
})
export type AddClientLogoInput = z.infer<typeof addClientLogoSchema>
export type AddClientLogoErrors = Partial<Record<keyof AddClientLogoInput, string>>

export const editClientLogoSchema = z.object({
  name: nameField,
  image: z.instanceof(File).superRefine(checkImageFile).optional(),
})
export type EditClientLogoInput = z.infer<typeof editClientLogoSchema>
export type EditClientLogoErrors = Partial<Record<keyof EditClientLogoInput, string>>

export interface ClientLogo {
  id: number
  name: string
  image: string
  order: number
}
