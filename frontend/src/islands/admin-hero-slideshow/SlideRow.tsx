import { useEditDelete } from '../../lib/useEditDelete'
import type { HeroSlide } from './schema'
import Modal from '../../lib/Modal'
import { DeleteIcon } from '../../lib/Icons'

const ENDPOINT = '/api/admin-hub/hero-slides/'

// The Home hero's main background photo — not deletable from the Admin Hub.
const PROTECTED_IMAGE_FILENAME = 'bg-image.jpg'

interface Props {
  slide: HeroSlide
  onDeleted: (id: number) => void
}

export default function SlideRow({ slide, onDeleted }: Props) {
  const { dialog, saveState, serverError, openDelete, closeDialog, remove } =
    useEditDelete<HeroSlide>(ENDPOINT, slide.id)

  async function handleDelete() {
    if (await remove()) onDeleted(slide.id)
  }

  const isProtected = slide.image.endsWith(PROTECTED_IMAGE_FILENAME)

  return (
    <div className="hero-slide-row">
      <img src={slide.image} alt="" />
      {!isProtected && (
        <button type="button" className="btn btn--primary btn--icon" onClick={openDelete} aria-label="Delete image">
          <DeleteIcon />
        </button>
      )}

      <Modal open={dialog === 'delete'} onClose={closeDialog} title="Delete Slide">
        <p className="modal__body">Delete this slideshow image? This can&apos;t be undone.</p>

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
