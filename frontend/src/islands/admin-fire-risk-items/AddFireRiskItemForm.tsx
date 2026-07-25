import { useState, type FormEvent } from 'react'
import { addFireRiskItemSchema, type AddFireRiskItemInput, type FireRiskAssessmentItem } from './schema'
import { useAddForm } from '../../lib/useAddForm'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/fire-risk-items/'

interface Props {
  onAdded: (item: FireRiskAssessmentItem) => void
}

export default function AddFireRiskItemForm({ onAdded }: Props) {
  const { open, errors, state, serverError, openModal, closeModal, submit } =
    useAddForm<AddFireRiskItemInput, FireRiskAssessmentItem>(addFireRiskItemSchema, ENDPOINT)
  const [text, setText] = useState('')

  function resetFields() {
    setText('')
  }

  function handleClose() {
    resetFields()
    closeModal()
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const created = await submit({ text }, (data) => data)
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

      <Modal open={open} onClose={handleClose} title="Add Fire Risk Assessment Item">
        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-fire-risk-item-text">Text</label>
            <input
              id="new-fire-risk-item-text"
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.text && <p className="form-note">{errors.text}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Item'}
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
