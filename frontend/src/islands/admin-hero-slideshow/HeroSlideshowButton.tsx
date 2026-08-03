import { useEffect, useState } from 'react'
import { durationSchema, MAX_DURATION_SECONDS, MIN_DURATION_SECONDS, type HeroSlide } from './schema'
import { useCrudList } from '../../lib/useCrudList'
import { getCsrfToken } from '../../lib/csrf'
import { readErrorMessage, NETWORK_ERROR_MESSAGE } from '../../lib/api'
import Modal from '../../lib/Modal'
import SlideRow from './SlideRow'
import AddSlideControl from './AddSlideControl'

const SLIDES_ENDPOINT = '/api/admin-hub/hero-slides/'
const SITE_SETTINGS_ENDPOINT = '/api/admin-hub/site-settings/'

type DoneState = 'idle' | 'saving'

/** Cycles a preview index through `count` slides on `intervalSeconds` — used
 * to crossfade the modal's live preview at whatever pace is currently typed
 * into the duration field, not just the last-saved value. */
function usePreviewIndex(count: number, intervalSeconds: number) {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    setIndex(0)
  }, [count])

  useEffect(() => {
    if (count < 2) return
    const ms = Math.max(1, intervalSeconds) * 1000
    const id = setInterval(() => setIndex((i) => (i + 1) % count), ms)
    return () => clearInterval(id)
  }, [count, intervalSeconds])

  return index
}

interface Props {
  initialDuration: number
}

export default function HeroSlideshowButton({ initialDuration }: Props) {
  const { items: slides, loadState, add, remove } = useCrudList<HeroSlide>(SLIDES_ENDPOINT)
  const [open, setOpen] = useState(false)
  const [duration, setDuration] = useState(initialDuration)
  const [durationInput, setDurationInput] = useState(String(initialDuration))
  const [durationError, setDurationError] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)
  const [doneState, setDoneState] = useState<DoneState>('idle')

  const previewSeconds = Number(durationInput) || duration
  const previewIndex = usePreviewIndex(slides.length, previewSeconds)

  function openModal() {
    setDurationInput(String(duration))
    setDurationError(null)
    setServerError(null)
    setOpen(true)
  }

  /** Escape/overlay-click and the Cancel button all funnel here — the
   * duration field is provisional until Done (same as Account Settings'
   * fields), so backing out just discards whatever was typed. Image
   * add/delete take effect immediately when clicked (like every other
   * admin list here), so there's nothing to revert for those. */
  function handleCancel() {
    setDurationInput(String(duration))
    setDurationError(null)
    setServerError(null)
    setOpen(false)
  }

  async function handleDone() {
    setServerError(null)

    const result = durationSchema.safeParse(durationInput)
    if (!result.success) {
      setDurationError(result.error.issues[0]?.message ?? 'Invalid value.')
      return
    }
    setDurationError(null)

    if (result.data === duration) {
      setOpen(false)
      return
    }

    setDoneState('saving')
    try {
      const res = await fetch(SITE_SETTINGS_ENDPOINT, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'same-origin',
        body: JSON.stringify({ hero_slide_duration_seconds: result.data }),
      })
      if (!res.ok) {
        setServerError(await readErrorMessage(res))
        setDoneState('idle')
        return
      }
      setDuration(result.data)
      setDoneState('idle')
      setOpen(false)
    } catch {
      setServerError(NETWORK_ERROR_MESSAGE)
      setDoneState('idle')
    }
  }

  return (
    <>
      <button type="button" className="cc-btn" onClick={openModal}>Hero Slideshow</button>

      <Modal open={open} onClose={handleCancel} title="Hero Slideshow" hideCloseButton>
        <div className="hero-slideshow-preview">
          {slides.map((slide, i) => (
            <div
              key={slide.id}
              className={`hero-slideshow-preview__slide${i === previewIndex ? ' is-active' : ''}`}
              style={{ backgroundImage: `url(${slide.image})` }}
            />
          ))}
          {loadState === 'loaded' && slides.length === 0 && (
            <p className="hero-slideshow-preview__empty">No images yet.</p>
          )}
        </div>

        <AddSlideControl onAdded={add} />

        {loadState === 'loading' ? (
          <p className="section__sub">Loading…</p>
        ) : slides.length === 0 ? (
          <p className="section__sub">No slideshow images yet.</p>
        ) : (
          <div className="hero-slide-list">
            {slides.map((slide) => (
              <SlideRow key={slide.id} slide={slide} onDeleted={remove} />
            ))}
          </div>
        )}

        <div className="field">
          <label htmlFor="hero-slide-duration">Slide Duration (seconds)</label>
          <input
            id="hero-slide-duration"
            type="number"
            min={MIN_DURATION_SECONDS}
            max={MAX_DURATION_SECONDS}
            autoComplete="off"
            value={durationInput}
            onChange={(e) => setDurationInput(e.target.value)}
            disabled={doneState === 'saving'}
          />
          {durationError && <p className="form-note">{durationError}</p>}
        </div>

        {serverError && <p className="form-note">{serverError}</p>}

        <div className="account-settings-footer">
          <button type="button" className="btn btn--outline" onClick={handleCancel} disabled={doneState === 'saving'}>
            Cancel
          </button>
          <button type="button" className="btn btn--primary" onClick={handleDone} disabled={doneState === 'saving'}>
            {doneState === 'saving' ? 'Saving…' : 'Done'}
          </button>
        </div>
      </Modal>
    </>
  )
}
