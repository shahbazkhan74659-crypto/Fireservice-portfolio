import { useState, type ChangeEvent, type FormEvent } from 'react'
import {
  editBlogSchema,
  type BlogPost,
  type EditBlogInput,
  type EditBlogErrors,
} from './schema'
import { useEditDelete } from '../../lib/useEditDelete'
import Modal from '../../lib/Modal'
import { DeleteIcon, EditIcon } from '../../lib/Icons'

const ENDPOINT = '/api/admin-hub/blog/'

interface Props {
  post: BlogPost
  onUpdated: (post: BlogPost) => void
  onDeleted: (id: number) => void
}

function toDateInputValue(isoDateTime: string) {
  return isoDateTime ? isoDateTime.slice(0, 10) : ''
}

export default function BlogPostCard({ post, onUpdated, onDeleted }: Props) {
  const { dialog, saveState, serverError, openEdit, openDelete, closeDialog, save, remove } =
    useEditDelete<BlogPost>(ENDPOINT, post.id)
  const [title, setTitle] = useState(post.title)
  const [excerpt, setExcerpt] = useState(post.excerpt)
  const [body, setBody] = useState(post.body)
  const [metaDescription, setMetaDescription] = useState(post.meta_description)
  const [file, setFile] = useState<File | null>(null)
  const [publishedAt, setPublishedAt] = useState(toDateInputValue(post.published_at))
  const [isPublished, setIsPublished] = useState(post.is_published)
  const [errors, setErrors] = useState<EditBlogErrors>({})

  function startEdit() {
    setTitle(post.title)
    setExcerpt(post.excerpt)
    setBody(post.body)
    setMetaDescription(post.meta_description)
    setFile(null)
    setPublishedAt(toDateInputValue(post.published_at))
    setIsPublished(post.is_published)
    setErrors({})
    openEdit()
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const values: EditBlogInput = {
      title,
      excerpt,
      body,
      meta_description: metaDescription,
      image: file ?? undefined,
      published_at: publishedAt,
      is_published: isPublished,
    }
    const result = editBlogSchema.safeParse(values)
    if (!result.success) {
      const fieldErrors: EditBlogErrors = {}
      for (const issue of result.error.issues) {
        const key = issue.path[0] as keyof EditBlogInput
        if (!fieldErrors[key]) fieldErrors[key] = issue.message
      }
      setErrors(fieldErrors)
      return
    }
    setErrors({})

    const formData = new FormData()
    formData.append('title', result.data.title)
    formData.append('excerpt', result.data.excerpt)
    formData.append('body', result.data.body)
    if (result.data.meta_description) formData.append('meta_description', result.data.meta_description)
    // Only append image if a new file was chosen, mirroring ServiceCard's
    // edit — an untouched file input must not overwrite the existing photo.
    if (result.data.image) formData.append('image', result.data.image)
    formData.append('published_at', result.data.published_at)
    formData.append('is_published', result.data.is_published ? 'true' : 'false')

    const updated = await save(formData)
    if (updated) onUpdated(updated)
  }

  async function handleDelete() {
    if (await remove()) onDeleted(post.id)
  }

  return (
    <div className="blog-card">
      {post.image && (
        <div className="blog-card__img">
          <img src={post.image} alt={post.title} />
        </div>
      )}
      <div className="blog-card__body">
        <span className={`blog-status ${post.is_published ? 'blog-status--published' : 'blog-status--draft'}`}>
          {post.is_published ? 'Published' : 'Draft'}
        </span>
        <h3>{post.title}</h3>
        <p>{post.excerpt}</p>

        <div className="logo-card__admin-actions">
          <button type="button" className="btn btn--outline btn--icon" onClick={startEdit} aria-label="Edit">
            <EditIcon />
          </button>
          <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete">
            <DeleteIcon />
          </button>
        </div>
      </div>

      <Modal open={dialog === 'edit'} onClose={closeDialog} title="Edit Blog Post">
        <form onSubmit={handleSave} noValidate>
          <div className="field">
            <label htmlFor={`blog-title-${post.id}`}>Title</label>
            <input
              id={`blog-title-${post.id}`}
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.title && <p className="form-note">{errors.title}</p>}
          </div>
          <div className="field">
            <label htmlFor={`blog-excerpt-${post.id}`}>Excerpt</label>
            <textarea
              id={`blog-excerpt-${post.id}`}
              rows={3}
              value={excerpt}
              onChange={(e) => setExcerpt(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.excerpt && <p className="form-note">{errors.excerpt}</p>}
          </div>
          <div className="field">
            <label htmlFor={`blog-body-${post.id}`}>Body</label>
            <textarea
              id={`blog-body-${post.id}`}
              rows={10}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.body && <p className="form-note">{errors.body}</p>}
          </div>
          <div className="field">
            <label htmlFor={`blog-meta-description-${post.id}`}>Meta Description (SEO override, optional)</label>
            <input
              id={`blog-meta-description-${post.id}`}
              type="text"
              value={metaDescription}
              onChange={(e) => setMetaDescription(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.meta_description && <p className="form-note">{errors.meta_description}</p>}
          </div>
          <div className="field">
            <label htmlFor={`blog-image-${post.id}`}>Replace Image (optional)</label>
            <input
              id={`blog-image-${post.id}`}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={saveState === 'saving'}
            />
            {file && <p className="form-note form-note--success">Selected: {file.name}</p>}
            {errors.image && <p className="form-note">{errors.image}</p>}
          </div>
          <div className="field">
            <label htmlFor={`blog-published-at-${post.id}`}>Published Date</label>
            <input
              id={`blog-published-at-${post.id}`}
              type="date"
              value={publishedAt}
              onChange={(e) => setPublishedAt(e.target.value)}
              disabled={saveState === 'saving'}
            />
            {errors.published_at && <p className="form-note">{errors.published_at}</p>}
          </div>
          <label className="field field--checkbox">
            <input
              type="checkbox"
              checked={isPublished}
              onChange={(e) => setIsPublished(e.target.checked)}
              disabled={saveState === 'saving'}
            />
            <span>Published</span>
          </label>

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

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Blog Post">
        <p className="modal__body">Delete &quot;{post.title}&quot;? This can&apos;t be undone.</p>

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
