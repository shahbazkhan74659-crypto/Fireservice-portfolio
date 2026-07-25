import { z } from 'zod'

export const editStatValueSchema = z.object({
  value: z.coerce.number({ error: 'Enter a number.' })
    .int('Must be a whole number.')
    .min(0, 'Must be zero or greater.')
    .max(999999, 'Too large.'),
})
export type EditStatValueInput = z.infer<typeof editStatValueSchema>
export type EditStatValueErrors = Partial<Record<keyof EditStatValueInput, string>>

export interface SiteSetting {
  years_experience: number
  clients_served: number
  installations: number
  emergency_support: number
  team_members: number
}

export type SiteSettingField = keyof SiteSetting
