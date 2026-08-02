import { z } from 'zod'
import { entityNameField, imageFileSchema } from '../../lib/validators'

const MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG, WebP or SVG.'

export const addProcessPhaseSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR),
})
export type AddProcessPhaseInput = z.infer<typeof addProcessPhaseSchema>
export type AddProcessPhaseErrors = Partial<Record<keyof AddProcessPhaseInput, string>>

export const editProcessPhaseSchema = z.object({
  name: entityNameField,
  image: imageFileSchema(MAX_LOGO_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR).optional(),
})
export type EditProcessPhaseInput = z.infer<typeof editProcessPhaseSchema>
export type EditProcessPhaseErrors = Partial<Record<keyof EditProcessPhaseInput, string>>

export interface ProcessPhase {
  id: number
  name: string
  image: string
  order: number
}
