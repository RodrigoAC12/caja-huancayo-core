import React from "react";
import { useEffect, useState } from 'react'
import api from '../services/api.js'
import StatCard from '../components/StatCard.jsx'

export default function DashboardPage() {
  const [data, setData] = useState(null)
  useEffect(() => { api.get('/reportes/dashboard').then(r => setData(r.data)).catch(() => setData({ stats: {}, solicitudes_recientes: [] })) }, [])
  const s = data?.stats || {}
  return <section>
    <div className="page-head"><h1>Dashboard</h1><p>Resumen general del ecosistema del core.</p></div>
    <div className="stats-grid">
      <StatCard title="Clientes" value={s.clientes ?? '-'} />
      <StatCard title="Solicitudes" value={s.solicitudes ?? '-'} />
      <StatCard title="Aprobadas" value={s.aprobadas ?? '-'} />
      <StatCard title="Cartera pendiente" value={s.cartera_pendiente ?? '-'} />
      <StatCard title="Visitas hoy" value={s.visitas_hoy ?? '-'} />
      <StatCard title="GPS válido" value={s.visitas_gps_valido ?? '-'} />
      <StatCard title="Monto solicitado" value={`S/ ${(s.monto_solicitado ?? 0).toLocaleString('es-PE')}`} />
    </div>
    <div className="panel">
      <h2>Solicitudes recientes</h2>
      <table><thead><tr><th>Expediente</th><th>Cliente</th><th>Monto</th><th>Estado</th></tr></thead><tbody>
        {(data?.solicitudes_recientes || []).map(x => <tr key={x.numero_expediente}><td>{x.numero_expediente}</td><td>{x.cliente_nombre}</td><td>S/ {Number(x.monto_solicitado).toLocaleString('es-PE')}</td><td><span className="badge">{x.estado}</span></td></tr>)}
      </tbody></table>
    </div>
  </section>
}

