import React, { useState } from 'react'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function PlantIdentify(){
  const [file, setFile] = useState(null)
  const [organ, setOrgan] = useState('leaf')
  const [res, setRes] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    if(!file) return alert('Select an image')
    const fd = new FormData()
    fd.append('file', file)
    fd.append('organ', organ)
    setLoading(true)
    try{
      const r = await fetch(`${API}/api/identify`, { method:'POST', body: fd })
      const j = await r.json()
      setRes(j)
    }catch(e){
      alert('Error: '+e.message)
    }finally{ setLoading(false) }
  }

  return (
    <div className="p-4">
      <div className="mb-3">
        <input type="file" accept="image/*" onChange={e=>setFile(e.target.files[0])} />
      </div>
      <div className="mb-3">
        <select className="border p-2 rounded" value={organ} onChange={e=>setOrgan(e.target.value)}>
          <option value="leaf">Leaf</option>
          <option value="flower">Flower</option>
          <option value="fruit">Fruit</option>
          <option value="bark">Bark</option>
          <option value="habit">Habit</option>
        </select>
        <button onClick={submit} disabled={loading}
          className="ml-3 px-4 py-2 rounded bg-emerald-600 text-white">{loading?'Identifying...':'Identify'}</button>
      </div>

      {res && (
        <div className="bg-white p-4 rounded shadow">
          <div className="font-semibold text-lg">{res.scientific_name || '—'}</div>
          <div className="text-sm text-gray-600">Confidence: {res.confidence ?? '—'}</div>
          <div className="mt-2">Common names: {(res.common_names||[]).join(', ') || '—'}</div>
          {res.enriched && (
            <div className="mt-3">
              <div className="font-medium">Medicinal uses</div>
              <ul className="list-disc ml-5">{(res.enriched.medicinal_uses||[]).map((u,i)=>(<li key={i}>{u}</li>))}</ul>
              <div className="font-medium mt-2">Contraindications</div>
              <ul className="list-disc ml-5">{(res.enriched.contraindications||[]).map((u,i)=>(<li key={i}>{u}</li>))}</ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
