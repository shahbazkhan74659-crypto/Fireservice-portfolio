import { z } from 'zod'
import { entityNameField, imageFileSchema } from '../../lib/validators'

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG or WebP.'

const descriptionField = z.string().trim()
  .min(2, 'Description is required.')
  .max(200, 'Description is too long (max 200 characters).')

const metaField = z.string().trim()
  .min(2, 'This field is required.')
  .max(200, 'Too long (max 200 characters).')

export const addCertificationSchema = z.object({
  name: entityNameField,
  description: descriptionField,
  meta: metaField,
  image: imageFileSchema(MAX_IMAGE_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR),
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
