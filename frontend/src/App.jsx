import React, { useState } from 'react'
import PlantIdentify from './components/PlantIdentify'
import AyurvedaChat from './components/AyurvedaChat'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function Nav({tab,setTab}){
  return (
    <div className="flex gap-2 p-2 bg-white shadow">
      {['identify','ayurveda'].map(t => (
        <button key={t} onClick={()=>setTab(t)}
          className={"px-3 py-2 rounded border "+(tab===t?'bg-black text-white':'bg-white')}>
          {t==='identify'?'Plant Identify':'Ayurveda Chat'}
        </button>
      ))}
      <div className="ml-auto text-sm text-gray-600">Backend: {API}</div>
    </div>
  )
}

export default function App(){
  const [tab,setTab] = useState('identify')
  return (
    <div className="max-w-3xl mx-auto">
      <header className="p-4">
        <h1 className="text-2xl font-bold">AyurDrishti</h1>
        <p className="text-sm text-gray-600">Live Plant ID + Ayurveda tips</p>
      </header>
      <Nav tab={tab} setTab={setTab} />
      <main className="p-4">
        {tab==='identify' ? <PlantIdentify/> : <AyurvedaChat/>}
      </main>
      <footer className="p-6 text-center text-xs text-gray-500">© {new Date().getFullYear()} AyurDrishti</footer>
    </div>
  )
}
