import { z } from 'zod'
import { nameSchema } from '../../lib/validators'

export const feedbackSchema = z.object({
  name: nameSchema,
  quote: z.string().trim()
    .min(10, 'Please share a bit more detail (at least 10 characters).')
    .max(1000, 'Quote is too long (max 1000 characters).'),
  rating: z.coerce.number({ error: 'Select a rating.' })
    .int('Rating must be a whole number.')
    .min(1, 'Please select a rating.')
    .max(5, 'Rating must be between 1 and 5.'),
})

export type FeedbackInput = z.infer<typeof feedbackSchema>
