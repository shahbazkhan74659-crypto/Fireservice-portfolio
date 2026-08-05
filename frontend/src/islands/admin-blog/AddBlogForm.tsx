import { useState, type ChangeEvent, type FormEvent } from 'react'
import { addBlogSchema, type AddBlogInput, type BlogPost } from './schema'
import { useAddForm } from '../../lib/useAddForm'
import Modal from '../../lib/Modal'

const ENDPOINT = '/api/admin-hub/blog/'

interface Props {
  onAdded: (post: BlogPost) => void
}

function todayISODate() {
  return new Date().toISOString().slice(0, 10)
}

export default function AddBlogForm({ onAdded }: Props) {
  const { open, errors, state, serverError, openModal, closeModal, submit } =
    useAddForm<AddBlogInput, BlogPost>(addBlogSchema, ENDPOINT)
  const [title, setTitle] = useState('')
  const [excerpt, setExcerpt] = useState('')
  const [body, setBody] = useState('')
  const [metaDescription, setMetaDescription] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [publishedAt, setPublishedAt] = useState(todayISODate())
  const [isPublished, setIsPublished] = useState(false)

  function resetFields() {
    setTitle('')
    setExcerpt('')
    setBody('')
    setMetaDescription('')
    setFile(null)
    setPublishedAt(todayISODate())
    setIsPublished(false)
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
        title,
        excerpt,
        body,
        meta_description: metaDescription,
        image: file ?? undefined,
        published_at: publishedAt,
        is_published: isPublished,
      },
      (data) => {
        const formData = new FormData()
        formData.append('title', data.title)
        formData.append('excerpt', data.excerpt)
        formData.append('body', data.body)
        if (data.meta_description) formData.append('meta_description', data.meta_description)
        if (data.image) formData.append('image', data.image)
        formData.append('published_at', data.published_at)
        // DRF's BooleanField accepts 'true'/'false' strings from multipart
        // form data by default.
        formData.append('is_published', data.is_published ? 'true' : 'false')
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

      <Modal open={open} onClose={handleClose} title="Add Blog Post">
        <form className="logo-add-form" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="new-blog-title">Title</label>
            <input
              id="new-blog-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.title && <p className="form-note">{errors.title}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-blog-excerpt">Excerpt</label>
            <textarea
              id="new-blog-excerpt"
              rows={3}
              value={excerpt}
              onChange={(e) => setExcerpt(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.excerpt && <p className="form-note">{errors.excerpt}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-blog-body">Body</label>
            <textarea
              id="new-blog-body"
              rows={10}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.body && <p className="form-note">{errors.body}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-blog-meta-description">Meta Description (SEO override, optional)</label>
            <input
              id="new-blog-meta-description"
              type="text"
              value={metaDescription}
              onChange={(e) => setMetaDescription(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.meta_description && <p className="form-note">{errors.meta_description}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-blog-image">Image (optional)</label>
            <input
              id="new-blog-image"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={state === 'submitting'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
          </div>
          <div className="field">
            <label htmlFor="new-blog-published-at">Published Date</label>
            <input
              id="new-blog-published-at"
              type="date"
              value={publishedAt}
              onChange={(e) => setPublishedAt(e.target.value)}
              disabled={state === 'submitting'}
            />
            {errors.published_at && <p className="form-note">{errors.published_at}</p>}
          </div>
          <label className="field field--checkbox">
            <input
              type="checkbox"
              checked={isPublished}
              onChange={(e) => setIsPublished(e.target.checked)}
              disabled={state === 'submitting'}
            />
            <span>Publish immediately</span>
          </label>

          {serverError && <p className="form-note">{serverError}</p>}

          <div className="logo-card__admin-actions">
            <button type="submit" className="btn btn--primary" disabled={state === 'submitting'}>
              {state === 'submitting' ? 'Adding…' : 'Add Post'}
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
