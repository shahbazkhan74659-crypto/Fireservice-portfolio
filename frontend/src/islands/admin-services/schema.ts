import { z } from 'zod'
import { entityNameField, imageFileSchema } from '../../lib/validators'

const MAX_ICON_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG, WebP or SVG.'

const descriptionField = z.string().trim()
  .min(10, 'Description must be at least 10 characters.')

export const addServiceSchema = z.object({
  name: entityNameField,
  description: descriptionField,
  icon: imageFileSchema(MAX_ICON_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR, 'Please choose an icon image.'),
})
export type AddServiceInput = z.infer<typeof addServiceSchema>
export type AddServiceErrors = Partial<Record<keyof AddServiceInput, string>>

export const editServiceSchema = z.object({
  name: entityNameField,
  description: descriptionField,
  icon: imageFileSchema(MAX_ICON_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR, 'Please choose an icon image.').optional(),
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
