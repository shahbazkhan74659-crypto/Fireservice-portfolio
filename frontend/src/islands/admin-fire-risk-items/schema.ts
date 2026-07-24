import { z } from 'zod'

const textField = z.string().trim()
  .min(2, 'Text is required.')
  .max(200, 'Text is too long (max 200 characters).')

export const addFireRiskItemSchema = z.object({
  text: textField,
})
export type AddFireRiskItemInput = z.infer<typeof addFireRiskItemSchema>
export type AddFireRiskItemErrors = Partial<Record<keyof AddFireRiskItemInput, string>>

export const editFireRiskItemSchema = z.object({
  text: textField,
})
export type EditFireRiskItemInput = z.infer<typeof editFireRiskItemSchema>
export type EditFireRiskItemErrors = Partial<Record<keyof EditFireRiskItemInput, string>>

export interface FireRiskAssessmentItem {
  id: number
  text: string
  order: number
}
