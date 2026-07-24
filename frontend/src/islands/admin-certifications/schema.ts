import { z } from 'zod'

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp']

const nameField = z.string().trim()
  .min(2, 'Name is required.')
  .max(120, 'Name is too long (max 120 characters).')

const descriptionField = z.string().trim()
  .min(2, 'Description is required.')
  .max(200, 'Description is too long (max 200 characters).')

const metaField = z.string().trim()
  .min(2, 'This field is required.')
  .max(200, 'Too long (max 200 characters).')

function checkImageFile(file: File, ctx: z.RefinementCtx) {
  if (file.size > MAX_IMAGE_SIZE_BYTES) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Image is too large (max 5MB).' })
  }
  if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Unsupported image type. Use PNG, JPEG or WebP.' })
  }
}

export const addCertificationSchema = z.object({
  name: nameField,
  description: descriptionField,
  meta: metaField,
  image: z.instanceof(File, { message: 'Please choose an image file.' }).superRefine(checkImageFile),
})
export type AddCertificationInput = z.infer<typeof addCertificationSchema>
export type AddCertificationErrors = Partial<Record<keyof AddCertificationInput, string>>

export interface Certification {
  id: number
  name: string
  description: string
  meta: string
  image: string
  order: number
}
