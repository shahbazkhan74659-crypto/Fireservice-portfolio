import { z } from 'zod'

const MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024
const PDF_CONTENT_TYPE = 'application/pdf'

// Mirrors website/serializers.py's validate_pdf_file (size + content-type —
// the real magic-byte check still happens server-side, this is UX only).
export const pdfFileSchema = z.instanceof(File, { message: 'Please choose a PDF file.' })
  .superRefine((file, ctx) => {
    if (file.size > MAX_PDF_SIZE_BYTES) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `PDF is too large (max ${MAX_PDF_SIZE_BYTES / (1024 * 1024)}MB).`,
      })
    }
    if (file.type !== PDF_CONTENT_TYPE) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Unsupported file type. Upload a PDF.' })
    }
  })

export interface Brochure {
  pdf: string
  image: string
}
