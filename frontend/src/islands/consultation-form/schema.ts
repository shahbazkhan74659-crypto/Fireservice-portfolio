import { z } from 'zod'
import { nameSchema } from '../../lib/validators'

export const consultationRequestSchema = z.object({
  name: nameSchema,
  phone: z.string().trim()
    .min(1, 'Phone number is required.')
    .max(20, 'Phone number is too long.')
    .refine((v) => v.replace(/\D/g, '').length >= 7, 'Please enter a valid phone number.'),
})

export type ConsultationRequestInput = z.infer<typeof consultationRequestSchema>
export type ConsultationFormErrors = Partial<Record<keyof ConsultationRequestInput, string>>
