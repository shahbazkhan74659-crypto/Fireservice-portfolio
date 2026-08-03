import { useState, type ChangeEvent, type FormEvent } from 'react'
import { addProcessPhaseSchema, type AddProcessPhaseInput, type ProcessPhase } from './schema'
import { useAddForm } from '../../lib/useAddForm'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/process-phases/'

interface Props {
  onAdded: (phase: ProcessPhase) => void
}

export default function AddProcessPhaseForm({ onAdded }: Props) {
  const { open, errors, state, serverError, openModal, closeModal, submit } =
    useAddForm<AddProcessPhaseInput, ProcessPhase>(addProcessPhaseSchema, ENDPOINT)
  const [name, setName] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [tagline, setTagline] = useState('')
  const [card1Title, setCard1Title] = useState('')
  const [card1Text, setCard1Text] = useState('')
  const [card2Title, setCard2Title] = useState('')
  const [card2Text, setCard2Text] = useState('')

  function resetFields() {
    setName('')
    setFile(null)
    setTitle('')
    setTagline('')
    setCard1Title('')
    setCard1Text('')
    setCard2Title('')
    setCard2Text('')
  }

  function handleClose() {
    resetFields()
    closeModal()
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const created = await submit(
      {
        name,
        image: file,
        title,
        tagline,
        card1_title: card1Title,
        card1_text: card1Text,
        card2_title: card2Title,
        card2_text: card2Text,
      },
      (data) => {
        const formData = new FormData()
        formData.append('name', data.name)
        formData.append('image', data.image)
        formData.append('title', data.title)
        formData.append('tagline', data.tagline)
        formData.append('card1_title', data.card1_title)
        formData.append('card1_text', data.card1_text)
        formData.append('card2_title', data.card2_title)
        formData.append('card2_text', data.card2_text)
        return formData
      },
    )
    if (created) {
      onAdded(created)
      resetFields()
    }
  }

  return (
    <>
      <div className="client-logos__admin-actions">
        <button type="button" className="btn btn--primary" onClick={openModal}>+ Add</button>
      </div>

      <Modal open={open} onClose={handleClose} title="Add Process Phase">
        <form className="logo-add-form" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-process-phase-name">Description (used as alt text)</label>
            <input
              id="new-process-phase-name"
              type="text"
              autoComplete="off"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-process-phase-file">Photo</label>
            <input
              id="new-process-phase-file"
              type="file"
              accept="image/*"
              autoComplete="off"
              onChange={handleFileChange}
              disabled={state === 'submitting'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-process-phase-title">Title</label>
            <input
              id="new-process-phase-title"
              type="text"
              autoComplete="off"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.title && <p className="form-note">{errors.title}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-process-phase-tagline">Tagline</label>
            <input
              id="new-process-phase-tagline"
              type="text"
              autoComplete="off"
              value={tagline}
              onChange={(e) => setTagline(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.tagline && <p className="form-note">{errors.tagline}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-process-phase-card1-title">Card 1 Title</label>
            <input
              id="new-process-phase-card1-title"
              type="text"
              autoComplete="off"
              value={card1Title}
              onChange={(e) => setCard1Title(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.card1_title && <p className="form-note">{errors.card1_title}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-process-phase-card1-text">Card 1 Text</label>
            <textarea
              id="new-process-phase-card1-text"
              rows={3}
              autoComplete="off"
              value={card1Text}
              onChange={(e) => setCard1Text(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.card1_text && <p className="form-note">{errors.card1_text}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-process-phase-card2-title">Card 2 Title</label>
            <input
              id="new-process-phase-card2-title"
              type="text"
              autoComplete="off"
              value={card2Title}
              onChange={(e) => setCard2Title(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.card2_title && <p className="form-note">{errors.card2_title}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-process-phase-card2-text">Card 2 Text</label>
            <textarea
              id="new-process-phase-card2-text"
              rows={3}
              autoComplete="off"
              value={card2Text}
              onChange={(e) => setCard2Text(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.card2_text && <p className="form-note">{errors.card2_text}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Phase'}
            </button>
            <button type="button" className="btn btn--outline" onClick={handleClose} disabled={state === 'submitting'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </>
  )
}
