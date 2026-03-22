import type { Asset, RobotType } from './types'

type Props = {
  asset: Pick<Asset, 'kind' | 'robotType'>
  size?: 'sm' | 'md'
}

export function AssetGlyph({ asset, size = 'md' }: Props) {
  const type = resolveGlyphType(asset)
  const pixelSize = size === 'sm' ? 18 : 22

  return (
    <span className={`asset-glyph asset-glyph--${size}`} aria-hidden="true">
      <svg viewBox="0 0 24 24" width={pixelSize} height={pixelSize} fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        {type === 'quadruped' ? (
          <>
            <path d="M5 12h8.5l2-2.5h1.8l1.4 1.5H20v3h-2.5" />
            <path d="M7 12v4" />
            <path d="M12 12v4" />
            <path d="M17 12v4" />
            <circle cx="18.7" cy="8.8" r="1.1" />
          </>
        ) : null}
        {type === 'humanoid' ? (
          <>
            <circle cx="12" cy="5.5" r="2.1" />
            <path d="M12 8.2v6.2" />
            <path d="M8.5 11.2 12 9.7l3.5 1.5" />
            <path d="M9.7 18.4 12 14.4l2.3 4" />
          </>
        ) : null}
        {type === 'drone' ? (
          <>
            <circle cx="12" cy="12" r="2.4" />
            <circle cx="6" cy="8" r="2" />
            <circle cx="18" cy="8" r="2" />
            <circle cx="6" cy="16" r="2" />
            <circle cx="18" cy="16" r="2" />
            <path d="M8 9.2 10.4 10.8" />
            <path d="M16 9.2 13.6 10.8" />
            <path d="M8 14.8 10.4 13.2" />
            <path d="M16 14.8 13.6 13.2" />
          </>
        ) : null}
        {type === 'boat' ? (
          <>
            <path d="M4 14.5h16l-2.8 3.2H7.3L4 14.5Z" />
            <path d="M10.2 14.5V8.2h3.7l1.4 2.4v3.9" />
            <path d="M5.5 19.2c1 .8 2 .8 3 0 1 .8 2 .8 3 0 1 .8 2 .8 3 0 1 .8 2 .8 3 0" />
          </>
        ) : null}
        {type === 'cargo' ? (
          <>
            <path d="M6.2 8.2 12 5l5.8 3.2v7.6L12 19l-5.8-3.2V8.2Z" />
            <path d="M6.2 8.2 12 11.5l5.8-3.3" />
            <path d="M12 11.5V19" />
          </>
        ) : null}
        {type === 'unknown' ? (
          <>
            <circle cx="12" cy="12" r="7" />
            <path d="M12 8.5v4.5" />
            <circle cx="12" cy="16.6" r="0.6" fill="currentColor" stroke="none" />
          </>
        ) : null}
      </svg>
    </span>
  )
}

export function robotTypeLabel(asset: Pick<Asset, 'kind' | 'robotType'>) {
  const type = resolveGlyphType(asset)
  switch (type) {
    case 'quadruped':
      return 'Quadruped'
    case 'humanoid':
      return 'Humanoid'
    case 'drone':
      return 'Drone'
    case 'boat':
      return 'Boat'
    case 'cargo':
      return 'Cargo'
    default:
      return asset.kind === 'robot' ? 'Robot' : 'Asset'
  }
}

function resolveGlyphType(asset: Pick<Asset, 'kind' | 'robotType'>): RobotType {
  if (asset.kind === 'boat') return 'boat'
  if (asset.kind === 'cargo') return 'cargo'
  return asset.robotType ?? 'unknown'
}
