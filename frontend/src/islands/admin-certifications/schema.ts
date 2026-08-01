import { z } from 'zod'
import { entityNameField } from '../../lib/validators'

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
const ACCEPTED_FILE_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp', 'application/pdf'])

const descriptionField = z.string().trim()
  .min(2, 'Description is required.')
  .max(200, 'Description is too long (max 200 characters).')

const metaField = z.string().trim()
  .min(2, 'This field is required.')
  .max(200, 'Too long (max 200 characters).')

// Either an image or a PDF — uploading a PDF renders its first page into
// the certificate thumbnail server-side (see website.serializers
// CertificationSerializer.create()), so the client just needs to accept
// both file families rather than deciding which one it is.
const certificateFileSchema = z.instanceof(File, { message: 'Please choose a certificate image or PDF.' })
  .superRefine((file, ctx) => {
    if (file.size > MAX_FILE_SIZE_BYTES) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: `File is too large (max ${MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB).` })
    }
    if (!ACCEPTED_FILE_TYPES.has(file.type)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Unsupported file type. Use PNG, JPEG, WebP or PDF.' })
    }
  })

export const addCertificationSchema = z.object({
  name: entityNameField,
  description: descriptionField,
  meta: metaField,
  file: certificateFileSchema,
})
export type AddCertificationInput = z.infer<typeof addCertificationSchema>
export type AddCertificationErrors = Partial<Record<keyof AddCertificationInput, string>>

export interface Certification {
  id: number
  name: string
  description: string
  meta: string
  image: string
  pdf: string | null
  order: number
}
