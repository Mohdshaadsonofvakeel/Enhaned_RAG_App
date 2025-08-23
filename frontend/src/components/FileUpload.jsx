import React, { useRef } from 'react'

export default function FileUpload({ onUpload, loading }) {
  const ref = useRef()

  const handleChange = (e) => {
    const files = [...(e.target.files || [])]
    if (files.length) onUpload(files)
    ref.current.value = null
  }

  return (
    <div className="card">
      <h3>1) Upload documents</h3>
      <input ref={ref} type="file" multiple onChange={handleChange} disabled={loading} />
      <p className="hint">PDF, DOCX, TXT, images supported.</p>
    </div>
  )
}
