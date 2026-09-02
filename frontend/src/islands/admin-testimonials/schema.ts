import { z } from 'zod'

const nameField = z.string().trim()
  .min(2, 'Name is required.')
  .max(120, 'Name is too long (max 120 characters).')

const companyField = z.string().trim()
  .max(120, 'Company is too long (max 120 characters).')

const quoteField = z.string().trim()
  .min(10, 'Quote must be at least 10 characters.')
  .max(1000, 'Quote is too long (max 1000 characters).')

const ratingField = z.coerce.number({ error: 'Select a rating.' })
  .int('Rating must be a whole number.')
  .min(1, 'Rating must be between 1 and 5.')
  .max(5, 'Rating must be between 1 and 5.')

export const addTestimonialSchema = z.object({
  name: nameField,
  company: companyField,
  quote: quoteField,
  rating: ratingField,
})
export type AddTestimonialInput = z.infer<typeof addTestimonialSchema>
export type AddTestimonialErrors = Partial<Record<keyof AddTestimonialInput, string>>

export const editTestimonialSchema = z.object({
  name: nameField,
  company: companyField,
  quote: quoteField,
  rating: ratingField,
})
export type EditTestimonialInput = z.infer<typeof editTestimonialSchema>
export type EditTestimonialErrors = Partial<Record<keyof EditTestimonialInput, string>>

export interface Testimonial {
  id: number
  name: string
  company: string
  quote: string
  rating: number
  order: number
}
