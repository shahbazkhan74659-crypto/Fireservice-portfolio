import { z } from 'zod'
import { imageFileSchema } from '../../lib/validators'

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
// Blog photos are raster-only (no SVG requirement, unlike the icon/logo
// fields elsewhere in Admin Hub) — see website/serializers.py's
// BlogPostSerializer comment for the matching backend decision.
const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp']
const IMAGE_TYPE_ERROR = 'Unsupported image type. Use PNG, JPEG or WebP.'

const titleField = z.string().trim()
  .min(2, 'Title is required.')
  .max(200, 'Title is too long (max 200 characters).')

const excerptField = z.string().trim()
  .min(10, 'Excerpt must be at least 10 characters.')
  .max(300, 'Excerpt is too long (max 300 characters).')

const bodyField = z.string().trim()
  .min(10, 'Body must be at least 10 characters.')

const metaDescriptionField = z.string().trim()
  .max(160, 'Meta description is too long (max 160 characters).')
  .optional()

// Unlike Service's `icon` (required on add via imageFileSchema(...) with no
// .optional()), a blog post's `image` is optional both on add AND edit — the
// model field itself is blank=True, and a post can reasonably be published
// text-only.
const imageField = imageFileSchema(
  MAX_IMAGE_SIZE_BYTES,
  ACCEPTED_IMAGE_TYPES,
  IMAGE_TYPE_ERROR,
  'Please choose an image file.',
).optional()

const publishedAtField = z.string().trim().min(1, 'Published date is required.')
const isPublishedField = z.boolean()

export const addBlogSchema = z.object({
  title: titleField,
  excerpt: excerptField,
  body: bodyField,
  meta_description: metaDescriptionField,
  image: imageField,
  published_at: publishedAtField,
  is_published: isPublishedField,
})
export type AddBlogInput = z.infer<typeof addBlogSchema>
export type AddBlogErrors = Partial<Record<keyof AddBlogInput, string>>

// Identical field set to addBlogSchema — image is already optional there
// (unlike editServiceSchema, which has to add .optional() on top of a
// required-on-add icon schema), so no separate edit schema is needed.
export const editBlogSchema = addBlogSchema
export type EditBlogInput = AddBlogInput
export type EditBlogErrors = AddBlogErrors

// Matches the API response shape directly (snake_case, no camelCase
// transform layer) — same convention Service's schema.ts follows.
export interface BlogPost {
  id: number
  title: string
  slug: string
  excerpt: string
  body: string
  meta_description: string
  image: string
  published_at: string
  is_published: boolean
  created_at: string
  updated_at: string
}
