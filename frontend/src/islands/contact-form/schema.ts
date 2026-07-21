import { z } from 'zod'

export const SERVICE_OPTIONS = [
  { value: 'fire_detection', label: 'Fire Detection System' },
  { value: 'co2_gas_flooding', label: 'Co2 Gas Flooding' },
  { value: 'cctv_pa', label: 'CCTV & PA System' },
  { value: 'hvws_mvms', label: 'HVWS / MVMS System' },
  { value: 'fire_extinguisher', label: 'All Type Fire Extinguisher' },
  { value: 'safety_equipment', label: 'Safety Equipment' },
  { value: 'fire_pump_house', label: 'Fire Pump House' },
  { value: 'electricals', label: 'All Type Electricals Work' },
  { value: 'other', label: 'Not sure / Other' },
] as const

const serviceValues = SERVICE_OPTIONS.map((o) => o.value) as [string, ...string[]]

export const contactMessageSchema = z.object({
  name: z.string().trim()
    .min(2, 'Please enter your full name.')
    .max(120, 'Name is too long (max 120 characters).'),
  phone: z.string().trim()
    .min(1, 'Phone number is required.')
    .max(20, 'Phone number is too long.')
    .refine((v) => v.replace(/\D/g, '').length >= 7, 'Please enter a valid phone number.'),
  email: z.string().trim()
    .min(1, 'Email is required.')
    .email('Enter a valid email address.')
    .max(254, 'Email is too long.'),
  service: z.enum(serviceValues, { message: 'Please select a service.' }),
  message: z.string().trim().max(2000, 'Message is too long (max 2000 characters).').optional(),
})

export type ContactMessageInput = z.infer<typeof contactMessageSchema>
export type ContactFormErrors = Partial<Record<keyof ContactMessageInput, string>>
