import { z } from 'zod'

const MAX_ICON_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']

const nameField = z.string().trim()
  .min(2, 'Name is required.')
  .max(120, 'Name is too long (max 120 characters).')

const descriptionField = z.string().trim()
  .min(10, 'Description must be at least 10 characters.')

function checkImageFile(file: File, ctx: z.RefinementCtx) {
  if (file.size > MAX_ICON_SIZE_BYTES) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Image is too large (max 5MB).' })
  }
  if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Unsupported image type. Use PNG, JPEG, WebP or SVG.' })
  }
}

export const addServiceSchema = z.object({
  name: nameField,
  description: descriptionField,
  icon: z.instanceof(File, { message: 'Please choose an icon image.' }).superRefine(checkImageFile),
})
export type AddServiceInput = z.infer<typeof addServiceSchema>
export type AddServiceErrors = Partial<Record<keyof AddServiceInput, string>>

export const editServiceSchema = z.object({
  name: nameField,
  description: descriptionField,
  icon: z.instanceof(File).superRefine(checkImageFile).optional(),
})
export type EditServiceInput = z.infer<typeof editServiceSchema>
export type EditServiceErrors = Partial<Record<keyof EditServiceInput, string>>

export interface Service {
  id: number
  name: string
  description: string
  icon: string
  order: number
}
