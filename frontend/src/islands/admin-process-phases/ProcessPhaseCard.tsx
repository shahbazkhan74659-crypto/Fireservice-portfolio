import { useState, type ChangeEvent, type FormEvent } from 'react'
import {
  editProcessPhaseSchema,
  type ProcessPhase,
  type EditProcessPhaseInput,
  type EditProcessPhaseErrors,
} from './schema'
import { useEditDelete } from '../../lib/useEditDelete'
import Modal from '../../lib/Modal'
import { DeleteIcon, EditIcon } from '../../lib/Icons'

const ENDPOINT = '/api/admin-hub/process-phases/'

interface Props {
  phase: ProcessPhase
  onUpdated: (phase: ProcessPhase) => void
  onDeleted: (id: number) => void
}

export default function ProcessPhaseCard({ phase, onUpdated, onDeleted }: Props) {
  const { dialog, saveState, serverError, openEdit, openDelete, closeDialog, save, remove } =
    useEditDelete<ProcessPhase>(ENDPOINT, phase.id)
  const [name, setName] = useState(phase.name)
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState(phase.title)
  const [tagline, setTagline] = useState(phase.tagline)
  const [card1Title, setCard1Title] = useState(phase.card1_title)
  const [card1Text, setCard1Text] = useState(phase.card1_text)
  const [card2Title, setCard2Title] = useState(phase.card2_title)
  const [card2Text, setCard2Text] = useState(phase.card2_text)
  const [errors, setErrors] = useState<EditProcessPhaseErrors>({})

  function startEdit() {
    setName(phase.name)
    setFile(null)
    setTitle(phase.title)
    setTagline(phase.tagline)
    setCard1Title(phase.card1_title)
    setCard1Text(phase.card1_text)
    setCard2Title(phase.card2_title)
    setCard2Text(phase.card2_text)
    setErrors({})
    openEdit()
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const values: EditProcessPhaseInput = {
      name,
      image: file ?? undefined,
      title,
      tagline,
      card1_title: card1Title,
      card1_text: card1Text,
      card2_title: card2Title,
      card2_text: card2Text,
    }
    const result = editProcessPhaseSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: EditProcessPhaseErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof EditProcessPhaseInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})

    const formData = new FormData()
    formData.append('name', result.data.name)
    if (result.data.image) formData.append('image', result.data.image)
    formData.append('title', result.data.title)
    formData.append('tagline', result.data.tagline)
    formData.append('card1_title', result.data.card1_title)
    formData.append('card1_text', result.data.card1_text)
    formData.append('card2_title', result.data.card2_title)
    formData.append('card2_text', result.data.card2_text)

    const updated = await save(formData)
    if (updated) onUpdated(updated)
  }

  async function handleDelete() {
    if (await remove()) onDeleted(phase.id)
  }

  return (
    <div className="phase-admin-row">
      <div className="phase-admin-row__head">
        <p className="phase-admin-row__label">Phase {phase.order} &mdash; {phase.title}</p>
        <div className="logo-card__admin-actions">
          <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
            <EditIcon />
          </button>
          <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete">
            <DeleteIcon />
          </button>
        </div>
      </div>

      <div className="phase__body">
        <img className="phase__image" src={phase.image} alt={phase.name} />
        <div className="phase__cards">
          <div className="phase__card">
            <h4>{phase.card1_title}</h4>
            <p>{phase.card1_text}</p>
          </div>
          <div className="phase__card">
            <h4>{phase.card2_title}</h4>
            <p>{phase.card2_text}</p>
          </div>
        </div>
      </div>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Process Phase">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`process-phase-name-${phase.id}`}>Description (used as alt text)</label>
            <input
              id={`process-phase-name-${phase.id}`}
              type="text"
              autoComplete="off"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor={`process-phase-file-${phase.id}`}>Replace Photo (optional)</label>
            <input
              id={`process-phase-file-${phase.id}`}
              type="file"
              accept="image/*"
              autoComplete="off"
              onChange={handleFileChange}
              disabled={saveState === 'saving'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
          </div>
          <div className="field">
            <label htmlFor={`process-phase-title-${phase.id}`}>Title</label>
            <input
              id={`process-phase-title-${phase.id}`}
              type="text"
              autoComplete="off"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.title && <p className="form-note">{errors.title}</p>}
          </div>
          <div className="field">
            <label htmlFor={`process-phase-tagline-${phase.id}`}>Tagline</label>
            <input
              id={`process-phase-tagline-${phase.id}`}
              type="text"
              autoComplete="off"
              value={tagline}
              onChange={(e) => setTagline(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.tagline && <p className="form-note">{errors.tagline}</p>}
          </div>
          <div className="field">
            <label htmlFor={`process-phase-card1-title-${phase.id}`}>Card 1 Title</label>
            <input
              id={`process-phase-card1-title-${phase.id}`}
              type="text"
              autoComplete="off"
              value={card1Title}
              onChange={(e) => setCard1Title(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.card1_title && <p className="form-note">{errors.card1_title}</p>}
          </div>
          <div className="field">
            <label htmlFor={`process-phase-card1-text-${phase.id}`}>Card 1 Text</label>
            <textarea
              id={`process-phase-card1-text-${phase.id}`}
              rows={3}
              autoComplete="off"
              value={card1Text}
              onChange={(e) => setCard1Text(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.card1_text && <p className="form-note">{errors.card1_text}</p>}
          </div>
          <div className="field">
            <label htmlFor={`process-phase-card2-title-${phase.id}`}>Card 2 Title</label>
            <input
              id={`process-phase-card2-title-${phase.id}`}
              type="text"
              autoComplete="off"
              value={card2Title}
              onChange={(e) => setCard2Title(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.card2_title && <p className="form-note">{errors.card2_title}</p>}
          </div>
          <div className="field">
            <label htmlFor={`process-phase-card2-text-${phase.id}`}>Card 2 Text</label>
            <textarea
              id={`process-phase-card2-text-${phase.id}`}
              rows={3}
              autoComplete="off"
              value={card2Text}
              onChange={(e) => setCard2Text(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.card2_text && <p className="form-note">{errors.card2_text}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={saveState === 'saving'}>
              {saveState === 'saving' ? 'Saving…' : 'Save'}
            </button>
            <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'saving'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Process Phase">
        <p className="modal__body">Delete phase {phase.order} (&quot;{phase.name}&quot;)? This can&apos;t be undone.</p>

        {serverError && <p className="form-note">{serverError}</p>}

        <div className="logo-card__admin-actions">
          <button type="button" className="btn btn--primary" onClick={handleDelete} disabled={saveState === 'deleting'}>
            {saveState === 'deleting' ? 'Deleting…' : 'Yes, Delete'}
          </button>
          <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'deleting'}>
            Cancel
          </button>
        </div>
      </Modal>
    </div>
  )
}
