import { z } from 'zod'
import { imageFileSchema } from '../../lib/validators'

const MAX_SLIDE_SIZE_BYTES = 5 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG, WebP or SVG.'

export const addHeroSlideSchema = z.object({
  image: imageFileSchema(MAX_SLIDE_SIZE_BYTES, ACCEPTED_IMAGE_TYPES, IMAGE_TYPE_ERROR),
})
export type AddHeroSlideInput = z.infer<typeof addHeroSlideSchema>
export type AddHeroSlideErrors = Partial<Record<keyof AddHeroSlideInput, string>>

export const MIN_DURATION_SECONDS = 1
export const MAX_DURATION_SECONDS = 60

// Mirrors website/serializers.py's SiteSettingSerializer min/max_value for
// hero_slide_duration_seconds.
export const durationSchema = z.string().trim()
  .refine((v) => /^\d+$/.test(v), 'Enter a whole number of seconds.')
  .transform((v) => Number(v))
  .refine(
    (v) => v >= MIN_DURATION_SECONDS && v <= MAX_DURATION_SECONDS,
    `Must be between ${MIN_DURATION_SECONDS} and ${MAX_DURATION_SECONDS} seconds.`,
  )

export interface HeroSlide {
  id: number
  image: string
  order: number
}
