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

export const addBrandSchema = z.object({
  name: nameField,
  image: z.instanceof(File, { message: 'Please choose an image file.' }).superRefine(checkImageFile),
})
export type AddBrandInput = z.infer<typeof addBrandSchema>
export type AddBrandErrors = Partial<Record<keyof AddBrandInput, string>>

export const editBrandSchema = z.object({
  name: nameField,
  image: z.instanceof(File).superRefine(checkImageFile).optional(),
})
export type EditBrandInput = z.infer<typeof editBrandSchema>
export type EditBrandErrors = Partial<Record<keyof EditBrandInput, string>>

export interface Brand {
  id: number
  name: string
  image: string
  order: number
}
