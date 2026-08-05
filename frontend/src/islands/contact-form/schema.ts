import { z } from 'zod'
import { nameSchema, emailSchema, phoneSchema } from '../../lib/validators'

export const SERVICE_OPTIONS = [
  { value: 'fire_detection', label: 'Fire Detection System' },
  { value: 'co2_gas_flooding', label: 'Co2 Gas Flooding' },
  { value: 'cctv_pa', label: 'CCTV & PA System' },
  { value: 'hvws_mvms', label: 'HVWS / MVWS System' },
  { value: 'fire_extinguisher', label: 'All Type Fire Extinguisher' },
  { value: 'safety_equipment', label: 'Safety Equipment' },
  { value: 'fire_pump_house', label: 'Fire Pump House' },
  { value: 'electricals', label: 'All Type Electricals Work' },
  { value: 'other', label: 'Not sure / Other' },
] as const

const serviceValues = SERVICE_OPTIONS.map((o) => o.value) as [string, ...string[]]

export const contactMessageSchema = z.object({
  name: nameSchema,
  phone: phoneSchema,
  email: emailSchema,
  service: z.enum(serviceValues, { message: 'Please select a service.' }),
  message: z.string().trim().max(2000, 'Message is too long (max 2000 characters).').optional(),
})

export type ContactMessageInput = z.infer<typeof contactMessageSchema>
export type ContactFormErrors = Partial<Record<keyof ContactMessageInput, string>>
