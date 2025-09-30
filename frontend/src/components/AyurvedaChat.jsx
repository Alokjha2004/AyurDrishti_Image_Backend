import React, { useState } from 'react'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function AyurvedaChat(){
  const [msg,setMsg]=useState('')
  const [ans,setAns]=useState(null)
  const [loading,setLoading]=useState(false)

  const send = async () => {
    if(!msg.trim()) return
    const fd = new FormData()
    fd.append('message', msg)
    setLoading(true)
    try{
      const r = await fetch(`${API}/api/ayurveda-chat`, { method:'POST', body: fd })
      const j = await r.json()
      setAns(j)
    }catch(e){ alert('Error: '+e.message) }finally{ setLoading(false) }
  }

  return (
    <div className="p-4">
      <textarea className="w-full border p-2 rounded" rows="4" placeholder="Symptoms or daily wellness question..."
        value={msg} onChange={e=>setMsg(e.target.value)} />
      <button onClick={send} disabled={loading} className="mt-2 px-4 py-2 rounded bg-indigo-600 text-white">
        {loading?'Thinking...':'Ask'}</button>

      {ans && (
        <div className="bg-white p-4 rounded shadow mt-3">
          <div className="whitespace-pre-wrap">{ans.answer}</div>
          <div className="text-xs text-gray-500 mt-2">{ans.disclaimer}</div>
        </div>
      )}
    </div>
  )
}
