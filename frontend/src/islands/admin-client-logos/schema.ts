import { z } from 'zod'
import { entityNameField, imageFileSchema } from '../../lib/validators'

const MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG, WebP or SVG.'

export const addClientLogoSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR),
})
export type AddClientLogoInput = z.infer<typeof addClientLogoSchema>
export type AddClientLogoErrors = Partial<Record<keyof AddClientLogoInput, string>>

export const editClientLogoSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR).optional(),
})
export type EditClientLogoInput = z.infer<typeof editClientLogoSchema>
export type EditClientLogoErrors = Partial<Record<keyof EditClientLogoInput, string>>

export interface ClientLogo {
  id: number
  name: string
  image: string
  order: number
}
