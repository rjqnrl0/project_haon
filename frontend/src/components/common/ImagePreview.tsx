interface ImagePreviewProps {
  src: string
  alt?: string
  onRemove?: () => void
}

export function ImagePreview({ src, alt = '미리보기', onRemove }: ImagePreviewProps) {
  return (
    <div className="relative inline-block" data-testid="image-preview">
      <img src={src} alt={alt} className="max-w-full rounded-lg shadow-sm" />
      {onRemove && (
        <button
          onClick={onRemove}
          className="absolute top-2 right-2 bg-black/50 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-black/70"
          data-testid="image-preview-remove-button"
        >
          &times;
        </button>
      )}
    </div>
  )
}
