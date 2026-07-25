import type { CSSProperties } from 'react'

interface Props {
  className?: string
  style?: CSSProperties
}

export default function Skeleton({ className = '', style }: Props) {
  return <span className={`skeleton ${className}`.trim()} style={style} aria-hidden="true" />
}
