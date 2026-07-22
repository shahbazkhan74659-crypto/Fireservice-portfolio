import { useState, type FormEvent } from 'react'
import {
  missionVisionItemSchema,
  type MissionVisionItem,
  type MissionVisionItemInput,
  type MissionVisionItemErrors,
} from './schema'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage } from '../../lib/api'

type Mode = 'view' | 'edit' | 'confirm-delete'
type SaveState = 'idle' | 'saving' | 'deleting'

interface Props {
  item: MissionVisionItem
  onUpdated: (item: MissionVisionItem) => void
  onDeleted: (id: number) => void
}

function toInput(item: MissionVisionItem): MissionVisionItemInput {
  return { title: item.title, body: item.body, points: item.points }
}

export default function MissionVisionCard({ item, onUpdated, onDeleted }: Props) {
  const [mode, setMode] = useState<Mode>('view')
  const [values, setValues] = useState<MissionVisionItemInput>(toInput(item))
  const [errors, setErrors] = useState<MissionVisionItemErrors>({})
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [serverError, setServerError] = useState<string | null>(null)

  function startEdit() {
    setValues(toInput(item))
    setErrors({})
    setServerError(null)
    setMode('edit')
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
    setServerError(null)

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
    setSaveState('saving')

    try {
      const res = await fetch(`/api/admin-hub/mission-vision/${item.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify(result.data),
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        return
      }
      const updated: MissionVisionItem = await res.json()
      onUpdated(updated)
      setSaveState('idle')
      setMode('view')
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
    }
  }

  async function handleDelete() {
    setSaveState('deleting')
    setServerError(null)
    try {
      const res = await fetch(`/api/admin-hub/mission-vision/${item.id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
      })
      if (!res.ok && res.status !== 204) {
        setServerError(await readErrorMessage(res))
        setSaveState('idle')
        setMode('view')
        return
      }
      onDeleted(item.id)
    } catch {
      setServerError('Network error. Check your connection and try again.')
      setSaveState('idle')
      setMode('view')
    }
  }

  if (mode === 'edit') {
    return (
      <article className="card admin-mv-card">
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
            <button type="button" className="btn btn--outline" onClick={() => setMode('view')} disabled={saveState === 'saving'}>
              Cancel
            </button>
          </div>
        </form>
      </article>
    )
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

      {serverError && <p className="form-note">{serverError}</p>}

      <div className="admin-mv-actions">
        {mode === 'confirm-delete' ? (
          <>
            <span className="admin-mv-confirm-text">Delete this item?</span>
            <button type="button" className="btn btn--primary" onClick={handleDelete} disabled={saveState === 'deleting'}>
              {saveState === 'deleting' ? 'Deleting…' : 'Yes, Delete'}
            </button>
            <button type="button" className="btn btn--outline" onClick={() => setMode('view')} disabled={saveState === 'deleting'}>
              Cancel
            </button>
          </>
        ) : (
          <>
            <button type="button" className="btn btn--outline" onClick={startEdit}>Edit</button>
            <button type="button" className="btn btn--outline" onClick={() => setMode('confirm-delete')}>Delete</button>
          </>
        )}
      </div>
    </article>
  )
}
