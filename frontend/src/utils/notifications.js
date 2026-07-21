import { toast } from 'react-toastify'

export const notify = {
  success: (message) => toast.success(message),
  error: (message) => toast.error(message || 'An error occurred'),
  info: (message) => toast.info(message),
  warning: (message) => toast.warning(message),
  promise: (promise, msgs) => toast.promise(promise, msgs),
}

export const handleApiError = (error, customMessage) => {
  const message = customMessage || error?.response?.data?.error || error?.message || 'An error occurred'
  notify.error(message)
}
