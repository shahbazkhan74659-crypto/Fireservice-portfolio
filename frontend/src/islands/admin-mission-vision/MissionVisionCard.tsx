import { useState, type FormEvent } from 'react'
import {
  missionVisionItemSchema,
  type MissionVisionItem,
  type MissionVisionItemInput,
  type MissionVisionItemErrors,
} from './schema'
import { useEditDelete } from '../../lib/useEditDelete'
import Modal from '../../lib/Modal'
import { DeleteIcon, EditIcon } from '../../lib/Icons'

const ENDPOINT = '/api/admin-hub/mission-vision/'

interface Props {
  item: MissionVisionItem
  onUpdated: (item: MissionVisionItem) => void
  onDeleted: (id: number) => void
}

function toInput(item: MissionVisionItem): MissionVisionItemInput {
  return { title: item.title, body: item.body, points: item.points }
}

export default function MissionVisionCard({ item, onUpdated, onDeleted }: Props) {
  const { dialog, saveState, serverError, openEdit, openDelete, closeDialog, save, remove } =
    useEditDelete<MissionVisionItem>(ENDPOINT, item.id)
  const [values, setValues] = useState<MissionVisionItemInput>(toInput(item))
  const [errors, setErrors] = useState<MissionVisionItemErrors>({})

  function startEdit() {
    setValues(toInput(item))
    setErrors({})
    openEdit()
  }

  function handlePointChange(index: number, value: string) {
    setValues((prev) => {
      const points = [...prev.points]
      points[index] = value
      return { ...prev, points }
    })
  }

  function addPoint() {
    setValues((prev) => ({ ...prev, points: [...prev.points, ''] }))
  }

  function removePoint(index: number) {
    setValues((prev) => ({ ...prev, points: prev.points.filter((_, i) => i !== index) }))
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const result = missionVisionItemSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: MissionVisionItemErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof MissionVisionItemInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})

    const updated = await save(result.data)
    if (updated) onUpdated(updated)
  }

  async function handleDelete() {
    if (await remove()) onDeleted(item.id)
  }

  return (
    <article className="card admin-mv-card">
      <h3>{item.title}</h3>
      <p>{item.body}</p>
      <ul className="check-list">
        {item.points.map((point, i) => (
          <li key={i}>{point}</li>
        ))}
      </ul>

      <div className="admin-mv-actions">
        <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
          <EditIcon />
        </button>
        <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete">
          <DeleteIcon />
        </button>
      </div>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Mission & Vision Item">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`mv-title-${item.id}`}>Title</label>
            <input
              id={`mv-title-${item.id}`}
              type="text"
              value={values.title}
              onChange={(e) => setValues((prev) => ({ ...prev, title: e.target.value }))}
              disabled={saveState === 'saving'}
            />
            {errors.title && <p className="form-note">{errors.title}</p>}
          </div>

          <div className="field">
            <label htmlFor={`mv-body-${item.id}`}>Description</label>
            <textarea
              id={`mv-body-${item.id}`}
              rows={4}
              value={values.body}
              onChange={(e) => setValues((prev) => ({ ...prev, body: e.target.value }))}
              disabled={saveState === 'saving'}
            />
            {errors.body && <p className="form-note">{errors.body}</p>}
          </div>

          <div className="field">
            <label>Checklist Points</label>
            {values.points.map((point, i) => (
              <div className="admin-mv-point" key={i}>
                <input
                  type="text"
                  value={point}
                  onChange={(e) => handlePointChange(i, e.target.value)}
                  disabled={saveState === 'saving'}
                />
                <button
                  type="button"
                  className="btn btn--outline"
                  onClick={() => removePoint(i)}
                  disabled={saveState === 'saving' || values.points.length <= 1}
                >
                  Remove
                </button>
              </div>
            ))}
            {errors.points && <p className="form-note">{errors.points}</p>}
            <button type="button" className="btn btn--outline" onClick={addPoint} disabled={saveState === 'saving'}>
              + Add Point
            </button>
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="admin-mv-actions">
            <button type="submit" className="btn btn--primary" disabled={saveState === 'saving'}>
              {saveState === 'saving' ? 'Saving…' : 'Save'}
            </button>
            <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'saving'}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Item">
        <p className="modal__body">Delete &quot;{item.title}&quot;? This can&apos;t be undone.</p>

        {serverError && <p className="form-note">{serverError}</p>}

        <div className="admin-mv-actions">
          <button type="button" className="btn btn--primary" onClick={handleDelete} disabled={saveState === 'deleting'}>
            {saveState === 'deleting' ? 'Deleting…' : 'Yes, Delete'}
          </button>
          <button type="button" className="btn btn--outline" onClick={closeDialog} disabled={saveState === 'deleting'}>
            Cancel
          </button>
        </div>
      </Modal>
    </article>
  )
}
