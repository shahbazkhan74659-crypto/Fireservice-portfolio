import { z } from 'zod'

export interface SiteSetting {
  years_experience: number
  clients_served: number
  installations: number
  emergency_support: number
  team_members: number
}

export type SiteSettingField = keyof SiteSetting

// Mirrors website/serializers.py's SiteSettingSerializer.Meta.extra_kwargs
// per-field max_value caps exactly, so an out-of-range value is caught here
// with an inline message instead of round-tripping to the server first.
export const SITE_SETTING_FIELD_MAX: Record<SiteSettingField, number> = {
  years_experience: 999,
  clients_served: 999999,
  installations: 999999,
  emergency_support: 999,
  team_members: 9999,
}

export function editStatValueSchemaFor(field: SiteSettingField) {
  const max = SITE_SETTING_FIELD_MAX[field]
  return z.object({
    value: z.coerce.number({ error: 'Enter a number.' })
      .int('Must be a whole number.')
      .min(0, 'Must be zero or greater.')
      .max(max, `Too large (max ${max}).`),
  })
}

export type EditStatValueInput = z.infer<ReturnType<typeof editStatValueSchemaFor>>
export type EditStatValueErrors = Partial<Record<keyof EditStatValueInput, string>>
