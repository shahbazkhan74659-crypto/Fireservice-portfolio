import { z } from 'zod'

export const missionVisionItemSchema = z.object({
  title: z.string().trim()
    .min(2, 'Title is required.')
    .max(100, 'Title is too long (max 100 characters).'),
  body: z.string().trim()
    .min(10, 'Description must be at least 10 characters.')
    .max(2000, 'Description is too long (max 2000 characters).'),
  points: z.array(z.string().trim().min(1, 'Point cannot be empty.'))
    .min(1, 'Add at least one checklist point.')
    .max(10, 'Too many points (max 10).'),
})

export type MissionVisionItemInput = z.infer<typeof missionVisionItemSchema>
export type MissionVisionItemErrors = Partial<Record<keyof MissionVisionItemInput, string>>

export interface MissionVisionItem extends MissionVisionItemInput {
  id: number
  order: number
}
