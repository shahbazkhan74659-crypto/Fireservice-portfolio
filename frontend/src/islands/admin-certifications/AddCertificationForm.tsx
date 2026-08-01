import { useState, type ChangeEvent, type FormEvent } from 'react'
import { addCertificationSchema, type AddCertificationInput, type Certification } from './schema'
import { useAddForm } from '../../lib/useAddForm'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/certifications/'

interface Props {
  onAdded: (certification: Certification) => void
}

export default function AddCertificationForm({ onAdded }: Props) {
  const { open, errors, state, serverError, openModal, closeModal, submit } =
    useAddForm<AddCertificationInput, Certification>(addCertificationSchema, ENDPOINT)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [meta, setMeta] = useState('')
  const [file, setFile] = useState<File | null>(null)

  function resetFields() {
    setName('')
    setDescription('')
    setMeta('')
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
    const created = await submit({ name, description, meta, file }, (data) => {
      const formData = new FormData()
      formData.append('name', data.name)
      formData.append('description', data.description)
      formData.append('meta', data.meta)
      // PDFs and images go to different serializer fields — the backend
      // renders a PDF's first page into the thumbnail automatically.
      formData.append(data.file.type === 'application/pdf' ? 'pdf' : 'image', data.file)
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

      <Modal open={open} onClose={handleClose} title="Add Certificate">
        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-cert-name">Certificate Name</label>
            <input
              id="new-cert-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.name && <p className="form-note">{errors.name}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-cert-description">Description</label>
            <input
              id="new-cert-description"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={state === 'submitting'}
              placeholder="e.g. Quality Management Systems"
            />
            {errors.description && <p className="form-note">{errors.description}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-cert-meta">Validity / Registration No.</label>
            <input
              id="new-cert-meta"
              type="text"
              value={meta}
              onChange={(e) => setMeta(e.target.value)}
              disabled={state === 'submitting'}
              placeholder="e.g. Valid till 15 Jul 2029"
            />
            {errors.meta && <p className="form-note">{errors.meta}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-cert-file">Certificate File (Image or PDF)</label>
            <input
              id="new-cert-file"
              type="file"
              accept="image/png,image/jpeg,image/webp,application/pdf"
              onChange={handleFileChange}
              disabled={state === 'submitting'}
            />
            <p className="form-note">Uploading a PDF automatically uses its first page as the certificate image.</p>
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.file && <p className="form-note">{errors.file}</p>}
          </div>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Certificate'}
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
