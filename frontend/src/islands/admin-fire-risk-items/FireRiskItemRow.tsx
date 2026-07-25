import { useState, type FormEvent } from 'react'
import {
  editFireRiskItemSchema,
  type FireRiskAssessmentItem,
  type EditFireRiskItemInput,
  type EditFireRiskItemErrors,
} from './schema'
import { useEditDelete } from '../../lib/useEditDelete'
import Modal from '../../lib/Modal'
import { DeleteIcon, EditIcon } from '../../lib/Icons'

const ENDPOINT = '/api/admin-hub/fire-risk-items/'

interface Props {
  item: FireRiskAssessmentItem
  onUpdated: (item: FireRiskAssessmentItem) => void
  onDeleted: (id: number) => void
}

export default function FireRiskItemRow({ item, onUpdated, onDeleted }: Props) {
  const { dialog, saveState, serverError, openEdit, openDelete, closeDialog, save, remove } =
    useEditDelete<FireRiskAssessmentItem>(ENDPOINT, item.id)
  const [text, setText] = useState(item.text)
  const [errors, setErrors] = useState<EditFireRiskItemErrors>({})

  function startEdit() {
    setText(item.text)
    setErrors({})
    openEdit()
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const values: EditFireRiskItemInput = { text }
    const result = editFireRiskItemSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: EditFireRiskItemErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof EditFireRiskItemInput
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
    <div className="admin-mv-point">
      <span className="admin-mv-point__text">{item.text}</span>

      <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
        <EditIcon />
      </button>
      <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete">
        <DeleteIcon />
      </button>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Fire Risk Assessment Item">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`fire-risk-item-text-${item.id}`}>Text</label>
            <input
              id={`fire-risk-item-text-${item.id}`}
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.text && <p className="form-note">{errors.text}</p>}
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

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Item">
        <p className="modal__body">Delete &quot;{item.text}&quot;? This can&apos;t be undone.</p>

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
