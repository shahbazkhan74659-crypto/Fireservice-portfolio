import { z } from 'zod'

export const adminLoginSchema = z.object({
  username: z.string().trim().min(1, 'Username is required.').max(150, 'Username is too long.'),
  password: z.string().min(1, 'Password is required.'),
})

export type AdminLoginInput = z.infer<typeof adminLoginSchema>
export type AdminLoginFormErrors = Partial<Record<keyof AdminLoginInput, string>>
