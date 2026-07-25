import { useState, type ChangeEvent, type FormEvent } from 'react'
import { addClientLogoSchema, type AddClientLogoInput, type ClientLogo } from './schema'
import { useAddForm } from '../../lib/useAddForm'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/client-logos/'

interface Props {
  onAdded: (logo: ClientLogo) => void
}

export default function AddClientLogoForm({ onAdded }: Props) {
  const { open, errors, state, serverError, openModal, closeModal, submit } =
    useAddForm<AddClientLogoInput, ClientLogo>(addClientLogoSchema, ENDPOINT)
  const [name, setName] = useState('')
  const [file, setFile] = useState<File | null>(null)

  function resetFields() {
    setName('')
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
    const created = await submit({ name, image: file }, (data) => {
      const formData = new FormData()
      formData.append('name', data.name)
      formData.append('image', data.image)
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

      <Modal open={open} onClose={handleClose} title="Add Client Logo">
        <form className="logo-add-form" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-logo-name">Name</label>
            <input
              id="new-logo-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-logo-file">Logo Image</label>
            <input
              id="new-logo-file"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={state === 'submitting'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Logo'}
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
