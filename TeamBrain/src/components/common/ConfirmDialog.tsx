import { Modal } from './Modal'

interface ConfirmDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  danger = false,
}: ConfirmDialogProps) {
  return (
    <Modal open={open} onClose={onClose} title={title}>
      <p className="text-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>
        {message}
      </p>
      <div className="flex justify-end gap-3">
        <button
          onClick={onClose}
          className="btn-secondary"
        >
          {cancelText}
        </button>
        <button
          onClick={() => { onConfirm(); onClose() }}
          className="btn-primary"
          style={danger ? { background: 'var(--color-danger)' } : undefined}
          onMouseEnter={(e) => {
            if (danger) e.currentTarget.style.background = '#DC2626'
          }}
          onMouseLeave={(e) => {
            if (danger) e.currentTarget.style.background = 'var(--color-danger)'
          }}
        >
          {confirmText}
        </button>
      </div>
    </Modal>
  )
}
