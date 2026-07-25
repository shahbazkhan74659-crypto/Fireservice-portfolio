import { useState, type ChangeEvent, type FormEvent } from 'react'
import { addServiceSchema, type AddServiceInput, type Service } from './schema'
import { useAddForm } from '../../lib/useAddForm'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/services/'

interface Props {
  onAdded: (service: Service) => void
}

export default function AddServiceForm({ onAdded }: Props) {
  const { open, errors, state, serverError, openModal, closeModal, submit } =
    useAddForm<AddServiceInput, Service>(addServiceSchema, ENDPOINT)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [file, setFile] = useState<File | null>(null)

  function resetFields() {
    setName('')
    setDescription('')
    setFile(null)
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
    const created = await submit({ name, description, icon: file }, (data) => {
      const formData = new FormData()
      formData.append('name', data.name)
      formData.append('description', data.description)
      formData.append('icon', data.icon)
      return formData
    })
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

      <Modal open={open} onClose={handleClose} title="Add Service">
        <form className="logo-add-form" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-service-name">Name</label>
            <input
              id="new-service-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-service-description">Description</label>
            <textarea
              id="new-service-description"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.description && <p className="form-note">{errors.description}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-service-icon">Icon Image</label>
            <input
              id="new-service-icon"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={state === 'submitting'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.icon && <p className="form-note">{errors.icon}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Service'}
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
