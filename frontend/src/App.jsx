import React, { useState } from 'react'
import { uploadFiles, askQuestion } from './api'
import FileUpload from './components/FileUpload.jsx'
import Chat from './components/Chat.jsx'

export default function App() {
  const [docs, setDocs] = useState([])
  const [chat, setChat] = useState([])
  const [loading, setLoading] = useState(false)

  const handleUpload = async (files) => {
    setLoading(true)
    try {
      const res = await uploadFiles(files)
      setDocs((prev) => [...prev, ...(res.items || [])])
    } catch (e) {
      alert('Upload failed: ' + (e?.message || e))
    } finally {
      setLoading(false)
    }
  }

  const handleAsk = async (question, docId = null) => {
    setLoading(true)
    try {
      const payload = { question, top_k: 5 }
      if (docId) payload.doc_id = docId
      const res = await askQuestion(payload)
      setChat((prev) => [
        ...prev,
        { role: 'user', content: question },
        { role: 'assistant', content: res.answer, sources: res.matches }
      ])
    } catch (e) {
      setChat((prev) => [...prev, { role: 'assistant', content: 'Error: ' + (e?.message || e) }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Enhanced RAG App</h1>
      </header>

      <section>
        <FileUpload onUpload={handleUpload} loading={loading} />
      </section>

      {docs.length > 0 && (
        <section className="docs">
          <h3>Uploaded documents</h3>
          <ul>
            {docs.map((d, i) => (
              <li key={i}>
                <b>{d.filename}</b> <small>({d.mime_type})</small> – chunks: {d.chunks} – <code>{d.doc_id}</code>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <Chat onAsk={handleAsk} loading={loading} docOptions={docs} />
      </section>
    </div>
  )
}
