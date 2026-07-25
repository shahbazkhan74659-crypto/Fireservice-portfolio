import { z } from 'zod'
import { entityNameField, imageFileSchema } from '../../lib/validators'

const MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG, WebP or SVG.'

export const addBrandSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR),
})
export type AddBrandInput = z.infer<typeof addBrandSchema>
export type AddBrandErrors = Partial<Record<keyof AddBrandInput, string>>

export const editBrandSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR).optional(),
})
export type EditBrandInput = z.infer<typeof editBrandSchema>
export type EditBrandErrors = Partial<Record<keyof EditBrandInput, string>>

export interface Brand {
  id: number
  name: string
  image: string
  order: number
}
