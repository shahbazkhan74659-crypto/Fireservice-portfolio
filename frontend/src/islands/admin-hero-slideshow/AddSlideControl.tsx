import type { ChangeEvent } from 'react'
import { addHeroSlideSchema, type AddHeroSlideInput, type HeroSlide } from './schema'
import { useAddForm } from '../../lib/useAddForm'

const ENDPOINT = '/api/admin-hub/hero-slides/'

interface Props {
  onAdded: (slide: HeroSlide) => void
}

/** Uploads immediately on file selection — no separate submit step, since
 * this is a single field with nothing else to fill in first. */
export default function AddSlideControl({ onAdded }: Props) {
  const { errors, state, serverError, submit } =
    useAddForm<AddHeroSlideInput, HeroSlide>(addHeroSlideSchema, ENDPOINT)

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    e.target.value = ''
    if (!file) return

    const created = await submit({ image: file }, (data) => {
      const formData = new FormData()
      formData.append('image', data.image)
      return formData
    })
    if (created) onAdded(created)
  }

  return (
    <div className="field">
      <label htmlFor="new-hero-slide-file">Add new image</label>
      <input
        id="new-hero-slide-file"
        type="file"
        accept="image/*"
        autoComplete="off"
        onChange={handleFileChange}
        disabled={state === 'submitting'}
      />
      {errors.image && <p className="form-note">{errors.image}</p>}
      {serverError && <p className="form-note">{serverError}</p>}
    </div>
  )
}
