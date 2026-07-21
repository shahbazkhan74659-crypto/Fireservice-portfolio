import { z } from 'zod'

export const surveyRequestSchema = z.object({
  name: z.string().trim()
    .min(2, 'Please enter your full name.')
    .max(120, 'Name is too long (max 120 characters).'),
  email: z.string().trim()
    .min(1, 'Email is required.')
    .email('Enter a valid email address.')
    .max(254, 'Email is too long.'),
  address: z.string().trim()
    .min(10, 'Please enter a full address so we can plan the site visit.')
    .max(500, 'Address is too long (max 500 characters).'),
  problem: z.string().trim()
    .min(20, 'Please describe the issue in a bit more detail.')
    .max(2000, 'Description is too long (max 2000 characters).'),
  whySurvey: z.string().trim()
    .min(20, 'Please tell us why a survey is needed.')
    .max(2000, 'This is too long (max 2000 characters).'),
})

export type SurveyRequestInput = z.infer<typeof surveyRequestSchema>
export type SurveyFormErrors = Partial<Record<keyof SurveyRequestInput, string>>
