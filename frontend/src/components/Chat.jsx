import React, { useState } from 'react'
import Message from './Message.jsx'

export default function Chat({ onAsk, loading, docOptions }) {
  const [question, setQuestion] = useState('')
  const [doc, setDoc] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!question.trim()) return
    onAsk(question, doc || null)
    setQuestion('')
  }

  return (
    <div className="card">
      <h3>2) Ask a question</h3>
      <form onSubmit={handleSubmit} className="row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask something about your documents..."
          disabled={loading}
        />
        <select value={doc} onChange={(e) => setDoc(e.target.value)} disabled={loading}>
          <option value="">All documents</option>
          {docOptions.map((d) => (
            <option key={d.doc_id} value={d.doc_id}>{d.filename}</option>
          ))}
        </select>
        <button type="submit" disabled={loading}>{loading ? 'Working...' : 'Ask'}</button>
      </form>
      <div className="messages">
        <Message />
      </div>
    </div>
  )
}
