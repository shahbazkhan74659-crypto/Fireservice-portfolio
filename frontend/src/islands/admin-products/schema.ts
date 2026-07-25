import { z } from 'zod'
import { entityNameField, imageFileSchema } from '../../lib/validators'

const MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG, WebP or SVG.'

export const addProductSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR),
})
export type AddProductInput = z.infer<typeof addProductSchema>
export type AddProductErrors = Partial<Record<keyof AddProductInput, string>>

export const editProductSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR).optional(),
})
export type EditProductInput = z.infer<typeof editProductSchema>
export type EditProductErrors = Partial<Record<keyof EditProductInput, string>>

export interface Product {
  id: number
  name: string
  image: string
  order: number
}
