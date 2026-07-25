import { z } from 'zod'
import { nameSchema, phoneSchema } from '../../lib/validators'

export const consultationRequestSchema = z.object({
  name: nameSchema,
  phone: phoneSchema,
})

export type ConsultationRequestInput = z.infer<typeof consultationRequestSchema>
export type ConsultationFormErrors = Partial<Record<keyof ConsultationRequestInput, string>>
