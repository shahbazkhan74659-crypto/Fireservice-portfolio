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
  const [errors, setErrors] = useState<EditProcessPhaseErrors>({})

  function startEdit() {
    setName(phase.name)
    setFile(null)
    setErrors({})
    openEdit()
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const values: EditProcessPhaseInput = { name, image: file ?? undefined }
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

    const updated = await save(formData)
    if (updated) onUpdated(updated)
  }

  async function handleDelete() {
    if (await remove()) onDeleted(phase.id)
  }

  return (
    <div className="logo-card logo-card--admin">
      <img src={phase.image} alt={phase.name} />

      <div className="logo-card__admin-actions">
        <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
          <EditIcon />
        </button>
        <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete">
          <DeleteIcon />
        </button>
      </div>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Process Phase Photo">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`process-phase-name-${phase.id}`}>Description (used as alt text)</label>
            <input
              id={`process-phase-name-${phase.id}`}
              type="text"
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
              onChange={handleFileChange}
              disabled={saveState === 'saving'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
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

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Process Phase Photo">
        <p className="modal__body">Delete &quot;{phase.name}&quot;? This can&apos;t be undone.</p>

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
