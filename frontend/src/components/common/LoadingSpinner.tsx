interface LoadingSpinnerProps {
  message?: string
}

export function LoadingSpinner({ message }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12" data-testid="loading-spinner">
      <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      {message && <p className="mt-4 text-sm text-gray-500">{message}</p>}
    </div>
  )
}
